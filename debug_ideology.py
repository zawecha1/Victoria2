#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import sys

# 强制重新加载模块
if 'victoria2_main_modifier' in sys.modules:
    importlib.reload(sys.modules['victoria2_main_modifier'])

from victoria2_main_modifier import Victoria2Modifier

def debug_ideology_issue():
    """调试意识形态修改问题"""
    
    print("🐛 调试意识形态修改问题")
    print("="*60)
    
    # 创建修改器实例
    modifier = Victoria2Modifier()
    modifier.debug_mode = True
    
    # 测试您提供的具体数据
    failing_ideology_content = """1=9.90045
2=5.42841
3=33.95660
4=14.95966
5=1.48831
6=32.77817
7=1.48831"""
    
    print("📊 问题数据 (修改后仍然所有值都非零):")
    print(failing_ideology_content)
    
    # 测试意识形态转换函数
    print(f"\n🔄 直接测试 _modify_ideology_distribution 函数...")
    result = modifier._modify_ideology_distribution(failing_ideology_content)
    
    print(f"\n✅ 函数返回结果:")
    print(result)
    
    # 解析结果验证
    import re
    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', result)
    new_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
    
    print(f"\n🔍 验证结果:")
    for ideology_id in [1, 2, 4, 5, 7]:
        value = new_dist.get(ideology_id, 0)
        if value > 0:
            print(f"❌ 意识形态 {ideology_id} 应该为0，但是值为 {value}")
        else:
            print(f"✅ 意识形态 {ideology_id} 正确设为0")
    
    print(f"\n📋 最终结果:")
    print(f"Conservative(3): {new_dist.get(3, 0):.5f}%")
    print(f"Liberal(6): {new_dist.get(6, 0):.5f}%")
    
    # 测试实际的存档文件修改
    print(f"\n🎮 测试实际存档修改...")
    modifier.load_file('China1841_12_17.v2')
    
    # 只处理一个省份进行测试
    chinese_provinces = modifier.find_chinese_provinces_structured()
    if chinese_provinces:
        print(f"找到 {len(chinese_provinces)} 个中国省份")
        test_province = chinese_provinces[0]
        print(f"测试第一个省份...")
        
        # 手动调用修改函数
        modifier._modify_province_populations_structured(test_province)
        print(f"意识形态修改计数: {modifier.ideology_changes}")

if __name__ == "__main__":
    debug_ideology_issue()
