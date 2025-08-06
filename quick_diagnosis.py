#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速诊断 - 直接测试修改方法
"""

import re

def quick_diagnosis():
    """快速诊断修改方法问题"""
    
    print("⚡ 快速诊断修改方法")
    print("=" * 40)
    
    # 模拟真实的ideology内容
    sample_ideology_content = '\n1=8.25323\n2=4.54782\n3=40.19861\n4=18.91043\n5=1.24637\n6=25.59711\n7=1.24637\n\t\t'
    
    print("原始内容:")
    print(repr(sample_ideology_content))
    
    # 模拟_modify_ideology_distribution方法的逻辑
    # 解析现有的意识形态分布
    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', sample_ideology_content)
    ideology_dist = {}
    
    # 解析所有现有的意识形态数据
    for id_str, value_str in ideology_pairs:
        ideology_dist[int(id_str)] = float(value_str)
    
    print(f"解析结果: {ideology_dist}")
    
    # 应用转换规则
    ideology_mapping = {1: 3, 2: 6, 4: 3, 5: 6, 7: 3}
    
    transferred_to_liberal = 0.0
    transferred_to_conservative = 0.0
    
    for old_id, new_id in ideology_mapping.items():
        if old_id in ideology_dist and ideology_dist[old_id] > 0:
            value = ideology_dist[old_id]
            print(f"  转换: {old_id} -> {new_id}, 值: {value}")
            
            if new_id == 6:  # Liberal
                transferred_to_liberal += value
            elif new_id == 3:  # Conservative  
                transferred_to_conservative += value
            
            ideology_dist[old_id] = 0.0
    
    # 更新目标意识形态的值
    if transferred_to_liberal > 0:
        ideology_dist[6] = ideology_dist.get(6, 0) + transferred_to_liberal
        print(f"  Liberal(6) 增加: {transferred_to_liberal}, 总值: {ideology_dist[6]}")
    
    if transferred_to_conservative > 0:
        ideology_dist[3] = ideology_dist.get(3, 0) + transferred_to_conservative
        print(f"  Conservative(3) 增加: {transferred_to_conservative}, 总值: {ideology_dist[3]}")
    
    print(f"转换后分布: {ideology_dist}")
    
    # 生成新的内容
    # 确保包含所有7个意识形态ID，按顺序
    new_content_lines = []
    for ideology_id in range(1, 8):
        value = ideology_dist.get(ideology_id, 0.0)
        formatted_value = f"{value:.5f}"
        new_content_lines.append(f"{ideology_id}={formatted_value}")
    
    # 使用适当的缩进格式
    new_ideology_content = '\n\t\t\t'.join(new_content_lines)
    
    print(f"新内容:")
    print(repr(new_ideology_content))
    
    # 检查是否有实际改变
    if new_ideology_content != sample_ideology_content:
        print("✅ 内容已改变")
    else:
        print("❌ 内容未改变")
    
    # 测试替换
    sample_full_block = """ideology=
                {
1=8.25323
2=4.54782
3=40.19861
4=18.91043
5=1.24637
6=25.59711
7=1.24637
                }"""
    
    print(f"\n🧪 测试替换:")
    print(f"原始完整块:")
    print(repr(sample_full_block))
    
    # 提取内容部分进行替换
    inner_match = re.search(r'ideology=\s*\{([^}]*)\}', sample_full_block, re.DOTALL)
    if inner_match:
        inner_content = inner_match.group(1)
        print(f"\n提取的内容:")
        print(repr(inner_content))
        
        # 替换内容
        new_full_block = sample_full_block.replace(inner_content, f'\n\t\t\t{new_ideology_content}\n\t\t\t')
        
        print(f"\n替换后:")
        print(repr(new_full_block))
        
        if new_full_block != sample_full_block:
            print("✅ 替换成功")
        else:
            print("❌ 替换失败")

if __name__ == "__main__":
    quick_diagnosis()
