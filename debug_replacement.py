#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import sys
import re

# 强制重新加载模块
if 'victoria2_main_modifier' in sys.modules:
    importlib.reload(sys.modules['victoria2_main_modifier'])

from victoria2_main_modifier import Victoria2Modifier

def debug_replacement_issue():
    """调试替换问题"""
    
    print("🔧 调试替换逻辑问题")
    print("="*60)
    
    # 模拟一个包含意识形态的人口块
    sample_pop_block = """farmers=
{
size=1000
culture=beifaren
religion=mahayana
money=15.42000
literacy=0.01200
militancy=0.00000
consciousness=10.50000
everyday_needs=0.98560
luxury_needs=0.75000
ideology=
        {
1=9.90045
2=5.42841
3=33.95660
4=14.95966
5=1.48831
6=32.77817
7=1.48831
        }
issues=
        {
trade_policy=2
economic_policy=1
religious_policy=0
citizenship_policy=2
war_policy=1
        }
}"""
    
    print("📋 原始人口块:")
    print(sample_pop_block)
    
    # 创建修改器
    modifier = Victoria2Modifier()
    modifier.debug_mode = True
    
    print(f"\n🔄 执行 _modify_single_population_structured...")
    result = modifier._modify_single_population_structured(sample_pop_block)
    
    print(f"\n✅ 修改后的人口块:")
    print(result)
    
    # 检查结果中的意识形态部分
    ideology_pattern = r'ideology=\s*\{([^}]*)\}'
    ideology_match = re.search(ideology_pattern, result, re.DOTALL)
    
    if ideology_match:
        ideology_content = ideology_match.group(1)
        print(f"\n🎭 提取的意识形态内容:")
        print(ideology_content)
        
        # 解析意识形态数据
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
        ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
        
        print(f"\n📊 意识形态分析:")
        for ideology_id in sorted(ideology_dist.keys()):
            value = ideology_dist[ideology_id]
            status = "❌" if ideology_id in [1, 2, 4, 5, 7] and value > 0 else "✅"
            print(f"{status} 意识形态 {ideology_id}: {value:.5f}%")
    else:
        print("❌ 无法找到意识形态块！")

if __name__ == "__main__":
    debug_replacement_issue()
