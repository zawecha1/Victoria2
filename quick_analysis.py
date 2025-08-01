#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 存档快速分析脚本
自动分析最新的JSON文件
"""

import json
import os
from collections import defaultdict, Counter


def load_latest_json():
    """加载最新的JSON文件"""
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    if not json_files:
        print("错误: 当前目录下没有找到JSON文件")
        return None, None
    
    # 按修改时间排序，选择最新的
    json_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_file = json_files[0]
    
    print(f"自动选择最新文件: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, latest_file
    except Exception as e:
        print(f"加载JSON文件失败: {e}")
        return None, None


def analyze_basic_info(data):
    """分析基本信息"""
    print("\n" + "="*60)
    print("📊 游戏基本信息")
    print("="*60)
    
    if hasattr(data, 'date'):
        # 新格式数据
        print(f"📅 游戏日期: {data.date}")
        print(f"🎮 玩家国家: {data.player}")
        print(f"🏛️  政府类型: {data.government}")
        print(f"📊 开始日期: {data.start_date}")
        print(f"🚩 游戏标志: {len(data.flags) if data.flags else 0}")
        print(f"🌍 国家数量: {len(data.countries) if data.countries else 0}")
        
        if hasattr(data, 'provinces') and isinstance(data.provinces, dict):
            print(f"🗺️  省份总数: {data.provinces.get('total_provinces', 'Unknown')}")
    else:
        # 旧格式数据
        basic = data.get('basic_info', {})
        print(f"📅 游戏日期: {basic.get('date', 'Unknown')}")
        print(f"🎮 玩家国家: {basic.get('player', 'Unknown')}")
        print(f"🏛️  政府类型: {basic.get('government', 'Unknown')}")
        print(f"📊 开始日期: {basic.get('start_date', 'Unknown')}")
        print(f"🚩 游戏标志: {data.get('flag_count', 0)}")
        print(f"🌍 国家数量: {data.get('country_count', 0)}")
        
        provinces = data.get('provinces', {})
        print(f"🗺️  省份总数: {provinces.get('total_provinces', 'Unknown')}")
        
        # 计算游戏年限
        start_date = basic.get('start_date', '1836.1.1')
        current_date = basic.get('date', '1836.1.1')
        if start_date and current_date:
            try:
                start_year = int(start_date.split('.')[0])
                current_year = int(current_date.split('.')[0])
                game_years = current_year - start_year
                print(f"⏱️  游戏进行年数: {game_years} 年")
            except:
                pass


def analyze_countries(data):
    """分析国家数据"""
    print("\n" + "="*60)
    print("🌍 国家经济分析")
    print("="*60)
    
    # 处理不同格式的数据
    if hasattr(data, 'countries'):
        countries = data.countries
    else:
        countries = data.get('countries', {})
    
    if not countries:
        print("没有国家数据")
        return
    
    # 创建排名列表
    country_stats = []
    
    for tag, info in countries.items():
        if isinstance(info, dict):
            tax_base = info.get('tax_base', 0)
            research_points = info.get('research_points', 0)
            flag_count = info.get('flag_count', 0)
            tech_count = info.get('technology_count', 0)
            
            country_stats.append({
                'tag': tag,
                'tax_base': float(tax_base) if tax_base else 0,
                'research_points': float(research_points) if research_points else 0,
                'flag_count': int(flag_count) if flag_count else 0,
                'tech_count': int(tech_count) if tech_count else 0
            })
    
    if not country_stats:
        print("没有有效的国家统计数据")
        return
    
    # 按研究点数排序
    research_ranking = sorted(country_stats, key=lambda x: x['research_points'], reverse=True)
    print(f"\n🔬 研究点数排行榜 (前10名):")
    for i, country in enumerate(research_ranking[:10], 1):
        tag = country['tag']
        research = country['research_points']
        tax = country['tax_base']
        if research > 0:  # 只显示有研究点数的国家
            print(f"{i:2d}. {tag}: {research:>10.1f} 研究点 (税收: {tax:>8.1f})")
    
    # 按税收基础排序
    tax_ranking = sorted(country_stats, key=lambda x: x['tax_base'], reverse=True)
    print(f"\n💰 税收基础排行榜 (前10名):")
    for i, country in enumerate(tax_ranking[:10], 1):
        tag = country['tag']
        tax = country['tax_base']
        flags = country['flag_count']
        if tax > 0:  # 只显示有税收的国家
            print(f"{i:2d}. {tag}: {tax:>10.1f} 税收 (标志: {flags})")
    
    # 统计信息
    total_countries = len([c for c in country_stats if c['tax_base'] > 0 or c['research_points'] > 0])
    total_research = sum(c['research_points'] for c in country_stats)
    total_tax = sum(c['tax_base'] for c in country_stats)
    
    print(f"\n📈 统计汇总:")
    print(f"   活跃国家数: {total_countries}")
    print(f"   总研究点数: {total_research:,.1f}")
    print(f"   总税收基础: {total_tax:,.1f}")
    
    if research_ranking and research_ranking[0]['research_points'] > 0:
        top_country = research_ranking[0]
        print(f"   研究领先者: {top_country['tag']} ({top_country['research_points']:,.1f} 点)")


def analyze_worldmarket(data):
    """分析世界市场"""
    print("\n" + "="*60)
    print("🏪 世界市场分析")
    print("="*60)
    
    # 处理不同格式的数据
    if hasattr(data, 'worldmarket'):
        wm = data.worldmarket
    else:
        wm = data.get('worldmarket', {})
    
    if not wm:
        print("没有世界市场数据")
        return
    
    # 显示各个商品池的信息
    pools = {
        'worldmarket_pool': '📦 世界市场库存',
        'price_pool': '💰 商品价格',
        'supply_pool': '📈 供应池'
    }
    
    for pool_name, pool_desc in pools.items():
        commodity_count = wm.get(f'{pool_name}_commodities', 0)
        sample_data = wm.get(f'{pool_name}_sample', {})
        
        if commodity_count > 0:
            print(f"\n{pool_desc}:")
            print(f"   总商品种类: {commodity_count}")
            
            if sample_data:
                print("   热门商品:")
                # 按值排序显示前5个
                sorted_items = sorted(sample_data.items(), 
                                    key=lambda x: float(x[1]) if isinstance(x[1], (int, float, str)) and str(x[1]).replace('.', '').isdigit() else 0, 
                                    reverse=True)
                
                for commodity, value in sorted_items[:5]:
                    try:
                        value_f = float(value)
                        print(f"     {commodity:<15}: {value_f:>10.2f}")
                    except:
                        print(f"     {commodity:<15}: {str(value):>10}")


def analyze_provinces(data):
    """分析省份"""
    print("\n" + "="*60)
    print("🗺️  省份分析")
    print("="*60)
    
    # 处理不同格式的数据
    if hasattr(data, 'provinces'):
        provinces_data = data.provinces
    else:
        provinces_data = data.get('provinces', {})
    
    if isinstance(provinces_data, dict):
        total_provinces = provinces_data.get('total_provinces', 0)
        sample_provinces = provinces_data.get('sample_provinces', [])
        
        print(f"📊 省份总数: {total_provinces}")
        print(f"🔍 样本省份: {len(sample_provinces)}")
        
        if sample_provinces:
            # 统计拥有者
            owners = Counter()
            controllers = Counter()
            
            for prov in sample_provinces:
                owner = prov.get('owner', 'Unknown')
                controller = prov.get('controller', 'Unknown')
                owners[owner] += 1
                controllers[controller] += 1
            
            print(f"\n🏴 省份拥有者分布 (样本):")
            for owner, count in owners.most_common():
                print(f"   {owner}: {count} 个省份")
            
            # 显示占领情况
            occupied_provinces = [p for p in sample_provinces 
                                if p.get('owner') != p.get('controller')]
            if occupied_provinces:
                print(f"\n⚔️ 被占领省份:")
                for prov in occupied_provinces:
                    name = prov.get('name', 'Unknown')
                    owner = prov.get('owner', 'Unknown') 
                    controller = prov.get('controller', 'Unknown')
                    print(f"   {name}: {owner} → {controller}")


def analyze_flags(data):
    """分析游戏标志"""
    print("\n" + "="*60)
    print("🚩 游戏标志分析")
    print("="*60)
    
    # 处理不同格式的数据
    if hasattr(data, 'flags'):
        flags = data.flags
    else:
        flags = data.get('flags', [])
    
    if not flags:
        print("没有标志数据")
        return
    
    print(f"总标志数: {len(flags)}")
    
    # 分类分析
    categories = defaultdict(list)
    
    for flag in flags:
        flag_name = flag if isinstance(flag, str) else str(flag)
        
        if 'nobel' in flag_name.lower():
            categories['🏆 诺贝尔奖'].append(flag_name)
        elif 'olympiad' in flag_name.lower():
            categories['🏅 奥运会'].append(flag_name)
        elif any(word in flag_name.lower() for word in ['war', 'revolution', 'rebellion']):
            categories['⚔️ 战争/革命'].append(flag_name)
        elif any(word in flag_name.lower() for word in ['canal', 'build', 'statue']):
            categories['🏗️ 建设工程'].append(flag_name)
        elif any(word in flag_name.lower() for word in ['discover', 'found', 'expedition']):
            categories['🔍 探索发现'].append(flag_name)
        else:
            categories['📋 其他'].append(flag_name)
    
    print(f"\n标志分类:")
    for category, flag_list in categories.items():
        print(f"\n{category} ({len(flag_list)}个):")
        for flag in flag_list[:8]:  # 显示前8个
            print(f"  • {flag}")
        if len(flag_list) > 8:
            print(f"  ... 还有{len(flag_list) - 8}个")


def main():
    """主函数"""
    print("Victoria II 存档快速分析")
    print("="*50)
    
    # 自动加载最新的JSON文件
    data, filename = load_latest_json()
    
    if not data:
        return
    
    print(f"正在分析: {filename}")
    
    # 执行所有分析
    analyze_basic_info(data)
    analyze_countries(data)
    analyze_worldmarket(data)
    analyze_provinces(data)
    analyze_flags(data)
    
    print("\n" + "="*60)
    print("✅ 分析完成!")
    print("="*60)


if __name__ == "__main__":
    main()
