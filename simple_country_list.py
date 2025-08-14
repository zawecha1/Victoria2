#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
维多利亚2存档国家代码名称简表生成器
Generate a simple country codes and names list from Victoria II save files
"""

import json
import os

def create_simple_country_list():
    """从现有的详细JSON文件创建简洁的国家代码和名称列表"""
    
    # 查找最新的国家数据文件
    json_files = [f for f in os.listdir('.') if f.startswith('countries_') and f.endswith('.json')]
    if not json_files:
        print("❌ 未找到国家数据文件")
        return
    
    # 使用最新的文件
    latest_file = max(json_files, key=lambda x: os.path.getmtime(x))
    print(f"📁 使用数据文件: {latest_file}")
    
    # 读取数据
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    countries = data['countries']
    active_countries = set(data['active_countries'])
    
    # 创建简洁的国家列表
    simple_list = {
        'metadata': {
            'source_file': data['metadata']['source_file'],
            'total_countries': len(countries),
            'active_countries': len(active_countries),
            'extraction_time': data['metadata']['extraction_time']
        },
        'countries': {},
        'active_countries_only': {},
        'country_codes': list(countries.keys()),
        'active_country_codes': data['active_countries']
    }
    
    # 提取所有国家的基本信息
    for tag, info in countries.items():
        simple_list['countries'][tag] = {
            'name': info['name'],
            'capital': info['capital'],
            'culture': info['primary_culture'],
            'civilized': info['civilized'],
            'active': tag in active_countries
        }
    
    # 只提取活跃国家
    for tag in active_countries:
        if tag in countries:
            info = countries[tag]
            simple_list['active_countries_only'][tag] = {
                'name': info['name'],
                'capital': info['capital'],
                'culture': info['primary_culture'],
                'civilized': info['civilized']
            }
    
    # 保存简洁版本
    output_file = f"simple_countries_{data['metadata']['source_file'].replace('.v2', '')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(simple_list, f, ensure_ascii=False, indent=2)
    
    print(f"💾 简洁版本已保存到: {output_file}")
    
    # 输出摘要
    print("\n" + "=" * 60)
    print("📊 国家代码和名称摘要:")
    print(f"   总国家数: {len(countries)}")
    print(f"   活跃国家数: {len(active_countries)}")
    
    print(f"\n🌟 主要国家信息:")
    major_countries = ['CHI', 'JAP', 'RUS', 'GBR', 'FRA', 'GER', 'USA', 'TUR', 'AUS', 'ENG']
    for tag in major_countries:
        if tag in countries:
            info = countries[tag]
            status = "活跃" if tag in active_countries else "已灭亡"
            civ = "文明化" if info['civilized'] else "未文明化"
            print(f"   {tag:3} - {info['name']:15} ({civ}, {status})")
    
    print("\n" + "=" * 60)
    print("✅ 简洁版本生成完成！")
    print("=" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("📋 维多利亚2国家代码名称简表生成器")
    print("=" * 60)
    create_simple_country_list()
