#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 完整国家分析报告
基于所有221个国家的数据
"""

import json
import os
from collections import defaultdict, Counter


def load_data():
    """加载最新的解析数据"""
    try:
        with open('china_optimized_parsed.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None


def analyze_all_countries(data):
    """分析所有国家数据"""
    print("\n" + "="*80)
    print("🌍 Victoria II 全球国家分析报告 (2245年)")
    print("="*80)
    
    countries = data.get('countries', {})
    if not countries:
        print("没有国家数据")
        return
    
    # 统计各类国家
    active_countries = []  # 有活动的国家
    major_powers = []     # 大国（研究点数>15000）
    secondary_powers = [] # 次强国（研究点数5000-15000）
    minor_countries = []  # 小国（研究点数1000-5000）
    weak_states = []      # 弱国（研究点数<1000）
    
    total_research = 0
    total_tax = 0
    
    for tag, info in countries.items():
        research = info.get('research_points', 0)
        tax = info.get('tax_base', 0)
        
        total_research += research
        total_tax += tax
        
        if research > 0 or tax > 0:
            active_countries.append((tag, info))
            
            if research >= 15000:
                major_powers.append((tag, info))
            elif research >= 5000:
                secondary_powers.append((tag, info))
            elif research >= 1000:
                minor_countries.append((tag, info))
            else:
                weak_states.append((tag, info))
    
    # 基本统计
    print(f"📊 基本统计:")
    print(f"   总国家数: {len(countries)}")
    print(f"   活跃国家: {len(active_countries)}")
    print(f"   大国 (研究>15000): {len(major_powers)}")
    print(f"   次强国 (研究5000-15000): {len(secondary_powers)}")
    print(f"   小国 (研究1000-5000): {len(minor_countries)}")
    print(f"   弱国 (研究<1000): {len(weak_states)}")
    print(f"   全球总研究点数: {total_research:,.0f}")
    print(f"   全球总税收: {total_tax:,.0f}")
    
    # 大国详细分析
    print(f"\n🏆 大国详细分析 ({len(major_powers)}个):")
    print(f"{'排名':<4} {'国家':<4} {'研究点数':<12} {'税收基础':<12} {'科技':<6} {'标志':<6} {'分类':<10}")
    print("-" * 70)
    
    major_powers.sort(key=lambda x: x[1].get('research_points', 0), reverse=True)
    
    for i, (tag, info) in enumerate(major_powers, 1):
        research = info.get('research_points', 0)
        tax = info.get('tax_base', 0)
        tech = info.get('technology_count', 0)
        flags = info.get('flag_count', 0)
        
        # 分类国家
        if tag == 'CHI':
            category = "玩家国家"
        elif research > 25000:
            category = "超级大国"
        elif research > 20000:
            category = "列强"
        else:
            category = "大国"
            
        print(f"{i:<4} {tag:<4} {research:<12.0f} {tax:<12.1f} {tech:<6} {flags:<6} {category:<10}")
    
    # 地区分析
    print(f"\n🗺️  地区势力分析:")
    
    # 根据国家代码进行地区分类（简化版）
    regions = {
        '欧洲': ['ENG', 'FRA', 'GER', 'AUS', 'RUS', 'ITA', 'SPA', 'POR', 'NET', 'BEL', 'SWI', 'SCA', 'PRU'],
        '亚洲': ['CHI', 'JAP', 'IND', 'SIA', 'KOR', 'PER', 'AFG', 'BUR', 'TIB'],
        '美洲': ['USA', 'MEX', 'BRZ', 'ARG', 'COL', 'CHL', 'BOL', 'PEU', 'VNZ'],
        '非洲': ['EGY', 'ETH', 'MAD', 'SAF', 'MOR', 'TUN', 'LIB'],
        '中东': ['TUR', 'PER', 'YEM', 'OMA', 'NEJ', 'HDJ', 'IRQ']
    }
    
    for region, country_codes in regions.items():
        region_countries = [(tag, info) for tag, info in countries.items() if tag in country_codes]
        if region_countries:
            region_research = sum(info.get('research_points', 0) for _, info in region_countries)
            region_tax = sum(info.get('tax_base', 0) for _, info in region_countries)
            
            # 找出该地区最强国家
            strongest = max(region_countries, key=lambda x: x[1].get('research_points', 0))
            
            print(f"   {region}: {len(region_countries)}国, 总研究{region_research:,.0f}, 霸主{strongest[0]}({strongest[1].get('research_points', 0):,.0f})")
    
    # 科技发展分析
    print(f"\n🔬 科技发展分析:")
    tech_levels = Counter()
    for tag, info in countries.items():
        tech_count = info.get('technology_count', 0)
        if tech_count >= 150:
            tech_levels['现代化'] += 1
        elif tech_count >= 120:
            tech_levels['工业化'] += 1
        elif tech_count >= 50:
            tech_levels['发展中'] += 1
        elif tech_count > 0:
            tech_levels['落后'] += 1
        else:
            tech_levels['原始'] += 1
    
    for level, count in tech_levels.most_common():
        print(f"   {level}: {count}个国家")
    
    # 经济集中度分析
    print(f"\n💰 经济集中度分析:")
    sorted_by_research = sorted(countries.items(), key=lambda x: x[1].get('research_points', 0), reverse=True)
    
    top_5_research = sum(info.get('research_points', 0) for _, info in sorted_by_research[:5])
    top_10_research = sum(info.get('research_points', 0) for _, info in sorted_by_research[:10])
    
    if total_research > 0:
        print(f"   前5强研究点占比: {(top_5_research/total_research)*100:.1f}%")
        print(f"   前10强研究点占比: {(top_10_research/total_research)*100:.1f}%")
    
    # 特殊国家分析
    print(f"\n🎯 特殊国家分析:")
    
    # 玩家国家CHI
    if 'CHI' in countries:
        chi_info = countries['CHI']
        chi_rank = next(i for i, (tag, _) in enumerate(sorted_by_research, 1) if tag == 'CHI')
        print(f"   🇨🇳 中国(玩家): 排名第{chi_rank}, 研究{chi_info.get('research_points', 0):,.0f}, 税收{chi_info.get('tax_base', 0):,.1f}")
    
    # 找出研究点数最高但税收很低的国家（可能是小国但科技先进）
    tech_vs_economy = []
    for tag, info in countries.items():
        research = info.get('research_points', 0)
        tax = info.get('tax_base', 0)
        if research > 20000 and tax < 50:  # 高科技但经济弱
            tech_vs_economy.append((tag, research, tax))
    
    if tech_vs_economy:
        print(f"   🔬 科技先进的小国:")
        for tag, research, tax in sorted(tech_vs_economy, key=lambda x: x[1], reverse=True)[:5]:
            print(f"     {tag}: 研究{research:,.0f}, 税收{tax:.1f}")


def analyze_player_performance(data):
    """分析玩家国家表现"""
    print(f"\n" + "="*80)
    print("🎮 玩家国家 (中国) 详细分析")
    print("="*80)
    
    countries = data.get('countries', {})
    if 'CHI' not in countries:
        print("未找到中国数据")
        return
    
    chi_info = countries['CHI']
    
    # 计算排名
    sorted_countries = sorted(countries.items(), key=lambda x: x[1].get('research_points', 0), reverse=True)
    chi_rank = next(i for i, (tag, _) in enumerate(sorted_countries, 1) if tag == 'CHI')
    
    print(f"🏆 综合表现:")
    print(f"   全球排名: 第{chi_rank}名 (共{len(countries)}个国家)")
    print(f"   研究点数: {chi_info.get('research_points', 0):,.0f}")
    print(f"   税收基础: {chi_info.get('tax_base', 0):,.1f}")
    print(f"   科技数量: {chi_info.get('technology_count', 0)}")
    print(f"   标志数量: {chi_info.get('flag_count', 0)}")
    print(f"   首都ID: {chi_info.get('capital', 0)}")
    
    # 与其他大国比较
    research = chi_info.get('research_points', 0)
    tax = chi_info.get('tax_base', 0)
    
    print(f"\n📊 与其他大国对比:")
    comparison_countries = ['RUS', 'ENG', 'USA', 'FRA', 'GER', 'JAP']
    
    for tag in comparison_countries:
        if tag in countries:
            other_info = countries[tag]
            other_research = other_info.get('research_points', 0)
            other_tax = other_info.get('tax_base', 0)
            
            research_diff = research - other_research
            tax_diff = tax - other_tax
            
            print(f"   vs {tag}: 研究{research_diff:+.0f}, 税收{tax_diff:+.1f}")
    
    # 评估表现
    print(f"\n🎯 表现评估:")
    if chi_rank <= 5:
        performance = "🥇 超级大国 - 表现卓越!"
    elif chi_rank <= 10:
        performance = "🥈 世界列强 - 表现优秀!"
    elif chi_rank <= 20:
        performance = "🥉 地区强国 - 表现良好"
    else:
        performance = "📈 发展中国家 - 仍需努力"
    
    print(f"   {performance}")
    
    # 提供建议
    print(f"\n💡 发展建议:")
    if tax < 10000:
        print("   • 建议继续扩张经济基础，提高税收收入")
    if chi_info.get('technology_count', 0) < 150:
        print("   • 建议加大科技投入，追赶先进国家")
    if chi_rank > 1:
        print("   • 建议制定策略超越领先国家")


def main():
    """主函数"""
    print("Victoria II 全球国家完整分析")
    print("基于2245年存档数据")
    
    data = load_data()
    if not data:
        return
    
    # 执行分析
    analyze_all_countries(data)
    analyze_player_performance(data)
    
    print(f"\n" + "="*80)
    print("✅ 分析完成! 这是一个庞大而复杂的世界!")
    print("="*80)


if __name__ == "__main__":
    main()
