#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试意识形态转换逻辑
"""

import re

def test_ideology_conversion():
    """直接测试意识形态转换"""
    
    # 模拟的意识形态内容（来自真实数据）
    test_content = """1=8.25323
2=4.54782
3=40.19861
4=18.91043
5=1.24637
6=25.59711
7=1.24637"""
    
    print("🧪 测试意识形态转换逻辑")
    print("原始内容:")
    print(test_content)
    print()
    
    # 解析现有的意识形态分布
    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', test_content)
    ideology_dist = {}
    
    for id_str, value_str in ideology_pairs:
        ideology_dist[int(id_str)] = float(value_str)
    
    print(f"解析结果: {ideology_dist}")
    
    # 意识形态映射
    ideology_mapping = {
        1: 3,  # Reactionary(1) -> Conservative(3)
        2: 6,  # Fascist(2) -> Liberal(6)
        4: 3,  # Socialist(4) -> Conservative(3)  
        5: 6,  # Anarcho-Liberal(5) -> Liberal(6)
        7: 3   # Communist(7) -> Conservative(3)
    }
    
    # 应用转换规则
    transferred_to_liberal = 0.0
    transferred_to_conservative = 0.0
    changes_made = False
    
    print("\n转换过程:")
    for old_id, new_id in ideology_mapping.items():
        if old_id in ideology_dist and ideology_dist[old_id] > 0:
            value = ideology_dist[old_id]
            print(f"  转换: {old_id} -> {new_id}, 值: {value}")
            
            if new_id == 6:  # Liberal
                transferred_to_liberal += value
            elif new_id == 3:  # Conservative
                transferred_to_conservative += value
            
            # 将原意识形态设为0
            ideology_dist[old_id] = 0.0
            changes_made = True
    
    # 增加目标意识形态的值
    if transferred_to_liberal > 0:
        ideology_dist[6] += transferred_to_liberal
        print(f"  Liberal(6) 增加: {transferred_to_liberal}, 总值: {ideology_dist[6]}")
    
    if transferred_to_conservative > 0:
        ideology_dist[3] += transferred_to_conservative
        print(f"  Conservative(3) 增加: {transferred_to_conservative}, 总值: {ideology_dist[3]}")
    
    print(f"\n转换后分布: {ideology_dist}")
    
    # 重新构建内容
    new_lines = []
    for ideology_id in sorted(ideology_dist.keys()):
        value = ideology_dist[ideology_id]
        new_lines.append(f'{ideology_id}={value:.5f}')
    
    formatted_content = '\n\t\t\t'.join(new_lines)
    
    print(f"\n格式化输出:")
    print(formatted_content)
    
    # 验证总和
    total = sum(ideology_dist.values())
    print(f"\n总和验证: {total:.5f}")
    
    # 检查是否还有旧意识形态
    old_remaining = sum(ideology_dist.get(old_id, 0) for old_id in [1, 2, 4, 5, 7])
    print(f"剩余旧意识形态: {old_remaining:.5f}")
    
    if old_remaining == 0:
        print("✅ 所有旧意识形态已清零")
    else:
        print("❌ 仍有旧意识形态残留")
    
    return formatted_content

if __name__ == "__main__":
    test_ideology_conversion()
