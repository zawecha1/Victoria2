#!/usr/bin/env python3
"""
快速测试修复后的国家块分类
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from victoria2_main_modifier import Victoria2Modifier

def test_classification_fix():
    """测试修复后的分类方法"""
    print("🔍 测试修复后的国家块分类")
    print("="*50)
    
    # 创建修改器实例
    modifier = Victoria2Modifier()
    
    # 测试各种国家代码
    test_cases = [
        'CHI', 'ENG', 'FRA', 'GER', 'RUS', 'AUS', 'USA',  # 3字母
        'US', 'UK', 'CN', 'JP', 'IN', 'FR', 'IT',         # 2字母
        'CHIN', 'TEST', 'ab', 'A', '123'                   # 其他情况
    ]
    
    for name in test_cases:
        # 创建模拟块
        class MockBlock:
            def __init__(self, name, content=""):
                self.name = name
                self.content = content
        
        mock_block = MockBlock(name, "civilized=yes primary_culture=test")
        classification = modifier._classify_block_type(mock_block)
        
        # 检查是否符合新的国家模式
        import re
        matches_new_pattern = bool(re.match(r'^[A-Z]{2,3}$', name))
        
        print(f"  {name:4}: 分类={classification:8}, 符合国家模式={matches_new_pattern}")

def test_actual_file():
    """测试实际文件中的国家块查找"""
    print(f"\n🔍 测试实际文件中的国家块查找")
    print("="*50)
    
    try:
        modifier = Victoria2Modifier("autosave.v2")
        
        # 使用修复后的方法查找国家块
        country_blocks = modifier.find_blocks_by_function_type('countries')
        
        print(f"找到的国家块数量: {len(country_blocks)}")
        
        if country_blocks:
            print(f"前10个国家块:")
            for i, block in enumerate(country_blocks[:10]):
                import re
                civilized_match = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', block.content)
                current_civilized = civilized_match.group(1) if civilized_match else "未找到"
                print(f"  {i+1:2}. {block.name:4}: civilized={current_civilized}")
        
        return len(country_blocks)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return 0

if __name__ == "__main__":
    test_classification_fix()
    country_count = test_actual_file()
    
    if country_count > 0:
        print(f"\n✅ 修复成功！找到 {country_count} 个国家块")
        print("现在可以重新尝试文明化状态修改了")
    else:
        print(f"\n❌ 修复失败，仍未找到国家块")
