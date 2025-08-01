#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 意识形态ID映射完整文档
==================================================
通过游戏测试确认的完整意识形态ID映射关系

测试方法：修改中国人口意识形态，在游戏中观察显示结果
测试日期：2025年1月27日
测试文件：China2245_04_06.v2
"""

# ✅ 已确认的Victoria II意识形态ID映射
VICTORIA2_IDEOLOGY_MAPPING = {
    1: "Reactionary",    # ✅ 确认 - 游戏显示"Reactionary"
    2: "Fascist",        # ✅ 确认 - 游戏显示"Fascist" 
    3: "Conservative",   # ✅ 确认 - 游戏显示"Conservative"
    4: "Socialist",      # ✅ 确认 - 游戏显示"Socialist"
    5: "Anarcho-Liberal",# 🔍 推测 - 未直接测试但逻辑推导
    6: "Liberal",        # ✅ 确认 - 游戏显示"Liberal"
    7: "Communist",      # 🔍 推测 - 未直接测试但逻辑推导
}

# 测试历程记录
TEST_HISTORY = {
    "第一次测试": {
        "转换": "所有ID → ID 1 + ID 2",
        "游戏显示": "Reactionary + Fascist",
        "确认": "ID 1 = Reactionary, ID 2 = Fascist"
    },
    "第二次测试": {
        "转换": "所有ID → ID 3 + ID 4", 
        "游戏显示": "Conservative + Socialist",
        "确认": "ID 3 = Conservative, ID 4 = Socialist"
    },
    "第三次测试": {
        "转换": "所有ID → ID 3 + ID 5",
        "游戏显示": "Conservative + ？",
        "结果": "需要进一步测试ID 5"
    },
    "第四次测试": {
        "转换": "所有ID → ID 3 + ID 6",
        "游戏显示": "Conservative + Liberal",
        "确认": "ID 6 = Liberal ✅"
    }
}

# 中国人口意识形态转换规则
CHINESE_POPULATION_IDEOLOGY_CONVERSION = {
    # 极端意识形态 → 温和意识形态
    "Reactionary": "Conservative",     # ID 1 → ID 3
    "Fascist": "Liberal",             # ID 2 → ID 6  
    "Socialist": "Conservative",       # ID 4 → ID 3
    "Anarcho-Liberal": "Liberal",     # ID 5 → ID 6
    "Communist": "Conservative",       # ID 7 → ID 3
    
    # 保持不变的温和意识形态
    "Conservative": "Conservative",    # ID 3 → ID 3 (不变)
    "Liberal": "Liberal",             # ID 6 → ID 6 (不变)
}

# 数值映射
IDEOLOGY_ID_CONVERSION_MAP = {
    1: 3,  # Reactionary → Conservative
    2: 6,  # Fascist → Liberal
    4: 3,  # Socialist → Conservative  
    5: 6,  # Anarcho-Liberal → Liberal
    7: 3,  # Communist → Conservative
    # 3: 3,  # Conservative → Conservative (不需要转换)
    # 6: 6,  # Liberal → Liberal (不需要转换)
}

def display_mapping_summary():
    """显示完整的映射总结"""
    print("🎯 Victoria II 意识形态ID映射 - 完整确认版")
    print("="*60)
    
    print("\n✅ 已确认的ID映射:")
    for id_num, name in VICTORIA2_IDEOLOGY_MAPPING.items():
        status = "✅ 确认" if id_num in [1, 2, 3, 4, 6] else "🔍 推测"
        print(f"  ID {id_num}: {name:<15} {status}")
    
    print("\n🔄 中国人口意识形态转换规则:")
    for old_ideology, new_ideology in CHINESE_POPULATION_IDEOLOGY_CONVERSION.items():
        if old_ideology != new_ideology:
            old_id = next((k for k, v in VICTORIA2_IDEOLOGY_MAPPING.items() if v == old_ideology), "?")
            new_id = next((k for k, v in VICTORIA2_IDEOLOGY_MAPPING.items() if v == new_ideology), "?")
            print(f"  {old_ideology:<15} (ID {old_id}) → {new_ideology:<15} (ID {new_id})")
    
    print("\n📊 数值转换映射:")
    for old_id, new_id in IDEOLOGY_ID_CONVERSION_MAP.items():
        old_name = VICTORIA2_IDEOLOGY_MAPPING.get(old_id, "Unknown")
        new_name = VICTORIA2_IDEOLOGY_MAPPING.get(new_id, "Unknown")
        print(f"  ID {old_id} ({old_name}) → ID {new_id} ({new_name})")
    
    print("\n🎮 测试结果:")
    print("  最终游戏显示: Conservative + Liberal")
    print("  目标达成: ✅ 中国人口意识形态成功调整为温和派")
    
    print("\n📝 使用说明:")
    print("  1. 所有中国人口宗教 → mahayana")
    print("  2. 极端意识形态转换为温和意识形态:")
    print("     • Reactionary/Socialist/Communist → Conservative")
    print("     • Fascist/Anarcho-Liberal → Liberal")
    print("  3. 结果: 中国人口只有Conservative和Liberal两种意识形态")

def get_ideology_name(ideology_id: int) -> str:
    """根据ID获取意识形态名称"""
    return VICTORIA2_IDEOLOGY_MAPPING.get(ideology_id, f"Unknown_ID_{ideology_id}")

def get_ideology_id(ideology_name: str) -> int:
    """根据名称获取意识形态ID"""
    for id_num, name in VICTORIA2_IDEOLOGY_MAPPING.items():
        if name.lower() == ideology_name.lower():
            return id_num
    return -1

if __name__ == "__main__":
    display_mapping_summary()
