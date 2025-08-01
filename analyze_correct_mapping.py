#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新确定Victoria II正确的意识形态ID映射
"""

def analyze_game_results():
    """基于游戏实际显示结果分析正确映射"""
    
    print("Victoria II 意识形态ID映射分析")
    print("="*50)
    
    print("🎮 游戏实际显示结果:")
    print("第一次修改后显示: Reactionary + Fascist")
    print("  我们转换到: ID 1 + ID 2")
    print("  所以: ID 1 = Reactionary, ID 2 = Fascist")
    print()
    
    print("第二次修改后显示: Conservative + Socialist") 
    print("  我们转换到: ID 3 + ID 4")
    print("  所以: ID 3 = Conservative, ID 4 = Socialist")
    print()
    
    print("🔍 推断的正确映射:")
    mapping_guess = {
        1: "Reactionary",      # 反动主义
        2: "Fascist",         # 法西斯主义
        3: "Conservative",    # 保守主义 ✓
        4: "Socialist",       # 社会主义 (不是Liberal!)
        5: "?",              # 未知
        6: "?",              # 未知  
        7: "?"               # 未知
    }
    
    for id_val, name in mapping_guess.items():
        print(f"  ID {id_val}: {name}")
    
    print()
    print("💡 问题发现:")
    print("ID 4 不是Liberal，而是Socialist!")
    print("我们需要找到Liberal对应的真实ID")
    
    return mapping_guess

def suggest_liberal_id():
    """推测Liberal的正确ID"""
    
    print("\n" + "="*50)
    print("寻找Liberal的正确ID")
    print("="*50)
    
    print("已知:")
    print("ID 1 = Reactionary")
    print("ID 2 = Fascist") 
    print("ID 3 = Conservative")
    print("ID 4 = Socialist")
    print()
    
    print("剩余可能的ID: 5, 6, 7")
    print("其中一个应该是Liberal")
    print()
    
    print("📊 分析原始数据中各ID的分布:")
    original = {
        1: 17.14,  # Reactionary
        2: 8.50,   # Fascist
        3: 6.99,   # Conservative  
        4: 22.85,  # Socialist (原以为是Liberal)
        5: 13.00,  # ? (原以为是Anarcho-Liberal)
        6: 18.52,  # ? (原以为是Communist)
        7: 13.00   # ? (原以为是Communist)
    }
    
    for id_val, percent in original.items():
        print(f"ID {id_val}: {percent:.2f}%")
    
    print()
    print("🤔 推测:")
    print("在Victoria II中，Liberal通常是主要的政治倾向之一")
    print("ID 4 (22.85%) 最高，如果它是Socialist而不是Liberal")
    print("那么Liberal可能是 ID 5, 6, 或 7 中的一个")
    
    return original

def generate_test_mapping():
    """生成测试用的新映射"""
    
    print("\n" + "="*50)
    print("生成新的测试映射")
    print("="*50)
    
    print("方案A: 假设 Liberal = ID 5")
    mapping_a = {
        1: 3,  # Reactionary(1) -> Conservative(3)
        2: 5,  # Fascist(2) -> Liberal(5)  
        4: 3,  # Socialist(4) -> Conservative(3)
        6: 3,  # ?(6) -> Conservative(3)
        7: 5   # ?(7) -> Liberal(5)
    }
    
    print("mapping_a =", mapping_a)
    print()
    
    print("方案B: 假设 Liberal = ID 6") 
    mapping_b = {
        1: 3,  # Reactionary(1) -> Conservative(3)
        2: 6,  # Fascist(2) -> Liberal(6)
        4: 3,  # Socialist(4) -> Conservative(3) 
        5: 3,  # ?(5) -> Conservative(3)
        7: 6   # ?(7) -> Liberal(6)
    }
    
    print("mapping_b =", mapping_b)
    print()
    
    print("方案C: 假设 Liberal = ID 7")
    mapping_c = {
        1: 3,  # Reactionary(1) -> Conservative(3)
        2: 7,  # Fascist(2) -> Liberal(7)
        4: 3,  # Socialist(4) -> Conservative(3)
        5: 3,  # ?(5) -> Conservative(3)
        6: 3   # ?(6) -> Conservative(3)
    }
    
    print("mapping_c =", mapping_c)
    
    return [mapping_a, mapping_b, mapping_c]

def main():
    game_mapping = analyze_game_results()
    original_data = suggest_liberal_id()
    test_mappings = generate_test_mapping()
    
    print(f"\n{'='*50}")
    print("建议: 先测试方案A (Liberal = ID 5)")
    print("="*50)

if __name__ == "__main__":
    main()
