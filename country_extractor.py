#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
维多利亚2存档国家信息提取器
Extract all country codes and names from Victoria II save files
Based on the country-finding code from victoria2_main_modifier.py
"""

import re
import json
import os
import glob
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class Victoria2CountryExtractor:
    def __init__(self, file_path: str):
        """初始化国家提取器"""
        self.file_path = file_path
        self.content = ""
        self.countries = {}
        
    def load_file(self) -> bool:
        """加载存档文件"""
        try:
            print(f"📁 正在加载文件: {os.path.basename(self.file_path)}")
            with open(self.file_path, 'r', encoding='latin1') as f:
                self.content = f.read()
            print(f"✅ 文件加载成功，大小: {len(self.content):,} 字符")
            return True
        except Exception as e:
            print(f"❌ 文件加载失败: {e}")
            return False
    
    def extract_country_data(self) -> Dict:
        """提取所有国家信息
        
        基于victoria2_main_modifier.py中的国家查找逻辑
        """
        print("🔍 开始提取国家信息...")
        
        # 查找所有国家块（基于victoria2_main_modifier.py的模式）
        country_pattern = re.compile(r'^([A-Z]{2,3})=\s*{', re.MULTILINE)
        country_matches = list(country_pattern.finditer(self.content))
        
        print(f"📊 找到 {len(country_matches)} 个潜在国家块")
        
        countries_data = {}
        
        for i, match in enumerate(country_matches):
            country_tag = match.group(1)
            start_pos = match.end()
            
            # 确定国家块的结束位置
            if i + 1 < len(country_matches):
                end_pos = country_matches[i + 1].start()
            else:
                # 查找下一个主要部分
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+50000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 30000
            
            country_content = self.content[start_pos:end_pos]
            
            # 提取国家基本信息
            country_info = self.parse_country_block(country_tag, country_content)
            
            if country_info:
                countries_data[country_tag] = country_info
                
        print(f"✅ 成功解析 {len(countries_data)} 个国家")
        return countries_data
    
    def parse_country_block(self, tag: str, content: str) -> Optional[Dict]:
        """解析单个国家块的详细信息"""
        country_info = {
            'tag': tag,
            'name': None,  # 将在后面根据文化智能确定
            'capital': None,
            'government': None,
            'primary_culture': None,
            'technology_school': None,
            'civilized': None,
            'prestige': None,
            'badboy': None,
            'money': None,
            'last_election': None,
            'established': None
        }
        
        # 查找首都
        capital_match = re.search(r'capital=(\d+)', content)
        if capital_match:
            country_info['capital'] = int(capital_match.group(1))
        
        # 查找政府类型
        gov_match = re.search(r'government="?([^"\n]+)"?', content)
        if gov_match:
            country_info['government'] = gov_match.group(1).strip()
        
        # 查找主要文化
        culture_match = re.search(r'primary_culture="?([^"\n]+)"?', content)
        if culture_match:
            country_info['primary_culture'] = culture_match.group(1).strip()
        
        # 查找技术学派
        tech_match = re.search(r'technology_school="?([^"\n]+)"?', content)
        if tech_match:
            country_info['technology_school'] = tech_match.group(1).strip()
        
        # 查找文明化状态
        civilized_match = re.search(r'civilized="?([^"\n]+)"?', content)
        if civilized_match:
            country_info['civilized'] = civilized_match.group(1).strip() == 'yes'
        
        # 查找威望
        prestige_match = re.search(r'prestige=([\d.-]+)', content)
        if prestige_match:
            try:
                country_info['prestige'] = float(prestige_match.group(1))
            except ValueError:
                pass
        
        # 查找恶名度
        badboy_match = re.search(r'badboy=([\d.-]+)', content)
        if badboy_match:
            try:
                country_info['badboy'] = float(badboy_match.group(1))
            except ValueError:
                pass
        
        # 查找金钱
        money_match = re.search(r'money=([\d.-]+)', content)
        if money_match:
            try:
                country_info['money'] = float(money_match.group(1))
            except ValueError:
                pass
        
        # 查找上次选举
        election_match = re.search(r'last_election="?([^"\n]+)"?', content)
        if election_match:
            country_info['last_election'] = election_match.group(1).strip()
        
        # 根据文化智能确定国家名称
        country_info['name'] = self.get_smart_country_name(tag, country_info['primary_culture'])
        
        return country_info
    
    def get_smart_country_name(self, tag: str, culture: str) -> str:
        """根据标签和文化智能确定国家名称"""
        # 特殊处理CHI标签，根据文化判断是中国还是智利
        if tag == 'CHI':
            chinese_cultures = ['beifaren', 'nanfaren', 'manchu']
            if culture in chinese_cultures:
                return 'China'
            else:
                return 'Chile'
        
        # 使用原有的名称映射
        return self.get_country_display_name(tag)
    
    def get_country_display_name(self, tag: str) -> str:
        """获取国家的显示名称
        
        注意：实际上这个函数应该根据文化来判断真正的国家身份
        CHI在游戏中可能是中国或智利，需要根据文化判断
        """
        # 常见国家名称映射
        country_names = {
            'CHI': 'China/Chile',  # 需要根据文化判断
            'JAP': 'Japan',
            'RUS': 'Russia',
            'GBR': 'Great Britain',
            'ENG': 'England',
            'FRA': 'France',
            'GER': 'Germany',
            'AUS': 'Austria',
            'USA': 'United States',
            'CSA': 'Confederate States',
            'PRU': 'Prussia',
            'SPA': 'Spain',
            'POR': 'Portugal',
            'ITA': 'Italy',
            'SAR': 'Sardinia-Piedmont',
            'TUR': 'Ottoman Empire',
            'EGY': 'Egypt',
            'PER': 'Persia',
            'ETH': 'Ethiopia',
            'MAR': 'Morocco',
            'TUN': 'Tunisia',
            'SIA': 'Siam',
            'BUR': 'Burma',
            'KOR': 'Korea',
            'DAI': 'Dai Nam',
            'ARG': 'Argentina',
            'BRA': 'Brazil',
            'MEX': 'Mexico',
            'COL': 'Colombia',
            'VEN': 'Venezuela',
            'PEU': 'Peru',
            'BOL': 'Bolivia',
            'CHL': 'Chile',
            'ECU': 'Ecuador',
            'URU': 'Uruguay',
            'PAR': 'Paraguay',
            'HAW': 'Hawaii',
            'TEX': 'Texas',
            'CAL': 'California',
            'CAN': 'Canada',
            'QUE': 'Quebec',
            'NET': 'Netherlands',
            'BEL': 'Belgium',
            'SWE': 'Sweden',
            'NOR': 'Norway',
            'DEN': 'Denmark',
            'SWI': 'Switzerland',
            'BAV': 'Bavaria',
            'WUR': 'Württemberg',
            'HAN': 'Hannover',
            'SAX': 'Saxony',
            'HES': 'Hesse-Darmstadt',
            'OLD': 'Oldenburg',
            'MEC': 'Mecklenburg',
            'HOL': 'Holstein',
            'POL': 'Poland',
            'CRA': 'Cracow',
            'HUN': 'Hungary',
            'WAL': 'Wallachia',
            'MOL': 'Moldavia',
            'SER': 'Serbia',
            'MON': 'Montenegro',
            'GRE': 'Greece',
            'ION': 'Ionian Islands',
            'ALB': 'Albania',
            'BUL': 'Bulgaria',
            'ROM': 'Romania',
            'YUG': 'Yugoslavia',
            'CZE': 'Czechoslovakia',
            'LIT': 'Lithuania',
            'LAT': 'Latvia',
            'EST': 'Estonia',
            'FIN': 'Finland',
            'UKR': 'Ukraine',
            'BYE': 'Belarus',
            'GEO': 'Georgia',
            'ARM': 'Armenia',
            'AZB': 'Azerbaijan',
            'KAZ': 'Kazakhstan',
            'UZB': 'Uzbekistan',
            'TUR': 'Turkmenistan',
            'KYR': 'Kyrgyzstan',
            'TAJ': 'Tajikistan',
            'AFG': 'Afghanistan',
            'BEL': 'Baluchistan',
            'PAN': 'Punjab',
            'SIN': 'Sindh',
            'KAS': 'Kashmir',
            'ORI': 'Orissa',
            'ASS': 'Assam',
            'BEN': 'Bengal',
            'MYS': 'Mysore',
            'HYD': 'Hyderabad',
            'TRA': 'Travancore',
            'KAL': 'Kalat',
            'MAK': 'Makran',
            'CEY': 'Ceylon',
        }
        
        return country_names.get(tag, tag)
    
    def find_active_countries(self, countries_data: Dict) -> List[str]:
        """查找拥有省份的活跃国家"""
        print("🔍 查找活跃国家（拥有省份的国家）...")
        
        # 查找所有省份的拥有者
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        active_countries = set()
        
        for i, match in enumerate(province_matches):
            start_pos = match.end()
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                end_pos = start_pos + 10000
            
            province_content = self.content[start_pos:end_pos]
            owner_match = re.search(r'owner="?([A-Z]{2,3})"?', province_content)
            if owner_match:
                owner = owner_match.group(1)
                if owner in countries_data:
                    active_countries.add(owner)
        
        print(f"✅ 找到 {len(active_countries)} 个活跃国家")
        return list(active_countries)
    
    def save_to_json(self, data: Dict, output_file: str = None) -> str:
        """保存数据到JSON文件"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            output_file = f"countries_{base_name}_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 数据已保存到: {output_file}")
            return output_file
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return ""
    
    def generate_report(self, countries_data: Dict, active_countries: List[str]) -> Dict:
        """生成详细报告"""
        report = {
            'metadata': {
                'source_file': os.path.basename(self.file_path),
                'extraction_time': datetime.now().isoformat(),
                'total_countries': len(countries_data),
                'active_countries': len(active_countries),
                'dead_countries': len(countries_data) - len(active_countries)
            },
            'countries': countries_data,
            'active_countries': active_countries,
            'dead_countries': [tag for tag in countries_data.keys() if tag not in active_countries]
        }
        
        # 统计信息
        civilized_count = sum(1 for c in countries_data.values() if c.get('civilized') == True)
        uncivilized_count = sum(1 for c in countries_data.values() if c.get('civilized') == False)
        
        report['statistics'] = {
            'civilized_countries': civilized_count,
            'uncivilized_countries': uncivilized_count,
            'unknown_civilization_status': len(countries_data) - civilized_count - uncivilized_count,
            'governments': self.count_governments(countries_data),
            'cultures': self.count_cultures(countries_data),
            'tech_schools': self.count_tech_schools(countries_data)
        }
        
        return report
    
    def count_governments(self, countries_data: Dict) -> Dict:
        """统计政府类型"""
        gov_count = {}
        for country in countries_data.values():
            gov = country.get('government', 'Unknown')
            gov_count[gov] = gov_count.get(gov, 0) + 1
        return dict(sorted(gov_count.items(), key=lambda x: x[1], reverse=True))
    
    def count_cultures(self, countries_data: Dict) -> Dict:
        """统计主要文化"""
        culture_count = {}
        for country in countries_data.values():
            culture = country.get('primary_culture', 'Unknown')
            culture_count[culture] = culture_count.get(culture, 0) + 1
        return dict(sorted(culture_count.items(), key=lambda x: x[1], reverse=True))
    
    def count_tech_schools(self, countries_data: Dict) -> Dict:
        """统计技术学派"""
        tech_count = {}
        for country in countries_data.values():
            tech = country.get('technology_school', 'Unknown')
            tech_count[tech] = tech_count.get(tech, 0) + 1
        return dict(sorted(tech_count.items(), key=lambda x: x[1], reverse=True))

