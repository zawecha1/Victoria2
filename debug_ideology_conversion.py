#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试意识形态转换过程
"""

import re

def debug_ideology_conversion():
    """调试意识形态转换的详细过程"""
    
    # 测试数据（从实际省份复制）
    test_data = """
    1=17.13712
    2=8.49777
    3=6.99579
    4=22.85031
    5=12.99979
    6=18.52100
    7=12.99814
    """
    
    # 当前映射规则
    ideology_mapping = {
        1: 3,  # Reactionary(1) -> Conservative(3)
        2: 5,  # Fascist(2) -> Liberal(5) - 测试ID 5是Liberal
        4: 3,  # Socialist(4) -> Conservative(3)  
        6: 5,  # Anarcho-Liberal(6) -> Liberal(5) - 测试ID 5是Liberal
        7: 3   # Communist(7) -> Conservative(3)
    }
    
    print("🔍 调试意识形态转换过程")
    print("==================================================")
    
    # 解析原始数据
    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', test_data)
    ideology_dist = {}
    
    for id_str, value_str in ideology_pairs:
        ideology_dist[int(id_str)] = float(value_str)
    
    print("📊 原始意识形态分布:")
    for id, value in sorted(ideology_dist.items()):
        print(f"  ID {id}: {value:.5f}")
    
    print("\n🔄 映射规则:")
    for old_id, new_id in ideology_mapping.items():
        print(f"  ID {old_id} -> ID {new_id}")
    
    print("\n🚀 执行转换:")
    total_transferred = 0.0
    transferred_to_liberal = 0.0
    transferred_to_conservative = 0.0
    
    for old_id, new_id in ideology_mapping.items():
        if old_id in ideology_dist:
            value = ideology_dist[old_id]
            print(f"  处理 ID {old_id}: {value:.5f} -> ID {new_id}")
            total_transferred += value
            
            if new_id == 5:  # Liberal = ID 5 (测试中)
                transferred_to_liberal += value
                print(f"    累计转换到Liberal: {transferred_to_liberal:.5f}")
            elif new_id == 3:  # Conservative = ID 3
                transferred_to_conservative += value
                print(f"    累计转换到Conservative: {transferred_to_conservative:.5f}")
            
            # 将原意识形态设为0
            ideology_dist[old_id] = 0.0
    
    print(f"\n📈 转换统计:")
    print(f"  总转换量: {total_transferred:.5f}")
    print(f"  转换到Liberal(5): {transferred_to_liberal:.5f}")
    print(f"  转换到Conservative(3): {transferred_to_conservative:.5f}")
    
    # 应用转换结果
    if transferred_to_liberal > 0:
        ideology_dist[5] = ideology_dist.get(5, 0.0) + transferred_to_liberal
        print(f"  ID 5最终值: {ideology_dist[5]:.5f}")
    
    if transferred_to_conservative > 0:
        ideology_dist[3] = ideology_dist.get(3, 0.0) + transferred_to_conservative
        print(f"  ID 3最终值: {ideology_dist[3]:.5f}")
    
    print("\n📊 最终意识形态分布:")
    total = 0
    for id, value in sorted(ideology_dist.items()):
        if value > 0:
            print(f"  ID {id}: {value:.5f}")
            total += value
    print(f"  总计: {total:.5f}")

if __name__ == "__main__":
    debug_ideology_conversion()
