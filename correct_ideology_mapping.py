#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 意识形态ID正确映射查询
"""

def show_correct_ideology_mapping():
    """显示Victoria II中正确的意识形态ID映射"""
    
    print("Victoria II 意识形态ID正确对应关系:")
    print("="*50)
    
    # 基于游戏实际机制的正确映射
    correct_mapping = {
        1: "Reactionary",        # 反动主义
        2: "Fascist",           # 法西斯主义  
        3: "Conservative",      # 保守主义
        4: "Liberal",           # 自由主义
        5: "Anarcho_Liberal",   # 无政府自由主义
        6: "Socialist",         # 社会主义
        7: "Communist"          # 共产主义
    }
    
    for id_val, name in correct_mapping.items():
        print(f"  ID {id_val}: {name}")
    
    print("\n基于游戏显示结果推断:")
    print("我们转换到 ID 1 和 ID 2")
    print("游戏显示为 Reactionary 和 Fascist")
    print("所以:")
    print("  ID 1 = Reactionary (反动主义)")
    print("  ID 2 = Fascist (法西斯主义)")
    
    print("\n如果要让中国人口变为温和意识形态，应该转换到:")
    print("  Conservative = ID 3")
    print("  Liberal = ID 4")
    
    return correct_mapping

def generate_corrected_ideology_mapping():
    """生成修正后的意识形态映射"""
    
    print("\n" + "="*50)
    print("修正后的转换规则:")
    print("="*50)
    
    # 修正后的映射：转换到温和的Conservative和Liberal
    corrected_mapping = {
        1: 3,  # Reactionary(1) -> Conservative(3)
        2: 4,  # Fascist(2) -> Liberal(4)  
        5: 3,  # Socialist(5) -> Conservative(3)
        6: 3,  # Communist(6) -> Conservative(3)
        7: 4   # [原]Fascist(7) -> Liberal(4)
    }
    
    print("新的转换规则 (基于正确的ID映射):")
    print("# 极端意识形态转换为温和意识形态")
    print("# Reactionary(1) + Socialist(5) + Communist(6) -> Conservative(3)")
    print("# Fascist(2) + [原]Fascist(7) -> Liberal(4)")
    print("# Conservative(3) 和 Liberal(4) 保持不变")
    
    print("\nPython代码:")
    print("```python")
    print("self.ideology_mapping = {")
    for old_id, new_id in corrected_mapping.items():
        print(f"    {old_id}: {new_id},  # 转换说明")
    print("}")
    print("```")
    
    return corrected_mapping

def main():
    correct_ids = show_correct_ideology_mapping()
    corrected_mapping = generate_corrected_ideology_mapping()
    
    print(f"\n{'='*50}")
    print("需要修改 chinese_pop_modifier.py 中的映射规则")
    print("="*50)

if __name__ == "__main__":
    main()