def select_save_file() -> str:
    """选择存档文件"""
    print("📂 查找可用的存档文件...")
    
    # 查找所有.v2文件
    v2_files = glob.glob("*.v2")
    
    if not v2_files:
        print("❌ 未找到.v2存档文件")
        return ""
    
    print(f"✅ 找到 {len(v2_files)} 个存档文件:")
    for i, file in enumerate(v2_files, 1):
        size = os.path.getsize(file) / (1024 * 1024)  # MB
        modified = datetime.fromtimestamp(os.path.getmtime(file))
        print(f"  {i}. {file} ({size:.1f}MB, 修改时间: {modified.strftime('%Y-%m-%d %H:%M')})")
    
    # 自动选择最新的文件（按修改时间排序）
    v2_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    selected_file = v2_files[0]
    print(f"\n🎯 自动选择最新文件: {selected_file}")
    return selected_file

def main():
    """主函数"""
    print("=" * 60)
    print("🏛️  维多利亚2存档国家信息提取器")
    print("   Victoria II Save File Country Extractor")
    print("=" * 60)
    
    # 选择文件
    file_path = select_save_file()
    if not file_path:
        return
    
    # 创建提取器
    extractor = Victoria2CountryExtractor(file_path)
    
    # 加载文件
    if not extractor.load_file():
        return
    
    # 提取国家数据
    countries_data = extractor.extract_country_data()
    if not countries_data:
        print("❌ 未找到任何国家数据")
        return
    
    # 查找活跃国家
    active_countries = extractor.find_active_countries(countries_data)
    
    # 生成报告
    report = extractor.generate_report(countries_data, active_countries)
    
    # 显示摘要
    print("\n" + "=" * 60)
    print("📊 提取结果摘要:")
    print(f"   总国家数: {report['metadata']['total_countries']}")
    print(f"   活跃国家: {report['metadata']['active_countries']}")
    print(f"   已灭亡国家: {report['metadata']['dead_countries']}")
    print(f"   文明化国家: {report['statistics']['civilized_countries']}")
    print(f"   未文明化国家: {report['statistics']['uncivilized_countries']}")
    
    # 显示前10个活跃国家
    print(f"\n🌟 前10个活跃国家:")
    for i, tag in enumerate(active_countries[:10], 1):
        country = countries_data[tag]
        name = country['name']
        gov = country.get('government', 'Unknown')
        civilized = "文明化" if country.get('civilized') else "未文明化"
        print(f"   {i:2d}. {tag} - {name} ({gov}, {civilized})")
    
    # 保存数据
    output_file = extractor.save_to_json(report)
    
    print("=" * 60)
    print("✅ 提取完成！")
    print(f"📁 数据已保存到: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
