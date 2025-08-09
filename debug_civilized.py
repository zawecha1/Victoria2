#!/usr/bin/env python3
"""
检查文明化状态修改失败的原因
"""

import re
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bracket_parser import Victoria2BracketParser
from victoria2_main_modifier import Victoria2Modifier

def debug_civilized_modification():
    """调试文明化状态修改问题"""
    print("🔍 调试文明化状态修改问题")
    print("="*60)
    
    try:
        # 初始化修改器
        modifier = Victoria2Modifier("autosave.v2", debug_mode=True)
        
        print(f"✅ 文件加载成功，大小: {len(modifier.content):,} 字符")
        
        # 查找所有可能的国家块
        print(f"\n🔍 查找所有可能的国家块...")
        
        all_blocks = []
        def collect_blocks(block):
            all_blocks.append(block)
            if hasattr(block, 'children') and block.children:
                for child in block.children:
                    collect_blocks(child)
        
        if modifier.structure:
            collect_blocks(modifier.structure)
            print(f"总块数: {len(all_blocks)}")
        else:
            print("❌ 解析结构失败")
            return
        
        # 分析块名称模式
        block_name_patterns = {}
        civilized_blocks = []
        
        for block in all_blocks:
            name = block.name if block.name else "无名"
            
            # 分类块名称
            if re.match(r'^[A-Z]{2,4}$', name):  # 2-4个大写字母
                pattern = "国家标签候选"
            elif re.match(r'^\d+$', name):
                pattern = "数字块"
            elif re.match(r'^[a-z_]+$', name):
                pattern = "小写标识符"
            else:
                pattern = "其他"
            
            if pattern not in block_name_patterns:
                block_name_patterns[pattern] = []
            block_name_patterns[pattern].append(name)
            
            # 检查是否包含civilized字段
            if 'civilized' in block.content:
                civilized_blocks.append(block)
        
        print(f"\n📊 块名称模式分析:")
        for pattern, names in block_name_patterns.items():
            unique_names = list(set(names))
            print(f"  {pattern}: {len(names)} 个 (去重: {len(unique_names)})")
            if pattern == "国家标签候选" and len(unique_names) <= 20:
                print(f"    示例: {', '.join(unique_names[:10])}")
        
        print(f"\n🏛️ 包含civilized字段的块:")
        print(f"  总数: {len(civilized_blocks)}")
        
        # 分析这些块的详细信息
        country_like_blocks = []
        for block in civilized_blocks:
            name = block.name if block.name else "无名"
            
            # 检查国家指标
            country_indicators = [
                'primary_culture', 'capital', 'technology', 'ruling_party',
                'government', 'plurality', 'civilized', 'badboy'
            ]
            indicator_count = sum(1 for indicator in country_indicators 
                                if indicator in block.content)
            
            # 查找当前的civilized值
            civilized_match = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', block.content)
            current_civilized = civilized_match.group(1) if civilized_match else "未找到"
            
            if indicator_count >= 2:  # 符合国家块的条件
                country_like_blocks.append({
                    'name': name,
                    'indicators': indicator_count,
                    'civilized': current_civilized,
                    'level': block.level
                })
                
                print(f"  ✅ {name}: civilized={current_civilized}, 指标数={indicator_count}, 层级={block.level}")
            else:
                print(f"  ⚠️ {name}: civilized={current_civilized}, 指标数={indicator_count} (可能不是国家块)")
        
        print(f"\n📊 符合条件的国家块: {len(country_like_blocks)}")
        
        # 检查当前的find_blocks_by_function_type方法的结果
        print(f"\n🔍 当前find_blocks_by_function_type('countries')结果:")
        country_blocks = modifier.find_blocks_by_function_type('countries')
        print(f"  找到的块数: {len(country_blocks)}")
        
        if country_blocks:
            print(f"  前5个块的详细信息:")
            for i, block in enumerate(country_blocks[:5]):
                civilized_match = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', block.content)
                current_civilized = civilized_match.group(1) if civilized_match else "未找到"
                print(f"    {i+1}. {block.name}: civilized={current_civilized}")
        
        # 比较差异
        found_names = {block.name for block in country_blocks}
        expected_names = {item['name'] for item in country_like_blocks}
        
        missing = expected_names - found_names
        if missing:
            print(f"\n❌ 未被find_blocks_by_function_type找到的国家块:")
            for name in sorted(missing):
                print(f"    {name}")
                
        # 检查_classify_block_type的分类结果
        print(f"\n🔍 _classify_block_type分类测试:")
        test_names = ['CHI', 'ENG', 'FR', 'USA', 'RUS', 'GER', 'AUS']
        for name in test_names:
            # 创建一个模拟的块来测试
            class MockBlock:
                def __init__(self, name, content=""):
                    self.name = name
                    self.content = content
            
            mock_block = MockBlock(name, "civilized=yes primary_culture=test")
            classification = modifier._classify_block_type(mock_block)
            matches_pattern = bool(re.match(r'^[A-Z]{3}$', name))
            print(f"    {name}: 分类={classification}, 匹配3字母模式={matches_pattern}")
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_civilized_modification()
