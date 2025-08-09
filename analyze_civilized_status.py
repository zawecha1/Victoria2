#!/usr/bin/env python3
"""
分析当前文明化状态
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from victoria2_main_modifier import Victoria2Modifier

def analyze_civilized_status():
    """分析当前文明化状态"""
    print("🔍 分析当前文明化状态...")
    
    try:
        modifier = Victoria2Modifier("autosave.v2")
        
        # 查找所有国家块
        country_blocks = modifier.find_blocks_by_function_type('countries')
        print(f"📊 找到 {len(country_blocks)} 个国家块")
        
        # 统计文明化状态
        civilized_stats = {"yes": 0, "no": 0, "未设置": 0, "其他": 0}
        china_status = None
        
        sample_countries = []
        
        for block in country_blocks:
            import re
            civilized_match = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', block.content)
            
            if civilized_match:
                status = civilized_match.group(1).strip('"')
                if status in civilized_stats:
                    civilized_stats[status] += 1
                else:
                    civilized_stats["其他"] += 1
                    
                # 记录中国的状态
                if block.name == "CHI":
                    china_status = status
                    
                # 收集前10个国家作为样本
                if len(sample_countries) < 10:
                    sample_countries.append((block.name, status))
            else:
                civilized_stats["未设置"] += 1
                if len(sample_countries) < 10:
                    sample_countries.append((block.name, "未设置"))
        
        print(f"\n📊 文明化状态统计:")
        for status, count in civilized_stats.items():
            if count > 0:
                print(f"  {status}: {count} 个国家")
        
        if china_status:
            print(f"\n🇨🇳 中国(CHI)状态: civilized={china_status}")
        
        print(f"\n📋 前10个国家样本:")
        for name, status in sample_countries:
            print(f"  {name}: {status}")
        
        # 如果都是no，尝试修改为yes
        if civilized_stats["no"] > civilized_stats["yes"]:
            print(f"\n🔧 大部分国家是'no'，尝试修改为'yes'进行测试...")
            
            # 先修改一个国家作为测试
            test_block = country_blocks[1] if len(country_blocks) > 1 else None  # 跳过第一个，可能是REB
            if test_block and test_block.name != "CHI":
                print(f"🧪 测试修改 {test_block.name} 为 civilized='yes'")
                
                modifications = {"civilized": '"yes"'}
                if modifier.modify_block_content_safely(test_block, modifications):
                    print(f"✅ {test_block.name} 修改成功")
                    
                    # 保存测试文件
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%H%M%S")
                    test_file = f"autosave_civilized_test_{timestamp}.v2"
                    modifier.save_file(test_file)
                    print(f"📁 测试文件保存为: {test_file}")
                    return True
                else:
                    print(f"❌ {test_block.name} 修改失败")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    analyze_civilized_status()
