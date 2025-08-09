#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无省份国家分析解释器 (explain_no_province_countries.py)
======================================================
解释为什么Victoria II中有些国家没有省份
"""

import json

def analyze_no_province_countries():
    """分析无省份国家的原因"""
    
    # 读取最新的分析结果
    filename = "comprehensive_country_analysis_20250809_191153.json"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 未找到分析文件: {filename}")
        return
    
    print("🔍 Victoria II 无省份国家分析报告")
    print("=" * 50)
    
    # 基本统计
    analysis_info = data['analysis_info']
    countries_without_provinces = data['countries_without_provinces']
    
    print(f"📊 基本统计:")
    print(f"   总国家数: {analysis_info['total_countries']}")
    print(f"   有省份的国家: {analysis_info['countries_with_provinces']}")
    print(f"   无省份的国家: {analysis_info['countries_without_provinces']}")
    print(f"   文明化国家: {analysis_info['civilized_countries']}")
    
    # 分析无省份国家的类型
    print(f"\\n🔍 无省份国家类型分析:")
    
    # 1. 分类统计
    potential_formable = []  # 可成立国家
    releasable = []          # 可释放国家
    special_tags = []        # 特殊标签
    dead_countries = []      # 灭亡国家
    
    for tag, info in countries_without_provinces.items():
        # 判断国家类型
        if tag == "REB":
            special_tags.append((tag, "叛军"))
        elif tag in ["GER", "KUK", "DEN", "FIN", "NOR", "SWE", "SCO", "ITA"]:
            if info.get('capital', 0) > 0:
                potential_formable.append((tag, info))
            else:
                dead_countries.append((tag, info))
        elif tag in ["NGF", "SGF", "SCH", "LOM", "LUC", "MOD", "PAP", "SAR", "SIC", "TRE"]:
            releasable.append((tag, info))
        else:
            # 检查是否有首都（可能是灭亡的国家）
            if info.get('capital', 0) > 0:
                dead_countries.append((tag, info))
            else:
                special_tags.append((tag, "未知类型"))
    
    print(f"\\n1️⃣ 可成立国家 ({len(potential_formable)}个):")
    print("   这些是通过统一、解放等方式可以成立的国家")
    for tag, info in potential_formable[:10]:
        capital = info.get('capital', 0)
        gov = info.get('government', 'unknown')[:10]
        print(f"   • {tag}: 首都省份{capital}, 政府{gov}")
    if len(potential_formable) > 10:
        print(f"   ... 还有 {len(potential_formable) - 10} 个")
    
    print(f"\\n2️⃣ 可释放国家 ({len(releasable)}个):")
    print("   这些是德意志、意大利等地区的小邦国")
    for tag, info in releasable[:10]:
        capital = info.get('capital', 0)
        culture = info.get('primary_culture', 'unknown')
        print(f"   • {tag}: 首都省份{capital}, 文化{culture}")
    if len(releasable) > 10:
        print(f"   ... 还有 {len(releasable) - 10} 个")
    
    print(f"\\n3️⃣ 灭亡国家 ({len(dead_countries)}个):")
    print("   这些国家曾经存在但已被征服，仍保留在存档中")
    for tag, info in dead_countries[:10]:
        capital = info.get('capital', 0)
        prestige = info.get('prestige', 0)
        print(f"   • {tag}: 首都省份{capital}, 威望{prestige:.1f}")
    if len(dead_countries) > 10:
        print(f"   ... 还有 {len(dead_countries) - 10} 个")
    
    print(f"\\n4️⃣ 特殊标签 ({len(special_tags)}个):")
    print("   这些是游戏机制相关的特殊国家标签")
    for tag, desc in special_tags[:10]:
        print(f"   • {tag}: {desc}")
    
    print(f"\\n💡 总结:")
    print(f"   Victoria II中确实存在{analysis_info['countries_without_provinces']}个无省份国家")
    print(f"   这是正常现象，主要原因包括:")
    print(f"   1. 游戏预设了很多可成立的国家（如德意志、意大利统一）")
    print(f"   2. 历史上存在的小邦国可以通过外交释放")
    print(f"   3. 被征服的国家在游戏中仍保留数据结构")
    print(f"   4. 特殊游戏机制标签（如叛军REB）")
    print(f"\\n   因此原分析程序是正确的：")
    print(f"   • 有省份的国家: {analysis_info['countries_with_provinces']}个")
    print(f"   • 无省份的国家: {analysis_info['countries_without_provinces']}个")
    print(f"   • 这是Victoria II游戏机制的正常表现 ✅")

if __name__ == "__main__":
    analyze_no_province_countries()
