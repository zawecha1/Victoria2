#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国家-省份结构比较诊断工具
检查重分配前后的国家结构差异
"""

import re
import os
import json
from typing import Dict, List, Set

class CountryProvinceAnalyzer:
    """国家省份结构分析器"""
    
    def __init__(self, filename: str):
        self.filename = filename
        if not os.path.exists(filename):
            raise FileNotFoundError(f"文件不存在: {filename}")
        
        with open(filename, 'r', encoding='latin1') as f:
            self.content = f.read()
    
    def extract_country_data(self) -> Dict[str, Dict]:
        """提取所有国家的详细数据"""
        print(f"🔍 分析文件: {self.filename}")
        
        # 查找所有国家块
        country_pattern = re.compile(r'^([A-Z]{2,3})=\s*{', re.MULTILINE)
        country_matches = list(country_pattern.finditer(self.content))
        
        countries_data = {}
        
        for i, match in enumerate(country_matches):
            country_tag = match.group(1)
            start_pos = match.end()
            
            # 确定国家块的结束位置
            if i + 1 < len(country_matches):
                end_pos = country_matches[i + 1].start()
            else:
                # 查找下一个主要section
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+100000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = len(self.content)
            
            country_content = self.content[start_pos:end_pos]
            
            # 提取国家信息
            country_info = {
                'tag': country_tag,
                'capital': None,
                'provinces': [],
                'technologies': [],
                'diplomacy': {},
                'government': None,
                'civilized': None,
                'prestige': None,
                'badboy': None,
                'money': None,
                'content_length': len(country_content),
                'has_politics_block': False,
                'has_upper_house': False,
                'has_ruling_party': False
            }
            
            # 查找首都
            capital_match = re.search(r'capital=(\d+)', country_content)
            if capital_match:
                country_info['capital'] = int(capital_match.group(1))
            
            # 查找文明化状态
            civilized_match = re.search(r'civilized=([^\s\n}]+)', country_content)
            if civilized_match:
                country_info['civilized'] = civilized_match.group(1).strip('"')
            
            # 查找政府类型
            government_match = re.search(r'government=([^\s\n}]+)', country_content)
            if government_match:
                country_info['government'] = government_match.group(1).strip('"')
            
            # 查找威望
            prestige_match = re.search(r'prestige=([0-9.-]+)', country_content)
            if prestige_match:
                try:
                    country_info['prestige'] = float(prestige_match.group(1))
                except ValueError:
                    country_info['prestige'] = None
            
            # 查找恶名
            badboy_match = re.search(r'badboy=([0-9.-]+)', country_content)
            if badboy_match:
                try:
                    country_info['badboy'] = float(badboy_match.group(1))
                except ValueError:
                    country_info['badboy'] = None
            
            # 查找金钱
            money_match = re.search(r'money=([0-9.-]+)', country_content)
            if money_match:
                try:
                    # 处理可能包含多个数字的情况
                    money_str = money_match.group(1)
                    if money_str.count('.') > 1:
                        # 如果有多个小数点，取第一个完整数字
                        money_str = money_str.split('.')[0] + '.' + money_str.split('.')[1]
                    country_info['money'] = float(money_str)
                except ValueError:
                    country_info['money'] = None
            
            # 检查政治结构
            if 'politics=' in country_content:
                country_info['has_politics_block'] = True
            
            if 'upper_house=' in country_content:
                country_info['has_upper_house'] = True
                
            if 'ruling_party=' in country_content:
                country_info['has_ruling_party'] = True
            
            # 查找科技
            tech_matches = re.findall(r'([a-z_]+)=([0-9.]+)', country_content)
            for tech_name, tech_level in tech_matches:
                if tech_name not in ['capital', 'prestige', 'badboy', 'money'] and '.' in tech_level:
                    try:
                        # 确保科技级别是有效的数字
                        level_value = float(tech_level)
                        if 0 <= level_value <= 10:  # 合理的科技级别范围
                            country_info['technologies'].append({
                                'name': tech_name,
                                'level': level_value
                            })
                    except ValueError:
                        continue
            
            countries_data[country_tag] = country_info
        
        print(f"✅ 提取了 {len(countries_data)} 个国家的数据")
        return countries_data
    
    def extract_province_ownership(self) -> Dict[int, Dict]:
        """提取所有省份的归属信息"""
        print(f"🏛️ 分析省份归属...")
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        provinces_data = {}
        
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 确定省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+20000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 10000
            
            province_content = self.content[start_pos:end_pos]
            
            # 提取省份信息
            province_info = {
                'id': province_id,
                'name': 'Unknown',
                'owner': None,
                'controller': None,
                'cores': [],
                'population': 0,
                'base_tax': 0,
                'has_fort': False,
                'has_naval_base': False
            }
            
            # 查找省份名称
            name_match = re.search(r'name="([^"]+)"', province_content)
            if name_match:
                province_info['name'] = name_match.group(1)
            
            # 查找拥有者
            owner_match = re.search(r'owner="?([A-Z]{2,3})"?', province_content)
            if owner_match:
                province_info['owner'] = owner_match.group(1)
            
            # 查找控制者
            controller_match = re.search(r'controller="?([A-Z]{2,3})"?', province_content)
            if controller_match:
                province_info['controller'] = controller_match.group(1)
            
            # 查找核心声明
            core_matches = re.findall(r'core="?([A-Z]{2,3})"?', province_content)
            province_info['cores'] = core_matches
            
            # 检查建筑
            if 'fort=' in province_content:
                province_info['has_fort'] = True
            if 'naval_base=' in province_content:
                province_info['has_naval_base'] = True
            
            provinces_data[province_id] = province_info
            
            if (i + 1) % 1000 == 0:
                print(f"  进度: {i + 1}/{len(province_matches)}")
        
        print(f"✅ 分析了 {len(provinces_data)} 个省份")
        return provinces_data
    
    def analyze_country_province_mapping(self) -> Dict:
        """分析国家-省份映射关系"""
        countries_data = self.extract_country_data()
        provinces_data = self.extract_province_ownership()
        
        # 构建国家到省份的映射
        country_to_provinces = {}
        province_to_country = {}
        
        for province_id, province_info in provinces_data.items():
            owner = province_info['owner']
            if owner:
                if owner not in country_to_provinces:
                    country_to_provinces[owner] = []
                country_to_provinces[owner].append(province_id)
                province_to_country[province_id] = owner
        
        # 检查数据一致性
        inconsistencies = []
        
        for country_tag, country_info in countries_data.items():
            capital = country_info['capital']
            owned_provinces = country_to_provinces.get(country_tag, [])
            
            # 检查首都是否在拥有的省份中
            if capital and capital not in owned_provinces:
                inconsistencies.append({
                    'type': 'capital_not_owned',
                    'country': country_tag,
                    'capital': capital,
                    'owned_provinces': owned_provinces
                })
            
            # 检查省份数量
            country_info['actual_provinces'] = owned_provinces
            country_info['province_count'] = len(owned_provinces)
        
        return {
            'countries': countries_data,
            'provinces': provinces_data,
            'country_to_provinces': country_to_provinces,
            'province_to_country': province_to_country,
            'inconsistencies': inconsistencies
        }

def compare_files(file1: str, file2: str) -> Dict:
    """比较两个文件的国家-省份结构"""
    print("🔍 比较文件结构差异")
    print("=" * 50)
    
    try:
        print(f"📁 分析文件1: {file1}")
        analyzer1 = CountryProvinceAnalyzer(file1)
        data1 = analyzer1.analyze_country_province_mapping()
        
        print(f"📁 分析文件2: {file2}")
        analyzer2 = CountryProvinceAnalyzer(file2)
        data2 = analyzer2.analyze_country_province_mapping()
        
        comparison = {
            'file1': file1,
            'file2': file2,
            'summary': {
                'countries_file1': len(data1['countries']),
                'countries_file2': len(data2['countries']),
                'provinces_file1': len(data1['provinces']),
                'provinces_file2': len(data2['provinces'])
            },
            'differences': {
                'ownership_changes': [],
                'new_owners': [],
                'lost_owners': [],
                'capital_issues': [],
                'structure_issues': []
            }
        }
        
        # 比较省份归属变化
        all_provinces = set(data1['provinces'].keys()) | set(data2['provinces'].keys())
        
        for province_id in all_provinces:
            prov1 = data1['provinces'].get(province_id, {})
            prov2 = data2['provinces'].get(province_id, {})
            
            owner1 = prov1.get('owner')
            owner2 = prov2.get('owner')
            
            if owner1 != owner2:
                comparison['differences']['ownership_changes'].append({
                    'province_id': province_id,
                    'province_name': prov1.get('name', prov2.get('name', 'Unknown')),
                    'old_owner': owner1,
                    'new_owner': owner2
                })
        
        # 比较国家结构
        all_countries = set(data1['countries'].keys()) | set(data2['countries'].keys())
        
        for country_tag in all_countries:
            country1 = data1['countries'].get(country_tag, {})
            country2 = data2['countries'].get(country_tag, {})
            
            provinces1 = country1.get('actual_provinces', [])
            provinces2 = country2.get('actual_provinces', [])
            
            if len(provinces1) != len(provinces2):
                comparison['differences']['structure_issues'].append({
                    'country': country_tag,
                    'provinces_before': len(provinces1),
                    'provinces_after': len(provinces2),
                    'difference': len(provinces2) - len(provinces1),
                    'capital_before': country1.get('capital'),
                    'capital_after': country2.get('capital')
                })
        
        # 检查数据一致性问题
        for inconsistency in data2['inconsistencies']:
            comparison['differences']['capital_issues'].append(inconsistency)
        
        return comparison
        
    except Exception as e:
        print(f"❌ 比较失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def diagnose_redistribution_problems():
    """诊断重分配问题"""
    print("🔬 重分配问题诊断")
    print("=" * 40)
    
    # 检查文件
    files = {
        'working': 'China1837_07_15.v2',
        'broken': 'autosave.v2'
    }
    
    for label, filename in files.items():
        if not os.path.exists(filename):
            print(f"❌ 文件不存在: {filename}")
            return
        else:
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            print(f"✅ {label.upper()}: {filename} ({size_mb:.1f} MB)")
    
    # 执行比较
    comparison = compare_files(files['working'], files['broken'])
    
    if not comparison:
        return
    
    print("\n📊 比较结果摘要:")
    print(f"   正常文件国家数: {comparison['summary']['countries_file1']}")
    print(f"   问题文件国家数: {comparison['summary']['countries_file2']}")
    print(f"   正常文件省份数: {comparison['summary']['provinces_file1']}")
    print(f"   问题文件省份数: {comparison['summary']['provinces_file2']}")
    
    # 显示归属变化
    ownership_changes = comparison['differences']['ownership_changes']
    print(f"\n🔄 省份归属变化: {len(ownership_changes)} 个")
    
    if ownership_changes:
        print("前20个变化:")
        for i, change in enumerate(ownership_changes[:20], 1):
            print(f"   {i:2d}. {change['province_name']} ({change['province_id']}): {change['old_owner']} -> {change['new_owner']}")
        
        if len(ownership_changes) > 20:
            print(f"   ... 还有 {len(ownership_changes) - 20} 个变化")
    
    # 显示结构问题
    structure_issues = comparison['differences']['structure_issues']
    print(f"\n🏗️ 国家结构变化: {len(structure_issues)} 个")
    
    if structure_issues:
        print("主要变化:")
        for issue in structure_issues[:10]:
            print(f"   {issue['country']}: {issue['provinces_before']} -> {issue['provinces_after']} 省份 (差异: {issue['difference']:+d})")
    
    # 显示首都问题
    capital_issues = comparison['differences']['capital_issues']
    print(f"\n🏛️ 首都一致性问题: {len(capital_issues)} 个")
    
    if capital_issues:
        for issue in capital_issues[:5]:
            print(f"   {issue['country']}: 首都 {issue['capital']} 不在拥有省份中")
    
    # 保存详细报告
    report_filename = f"country_structure_comparison_report.json"
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, ensure_ascii=False, indent=2)
        print(f"\n📋 详细报告已保存: {report_filename}")
    except Exception as e:
        print(f"⚠️ 保存报告失败: {e}")
    
    return comparison

def main():
    """主函数"""
    print("🔍 Victoria II 国家-省份结构诊断工具")
    print("=" * 50)
    
    result = diagnose_redistribution_problems()
    
    if result:
        print("\n💡 问题分析建议:")
        
        ownership_changes = result['differences']['ownership_changes']
        china_gains = sum(1 for change in ownership_changes if change['new_owner'] == 'CHI')
        
        if china_gains > 1000:
            print(f"   ⚠️ 中国获得了 {china_gains} 个省份，这可能导致:")
            print(f"      • 游戏性能问题")
            print(f"      • 存档结构不稳定")
            print(f"      • 经济/人口计算错误")
        
        capital_issues = result['differences']['capital_issues']
        if capital_issues:
            print(f"   ❌ 发现 {len(capital_issues)} 个首都一致性问题")
            print(f"      这可能是导致游戏崩溃的主要原因")
        
        structure_issues = result['differences']['structure_issues']
        extreme_changes = [issue for issue in structure_issues if abs(issue['difference']) > 50]
        if extreme_changes:
            print(f"   ⚠️ 发现 {len(extreme_changes)} 个国家有极端省份变化")
            print(f"      这可能影响游戏稳定性")

if __name__ == "__main__":
    main()
