#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试意识形态ID对应关系
基于游戏实际显示结果反推正确的映射
"""

def analyze_ideology_mapping():
    """分析意识形态ID实际对应关系"""
    
    print("根据游戏显示结果分析意识形态ID映射:")
    print("="*60)
    
    # 我们的原始转换规则
    our_mapping = {
        3: 2,  # 我们认为: Reactionary(3) -> Liberal(2)
        4: 2,  # 我们认为: Anarcho-Liberal(4) -> Liberal(2)  
        5: 1,  # 我们认为: Socialist(5) -> Conservative(1)
        6: 1,  # 我们认为: Communist(6) -> Conservative(1)
        7: 1   # 我们认为: Fascist(7) -> Conservative(1)
    }
    
    # 游戏实际显示结果是Reactionary和Fascist
    # 这意味着我们转换到的ID 1和2实际对应的是Reactionary和Fascist
    
    print("❌ 我们的错误假设:")
    print("  ID 1 = Conservative (保守主义)")
    print("  ID 2 = Liberal (自由主义)")
    print()
    
    print("🎮 游戏实际显示:")
    print("  转换后显示为 Reactionary 和 Fascist")
    print()
    
    print("🔍 可能的正确映射:")
    print("方案1 - ID顺序可能不同:")
    print("  ID 1 = Reactionary (反动主义)")
    print("  ID 2 = Fascist (法西斯主义)")
    print("  ID 3 = Conservative (保守主义)")
    print("  ID 4 = Liberal (自由主义)")
    print()
    
    print("方案2 - 或者其他顺序:")
    print("  需要通过原始数据确认每个ID对应的真实意识形态")
    print()
    
    # 分析原始数据中哪个ID值最高，对应游戏中的主要意识形态
    print("📊 原始数据分析:")
    original_sample = {
        1: 17.13712,  # 我们假设的Conservative
        2: 8.49777,   # 我们假设的Liberal  
        3: 6.99579,   # 我们假设的Reactionary
        4: 22.85031,  # 我们假设的Anarcho-Liberal (最高值)
        5: 12.99979,  # 我们假设的Socialist
        6: 18.52100,  # 我们假设的Communist (第二高)
        7: 12.99814   # 我们假设的Fascist
    }
    
    sorted_ideologies = sorted(original_sample.items(), key=lambda x: x[1], reverse=True)
    print("原始分布从高到低:")
    for id_val, percentage in sorted_ideologies:
        print(f"  ID {id_val}: {percentage:.2f}%")
    
    print()
    print("💡 推测:")
    print("如果游戏中主要显示为某种意识形态，")
    print("那么ID 4 (最高22.85%) 可能对应该意识形态")
    
    return our_mapping

def suggest_correct_mapping():
    """建议正确的映射方案"""
    
    print("\n" + "="*60)
    print("🔧 建议的修正方案:")
    print("="*60)
    
    print("需要您确认游戏中实际显示的意识形态分布:")
    print("1. 约60%的人口显示为什么意识形态？")
    print("2. 约40%的人口显示为什么意识形态？")
    print()
    
    print("可能的正确转换规则:")
    print()
    
    print("选项A - 如果要让中国人变为Conservative + Liberal:")
    conservative_target = input("请输入Conservative对应的ID (1-7): ").strip()
    liberal_target = input("请输入Liberal对应的ID (1-7): ").strip()
    
    if conservative_target.isdigit() and liberal_target.isdigit():
        conservative_id = int(conservative_target)
        liberal_id = int(liberal_target)
        
        print(f"\n修正后的映射规则:")
        print(f"# Reactionary(3) + Anarcho-Liberal(4) -> Liberal({liberal_id})")
        print(f"# Socialist(5) + Communist(6) + Fascist(7) -> Conservative({conservative_id})")
        
        corrected_mapping = {
            3: liberal_id,    # Reactionary -> Liberal
            4: liberal_id,    # Anarcho-Liberal -> Liberal  
            5: conservative_id,  # Socialist -> Conservative
            6: conservative_id,  # Communist -> Conservative
            7: conservative_id   # Fascist -> Conservative
        }
        
        return corrected_mapping
    
    return None

def main():
    print("Victoria II 意识形态ID映射分析工具")
    print("="*60)
    
    current_mapping = analyze_ideology_mapping()
    
    print("\n当前转换结果分析:")
    print("原始分布 -> 转换后分布")
    print("Conservative(1): 17.14% -> 61.66% (增加44.52%)")
    print("Liberal(2): 8.50% -> 38.34% (增加29.84%)")
    print("其他意识形态: 全部归零")
    print()
    
    corrected = suggest_correct_mapping()
    
    if corrected:
        print(f"\n生成修正代码:")
        print("```python")
        print("self.ideology_mapping = {")
        for old_id, new_id in corrected.items():
            print(f"    {old_id}: {new_id},")
        print("}")
        print("```")

if __name__ == "__main__":
    main()
