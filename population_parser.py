#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 人口统计专用解析器
专门用于提取和分析各国人口信息
"""

import re
import json
import time
from typing import Dict, List, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class PopulationData:
    """人口数据"""
    size: int = 0
    type: str = ""
    culture: str = ""
    religion: str = ""
    location: str = ""
    literacy: float = 0.0
    militancy: float = 0.0
    consciousness: float = 0.0


@dataclass
class ProvincePopulation:
    """省份人口数据"""
    id: int = 0
    name: str = ""
    owner: str = ""
    total_population: int = 0
    pop_groups: List[PopulationData] = field(default_factory=list)


@dataclass
class CountryPopulation:
    """国家人口数据"""
    tag: str = ""
    name: str = ""
    total_population: int = 0
    provinces: List[ProvincePopulation] = field(default_factory=list)
    population_by_culture: Dict[str, int] = field(default_factory=dict)
    population_by_religion: Dict[str, int] = field(default_factory=dict)
    population_by_type: Dict[str, int] = field(default_factory=dict)
    literacy_rate: float = 0.0
    research_points: float = 0.0
    tax_base: float = 0.0


class PopulationParser:
    """人口专用解析器"""
    
    def __init__(self):
        self.content = ""
        # 预编译正则表达式
        self.country_pattern = re.compile(r'^([A-Z]{3})=\s*{', re.MULTILINE)
        self.province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        
    def parse_file(self, filename: str) -> Dict[str, CountryPopulation]:
        """解析存档文件中的人口信息"""
        print(f"开始解析人口数据: {filename}")
        start_time = time.time()
        
        # 读取文件
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                self.content = f.read()
            print(f"文件读取完成，大小: {len(self.content):,} 字符")
        except Exception as e:
            print(f"文件读取失败: {e}")
            return {}
        
        # 提取所有国家的人口信息
        countries_population = self._extract_all_countries_population()
        
        elapsed = time.time() - start_time
        print(f"人口解析完成! 耗时: {elapsed:.2f}秒")
        
        return countries_population
    
    def _extract_all_countries_population(self) -> Dict[str, CountryPopulation]:
        """提取所有国家的人口信息"""
        print("开始提取国家人口信息...")
        
        # 首先提取所有省份的所有者信息
        print("构建省份-国家映射...")
        province_owners = self._build_province_owner_mapping()
        print(f"找到 {len(province_owners)} 个省份")
        
        # 然后提取每个省份的人口数据
        print("提取省份人口数据...")
        provinces_data = self._extract_all_provinces_population()
        print(f"成功解析 {len(provinces_data)} 个省份的人口数据")
        
        # 按国家聚合人口数据
        print("按国家聚合人口数据...")
        countries_population = self._aggregate_population_by_country(provinces_data, province_owners)
        
        # 添加国家的基本信息
        print("添加国家基本信息...")
        self._add_country_basic_info(countries_population)
        
        print(f"最终统计: {len(countries_population)} 个国家有人口数据")
        
        return countries_population
    
    def _build_province_owner_mapping(self) -> Dict[int, str]:
        """构建省份ID到所有者国家的映射"""
        province_owners = {}
        
        # 在存档中查找所有省份的owner信息
        province_matches = list(self.province_pattern.finditer(self.content))
        
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 找到省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                # 查找下一个主要块的开始
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+10000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 5000
            
            province_content = self.content[start_pos:end_pos]
            
            # 提取owner信息
            owner_match = re.search(r'owner="?([A-Z]{3})"?', province_content)
            if owner_match:
                province_owners[province_id] = owner_match.group(1)
            
            # 进度显示
            if (i + 1) % 500 == 0:
                print(f"已处理 {i + 1}/{len(province_matches)} 个省份映射...")
        
        return province_owners
    
    def _extract_all_provinces_population(self) -> Dict[int, ProvincePopulation]:
        """提取所有省份的人口数据"""
        provinces_data = {}
        province_matches = list(self.province_pattern.finditer(self.content))
        
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 找到省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+10000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 5000
            
            province_content = self.content[start_pos:end_pos]
            
            # 解析省份人口数据
            province_pop = self._parse_province_population(province_id, province_content)
            if province_pop and province_pop.total_population > 0:
                provinces_data[province_id] = province_pop
            
            # 进度显示
            if (i + 1) % 500 == 0:
                print(f"已处理 {i + 1}/{len(province_matches)} 个省份人口...")
        
        return provinces_data
    
    def _parse_province_population(self, province_id: int, content: str) -> ProvincePopulation:
        """解析单个省份的人口数据"""
        province_pop = ProvincePopulation()
        province_pop.id = province_id
        
        # 提取省份基本信息
        name_match = re.search(r'name="([^"]+)"', content)
        if name_match:
            province_pop.name = name_match.group(1)
        
        owner_match = re.search(r'owner="?([A-Z]{3})"?', content)
        if owner_match:
            province_pop.owner = owner_match.group(1)
        
        # 查找所有职业人口群体（aristocrats, clergymen, craftsmen等）
        # 使用新的模式匹配真实的人口数据
        pop_type_pattern = r'(\w+)=\s*\{\s*id=\d+\s*size=(\d+)\s*([^=]+?)=([^=\s]+)\s*money=([\d.]+)'
        pop_matches = re.finditer(pop_type_pattern, content, re.DOTALL)
        
        total_pop = 0
        for pop_match in pop_matches:
            pop_type = pop_match.group(1)
            size = int(pop_match.group(2))
            culture_religion = pop_match.group(3).strip()
            religion = pop_match.group(4).strip()
            
            # 解析文化和宗教（格式：culture=religion）
            if '=' in culture_religion:
                culture = culture_religion.strip()
            else:
                culture = culture_religion.strip()
            
            pop_data = PopulationData()
            pop_data.size = size
            pop_data.type = pop_type
            pop_data.culture = culture
            pop_data.religion = religion
            
            province_pop.pop_groups.append(pop_data)
            total_pop += size
        
        province_pop.total_population = total_pop
        return province_pop
    
    def _parse_single_pop(self, content: str) -> PopulationData:
        """解析单个人口组的数据（保留用于向后兼容）"""
        # 这个函数现在被整合到 _parse_province_population 中
        # 保留此函数以防需要
        return PopulationData()
    
    def _aggregate_population_by_country(self, provinces_data: Dict[int, ProvincePopulation], 
                                       province_owners: Dict[int, str]) -> Dict[str, CountryPopulation]:
        """按国家聚合人口数据"""
        countries_population = defaultdict(lambda: CountryPopulation())
        
        for province_id, province_pop in provinces_data.items():
            owner = province_owners.get(province_id, province_pop.owner)
            if not owner:
                continue
            
            country_pop = countries_population[owner]
            country_pop.tag = owner
            country_pop.total_population += province_pop.total_population
            country_pop.provinces.append(province_pop)
            
            # 统计文化、宗教、职业分布
            for pop_group in province_pop.pop_groups:
                # 按文化统计
                if pop_group.culture:
                    country_pop.population_by_culture[pop_group.culture] = \
                        country_pop.population_by_culture.get(pop_group.culture, 0) + pop_group.size
                
                # 按宗教统计
                if pop_group.religion:
                    country_pop.population_by_religion[pop_group.religion] = \
                        country_pop.population_by_religion.get(pop_group.religion, 0) + pop_group.size
                
                # 按职业统计
                if pop_group.type:
                    country_pop.population_by_type[pop_group.type] = \
                        country_pop.population_by_type.get(pop_group.type, 0) + pop_group.size
        
        # 计算识字率
        for country_pop in countries_population.values():
            total_literate = sum(
                pop_group.size * pop_group.literacy
                for province in country_pop.provinces
                for pop_group in province.pop_groups
                if pop_group.literacy > 0
            )
            if country_pop.total_population > 0:
                country_pop.literacy_rate = total_literate / country_pop.total_population
        
        return dict(countries_population)
    
    def _add_country_basic_info(self, countries_population: Dict[str, CountryPopulation]):
        """添加国家基本信息（研究点数、税收等）"""
        country_matches = list(self.country_pattern.finditer(self.content))
        
        for match in country_matches:
            tag = match.group(1)
            if tag not in countries_population:
                continue
            
            start_pos = match.end()
            end_pos = self.content.find('\n}', start_pos)
            if end_pos == -1:
                continue
            
            country_content = self.content[start_pos:end_pos]
            
            # 提取研究点数
            research_match = re.search(r'research_points=([\d.]+)', country_content)
            if research_match:
                countries_population[tag].research_points = float(research_match.group(1))
            
            # 提取税收基础
            tax_match = re.search(r'tax_base=([\d.]+)', country_content)
            if tax_match:
                countries_population[tag].tax_base = float(tax_match.group(1))
    
    def save_population_data(self, countries_population: Dict[str, CountryPopulation], filename: str = "population_analysis.json"):
        """保存人口数据到JSON文件"""
        print(f"保存人口数据到 {filename}...")
        
        # 转换为可序列化的格式
        serializable_data = {}
        for tag, country_pop in countries_population.items():
            serializable_data[tag] = {
                'tag': country_pop.tag,
                'total_population': country_pop.total_population,
                'province_count': len(country_pop.provinces),
                'population_by_culture': country_pop.population_by_culture,
                'population_by_religion': country_pop.population_by_religion,
                'population_by_type': country_pop.population_by_type,
                'literacy_rate': round(country_pop.literacy_rate * 100, 2),
                'research_points': country_pop.research_points,
                'tax_base': country_pop.tax_base
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        print(f"人口数据已保存到 {filename}")
    
    def print_population_summary(self, countries_population: Dict[str, CountryPopulation]):
        """打印人口统计摘要"""
        if not countries_population:
            print("没有找到人口数据")
            return
        
        # 按人口数量排序
        sorted_countries = sorted(countries_population.items(), 
                                key=lambda x: x[1].total_population, reverse=True)
        
        print("\n" + "="*80)
        print("🌍 Victoria II 全球人口统计报告")
        print("="*80)
        
        total_world_population = sum(country.total_population for country in countries_population.values())
        print(f"📊 全球总人口: {total_world_population:,}")
        print(f"📈 统计国家: {len(countries_population)} 个")
        
        print("\n🏆 人口排名前20的国家:")
        print("排名   国家   人口数量         占世界%   研究点数    税收基础    识字率%")
        print("-" * 75)
        
        for i, (tag, country) in enumerate(sorted_countries[:20], 1):
            pop_percentage = (country.total_population / total_world_population * 100) if total_world_population > 0 else 0
            print(f"{i:2d}   {tag:3s}  {country.total_population:>10,}  {pop_percentage:>8.1f}  "
                  f"{country.research_points:>9.0f}  {country.tax_base:>9.1f}  {country.literacy_rate*100:>7.1f}")
        
        # 玩家国家特别分析
        player_countries = [tag for tag in ['CHI', 'ENG', 'FRA', 'GER', 'RUS', 'USA', 'JAP'] 
                          if tag in countries_population]
        
        if player_countries:
            print(f"\n🎮 主要国家人口对比:")
            print("国家   人口数量         全球排名   识字率%   主要文化")
            print("-" * 65)
            
            for tag in player_countries:
                country = countries_population[tag]
                rank = next(i for i, (t, _) in enumerate(sorted_countries, 1) if t == tag)
                main_culture = max(country.population_by_culture.items(), key=lambda x: x[1])[0] \
                             if country.population_by_culture else "未知"
                
                print(f"{tag:3s}  {country.total_population:>10,}  {rank:>8d}    "
                      f"{country.literacy_rate*100:>7.1f}   {main_culture}")
        
        print("\n" + "="*80)
        print("✅ 人口统计分析完成!")
        print("="*80)


def main():
    """主函数"""
    parser = PopulationParser()
    
    # 解析人口数据
    countries_population = parser.parse_file("China2245_04_06.v2")
    
    if countries_population:
        # 打印统计摘要
        parser.print_population_summary(countries_population)
        
        # 保存详细数据
        parser.save_population_data(countries_population)
    else:
        print("人口数据解析失败")


if __name__ == "__main__":
    main()
