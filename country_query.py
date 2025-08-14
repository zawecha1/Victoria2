#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
维多利亚2国家查询工具
Victoria II Country Query Tool

基于从victoria2_main_modifier.py提取的国家查找代码
使用方法：
1. 直接运行显示所有国家
2. python country_query.py CHI - 查询特定国家
3. python country_query.py active - 显示所有活跃国家
4. python country_query.py codes - 显示所有国家代码
"""

import json
import sys
import os
from typing import Dict, List, Optional

class CountryQuery:
    def __init__(self):
        self.data = None
        self.load_data()
    
    def load_data(self):
        """加载最新的国家数据"""
        json_files = [f for f in os.listdir('.') if f.startswith('simple_countries_') and f.endswith('.json')]
        if not json_files:
            print("❌ 未找到国家数据文件，请先运行 country_extractor.py")
            return
        
        latest_file = max(json_files, key=lambda x: os.path.getmtime(x))
        print(f"📁 使用数据文件: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def query_country(self, tag: str) -> Optional[Dict]:
        """查询特定国家"""
        if not self.data:
            return None
        
        tag = tag.upper()
        if tag in self.data['countries']:
            return self.data['countries'][tag]
        return None
    
    def display_country(self, tag: str, info: Dict):
        """显示单个国家信息"""
        status = "🟢 活跃" if info['active'] else "🔴 已灭亡"
        civ = "🏛️ 文明化" if info['civilized'] else "🏺 未文明化"
        
        print(f"\n国家代码: {tag}")
        print(f"国家名称: {info['name']}")
        print(f"首都省份: {info['capital']}")
        print(f"主要文化: {info['culture'] or '未知'}")
        print(f"文明状态: {civ}")
        print(f"活跃状态: {status}")
    
    def display_all_countries(self):
        """显示所有国家的简表"""
        if not self.data:
            return
        
        print(f"\n📊 维多利亚2存档国家信息 - {self.data['metadata']['source_file']}")
        print(f"总计: {self.data['metadata']['total_countries']} 个国家")
        print(f"活跃: {self.data['metadata']['active_countries']} 个国家")
        print("=" * 80)
        
        countries = self.data['countries']
        for tag, info in countries.items():
            status_icon = "🟢" if info['active'] else "🔴"
            civ_icon = "🏛️" if info['civilized'] else "🏺"
            name = info['name'] or tag
            
            print(f"{status_icon}{civ_icon} {tag:3} - {name:20} (首都: {info['capital'] or 'N/A':4})")
    
    def display_active_countries(self):
        """显示活跃国家"""
        if not self.data:
            return
        
        print(f"\n🟢 活跃国家 ({self.data['metadata']['active_countries']} 个):")
        print("=" * 60)
        
        active_countries = {tag: info for tag, info in self.data['countries'].items() if info['active']}
        
        # 按文明化状态分组
        civilized = [(tag, info) for tag, info in active_countries.items() if info['civilized']]
        uncivilized = [(tag, info) for tag, info in active_countries.items() if not info['civilized']]
        
        print(f"\n🏛️ 文明化国家 ({len(civilized)} 个):")
        for tag, info in sorted(civilized, key=lambda x: x[1]['name'] or x[0]):
            name = info['name'] or tag
            print(f"   {tag:3} - {name:20} (首都: {info['capital'] or 'N/A':4})")
        
        print(f"\n🏺 未文明化国家 ({len(uncivilized)} 个):")
        for tag, info in sorted(uncivilized, key=lambda x: x[1]['name'] or x[0]):
            name = info['name'] or tag
            print(f"   {tag:3} - {name:20} (首都: {info['capital'] or 'N/A':4})")
    
    def display_codes_only(self):
        """仅显示国家代码"""
        if not self.data:
            return
        
        print(f"\n📋 所有国家代码 ({self.data['metadata']['total_countries']} 个):")
        print("=" * 60)
        
        codes = self.data['country_codes']
        for i, code in enumerate(codes):
            print(f"{code:3}", end="  ")
            if (i + 1) % 10 == 0:
                print()  # 每10个换行
        print()
        
        print(f"\n🟢 活跃国家代码 ({self.data['metadata']['active_countries']} 个):")
        print("=" * 60)
        
        active_codes = self.data['active_country_codes']
        for i, code in enumerate(active_codes):
            print(f"{code:3}", end="  ")
            if (i + 1) % 10 == 0:
                print()  # 每10个换行
        print()
    
    def search_by_name(self, name: str):
        """按名称搜索国家"""
        if not self.data:
            return
        
        name = name.lower()
        matches = []
        
        for tag, info in self.data['countries'].items():
            country_name = (info['name'] or tag).lower()
            if name in country_name or country_name in name:
                matches.append((tag, info))
        
        if matches:
            print(f"\n🔍 搜索结果 (关键词: '{name}'):")
            print("=" * 60)
            for tag, info in matches:
                self.display_country(tag, info)
        else:
            print(f"❌ 未找到包含 '{name}' 的国家")

def main():
    """主函数"""
    query = CountryQuery()
    if not query.data:
        return
    
    if len(sys.argv) == 1:
        # 无参数 - 显示所有国家
        query.display_all_countries()
    
    elif len(sys.argv) == 2:
        arg = sys.argv[1].lower()
        
        if arg == 'active':
            # 显示活跃国家
            query.display_active_countries()
        
        elif arg == 'codes':
            # 显示所有代码
            query.display_codes_only()
        
        elif arg == 'help' or arg == '-h':
            # 显示帮助
            print("""
维多利亚2国家查询工具使用方法：

python country_query.py              - 显示所有国家
python country_query.py active       - 显示活跃国家
python country_query.py codes        - 显示所有国家代码
python country_query.py CHI          - 查询特定国家 (CHI)
python country_query.py China        - 按名称搜索国家

示例：
python country_query.py CHI          # 查看中国信息
python country_query.py active       # 查看所有活跃国家
python country_query.py German       # 搜索包含German的国家
            """)
        
        elif len(arg) <= 4 and arg.isalpha():
            # 可能是国家代码 - 先尝试精确匹配
            result = query.query_country(arg)
            if result:
                query.display_country(arg.upper(), result)
            else:
                # 如果精确匹配失败，则按名称搜索
                print(f"❌ 未找到国家代码: {arg.upper()}，尝试按名称搜索...")
                query.search_by_name(arg)

if __name__ == "__main__":
    print("=" * 80)
    print("🏛️  维多利亚2国家查询工具")
    print("   Victoria II Country Query Tool")
    print("=" * 80)
    main()
