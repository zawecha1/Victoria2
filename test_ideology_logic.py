#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查意识形态转换逻辑
"""

def test_ideology_conversion():
    """测试意识形态转换逻辑"""
    
    # 意识形态映射规则（和修改器中相同）
    ideology_mapping = {
        # Reactionary(3) -> Liberal(2)
        3: 2,
        # Anarcho-Liberal(4) -> Liberal(2)  
        4: 2,
        # Socialist(5) -> Conservative(1)
        5: 1,
        # Communist(6) -> Conservative(1)
        6: 1,
        # Fascist(7) -> Conservative(1)
        7: 1
    }
    
    # 模拟原始意识形态分布（从备份文件中看到的真实数据）
    original_ideology_dist = {
        1: 17.13712,  # Conservative
        2: 8.49777,   # Liberal  
        3: 6.99579,   # Reactionary
        4: 22.85031,  # Anarcho-Liberal
        5: 12.99979,  # Socialist
        6: 18.52100,  # Communist
        7: 12.99814   # Fascist
    }
    
    print("原始意识形态分布:")
    ideology_names = {
        1: "Conservative", 2: "Liberal", 3: "Reactionary", 
        4: "Anarcho-Liberal", 5: "Socialist", 6: "Communist", 7: "Fascist"
    }
    
    for id_val, value in original_ideology_dist.items():
        print(f"  {id_val}={value:.5f} ({ideology_names[id_val]})")
    
    print(f"\n总计: {sum(original_ideology_dist.values()):.5f}")
    
    # 应用转换规则
    new_ideology_dist = original_ideology_dist.copy()
    transferred_to_liberal = 0.0
    transferred_to_conservative = 0.0
    
    for old_id, new_id in ideology_mapping.items():
        if old_id in new_ideology_dist:
            value = new_ideology_dist[old_id]
            
            if new_id == 2:  # Liberal
                transferred_to_liberal += value
            elif new_id == 1:  # Conservative
                transferred_to_conservative += value
            
            # 将原意识形态设为0
            new_ideology_dist[old_id] = 0.0
    
    # 增加目标意识形态的值
    if transferred_to_liberal > 0:
        new_ideology_dist[2] = new_ideology_dist.get(2, 0.0) + transferred_to_liberal
    
    if transferred_to_conservative > 0:
        new_ideology_dist[1] = new_ideology_dist.get(1, 0.0) + transferred_to_conservative
    
    print("\n转换后意识形态分布:")
    for id_val, value in new_ideology_dist.items():
        print(f"  {id_val}={value:.5f} ({ideology_names[id_val]})")
    
    print(f"\n总计: {sum(new_ideology_dist.values()):.5f}")
    
    print("\n转换详情:")
    print(f"转移到Liberal(2): {transferred_to_liberal:.5f}")
    print(f"  来自Reactionary(3): {original_ideology_dist[3]:.5f}")
    print(f"  来自Anarcho-Liberal(4): {original_ideology_dist[4]:.5f}")
    
    print(f"转移到Conservative(1): {transferred_to_conservative:.5f}")
    print(f"  来自Socialist(5): {original_ideology_dist[5]:.5f}")
    print(f"  来自Communist(6): {original_ideology_dist[6]:.5f}")
    print(f"  来自Fascist(7): {original_ideology_dist[7]:.5f}")

if __name__ == "__main__":
    test_ideology_conversion()
