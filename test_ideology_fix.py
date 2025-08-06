#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试意识形态修改的简单脚本
"""

import re

def test_ideology_modification():
    """测试意识形态修改逻辑"""
    
    # 模拟的意识形态数据
    test_ideology_content = """1=0.25000
2=0.15000
3=0.10000
4=0.20000
5=0.05000
6=0.15000
7=0.10000"""
    
    print("测试意识形态修改逻辑")
    print("="*50)
    print("原始意识形态分布:")
    print(test_ideology_content)
    
    # 解析原始数据
    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', test_ideology_content)
    ideology_dist = {}
    for id_str, value_str in ideology_pairs:
        ideology_dist[int(id_str)] = float(value_str)
    
    print(f"\n解析结果: {ideology_dist}")
    
    # 应用转换规则
    ideology_mapping = {
        1: 3,  # Reactionary(1) -> Conservative(3)
        2: 6,  # Fascist(2) -> Liberal(6)
        4: 3,  # Socialist(4) -> Conservative(3)  
        5: 6,  # Anarcho-Liberal(5) -> Liberal(6)
        7: 3   # Communist(7) -> Conservative(3)
    }
    
    transferred_to_liberal = 0.0
    transferred_to_conservative = 0.0
    
    for old_id, new_id in ideology_mapping.items():
        if old_id in ideology_dist and ideology_dist[old_id] > 0:
            value = ideology_dist[old_id]
            print(f"转换: {old_id} -> {new_id}, 值: {value}")
            
            if new_id == 6:  # Liberal
                transferred_to_liberal += value
            elif new_id == 3:  # Conservative
                transferred_to_conservative += value
            
            # 将原意识形态设为0
            ideology_dist[old_id] = 0.0
    
    # 确保目标意识形态存在
    if 6 not in ideology_dist:
        ideology_dist[6] = 0.0
    if 3 not in ideology_dist:
        ideology_dist[3] = 0.0
    
    # 增加目标意识形态的值
    if transferred_to_liberal > 0:
        ideology_dist[6] += transferred_to_liberal
        print(f"Liberal(6) 最终值: {ideology_dist[6]}")
    
    if transferred_to_conservative > 0:
        ideology_dist[3] += transferred_to_conservative
        print(f"Conservative(3) 最终值: {ideology_dist[3]}")
    
    print(f"\n修改后的意识形态分布: {ideology_dist}")
    
    # 构建输出格式
    new_lines = []
    for ideology_id in sorted(ideology_dist.keys()):
        value = ideology_dist[ideology_id]
        new_lines.append(f'{ideology_id}={value:.5f}')
    
    formatted_content = '\n\t\t\t'.join(new_lines)
    
    print(f"\n格式化输出:")
    print(formatted_content)
    
    # 验证总和
    total = sum(ideology_dist.values())
    print(f"\n总和验证: {total:.5f} (应该约等于1.0)")

if __name__ == "__main__":
    test_ideology_modification()
