#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速分析 civilized 字段枚举值
"""

import re
from collections import Counter

def quick_analyze_civilized(filename='autosave.v2'):
    """快速分析 civilized 字段的值"""
    print("⚡ 快速分析 civilized 字段...")
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        print(f"✅ 文件读取成功")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 直接搜索所有 civilized= 字段
    civilized_pattern = r'civilized\s*=\s*([^\n\s]+)'
    matches = re.findall(civilized_pattern, content)
    
    # 统计值
    civilized_values = Counter()
    for match in matches:
        value = match.strip().strip('"')
        civilized_values[value] += 1
    
    print(f"\n" + "="*50)
    print(f"🏛️ Victoria II civilized 字段枚举值")
    print(f"="*50)
    print(f"📊 总共找到: {len(matches)} 个 civilized 字段")
    print(f"🎯 不同值类型: {len(civilized_values)} 种")
    
    print(f"\n📋 所有 civilized 枚举值:")
    print(f"{'值':<15} {'出现次数':<10} {'百分比'}")
    print("-" * 40)
    
    for value, count in civilized_values.most_common():
        percentage = count / len(matches) * 100
        print(f"{value:<15} {count:<10} {percentage:>6.1f}%")
    
    return civilized_values

def show_civilized_enum_definition():
    """显示 civilized 字段的完整定义"""
    print(f"\n📚 Victoria II civilized 字段完整定义:")
    print("="*50)
    
    enum_info = {
        "字段名": "civilized",
        "数据类型": "布尔值/枚举",
        "可能值": [
            "yes - 已文明化国家",
            "no - 未文明化国家"
        ],
        "默认值": "no (对于大多数非欧洲国家)",
        "影响": [
            "科技研发速度和可用科技",
            "外交选项和能力",
            "工业建设能力",
            "殖民能力",
            "人口增长率",
            "教育效率"
        ]
    }
    
    print(f"• 字段名: {enum_info['字段名']}")
    print(f"• 数据类型: {enum_info['数据类型']}")
    print(f"• 默认值: {enum_info['默认值']}")
    
    print(f"\n🎯 可能的枚举值:")
    for value in enum_info['可能值']:
        print(f"  {value}")
    
    print(f"\n📈 对游戏的影响:")
    for impact in enum_info['影响']:
        print(f"  • {impact}")

def show_civilized_examples():
    """显示实际游戏中的文明化例子"""
    print(f"\n🌍 历史上的文明化情况 (1836年):")
    print("="*50)
    
    examples = {
        "已文明化国家 (civilized=yes)": [
            "ENG - 英国 (工业革命发源地)",
            "FRA - 法国 (欧洲强国)",
            "RUS - 俄国 (欧洲大国)",
            "AUS - 奥地利 (中欧强国)",
            "PRU - 普鲁士 (德意志邦联)",
            "USA - 美国 (新兴工业国)",
            "SWE - 瑞典 (北欧国家)",
            "NED - 荷兰 (海上贸易强国)"
        ],
        "未文明化国家 (civilized=no)": [
            "CHI - 中国 (需要通过改革文明化)",
            "JAP - 日本 (可通过明治维新文明化)", 
            "PER - 波斯 (中东传统国家)",
            "SIA - 暹罗/泰国 (东南亚王国)",
            "ETH - 埃塞俄比亚 (非洲古国)",
            "MAR - 摩洛哥 (北非国家)",
            "TUR - 奥斯曼帝国 (欧洲病夫)"
        ]
    }
    
    for category, countries in examples.items():
        print(f"\n{category}:")
        for country in countries:
            print(f"  • {country}")

def main():
    """主函数"""
    print("🚀 Victoria II civilized 字段枚举值分析")
    
    # 快速分析
    civilized_values = quick_analyze_civilized()
    
    # 显示枚举定义
    show_civilized_enum_definition()
    
    # 显示历史例子
    show_civilized_examples()
    
    print(f"\n" + "="*50)
    print(f"💡 总结:")
    print(f"civilized 字段只有两个有效枚举值:")
    print(f"  • 'yes' - 已文明化国家")
    print(f"  • 'no'  - 未文明化国家")
    print(f"="*50)

if __name__ == "__main__":
    main()
