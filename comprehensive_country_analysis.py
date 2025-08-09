#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面国家分析工具 (comprehensive_country_analysis.py)
=================================================
分析Victoria II存档中的所有国家，包括有省份和没有省份的国家

功能:
1. 统计所有存在的国家
2. 统计有省份的国家
3. 统计没有省份的国家
4. 分析国家状态（存在但无领土、附庸国等）
"""

from victoria2_main_modifier import Victoria2Modifier
import re
import json
from datetime import datetime

class ComprehensiveCountryAnalyzer:
    def __init__(self, filename):
        self.modifier = Victoria2Modifier(filename, debug_mode=True)
        self.content = self.modifier.content
        
    def find_all_countries(self):
        """查找存档中所有存在的国家"""
        print("🔍 搜索所有国家...")
        
        # 查找所有国家块
        country_pattern = re.compile(r'^([A-Z]{2,3})=\s*{', re.MULTILINE)
        country_matches = list(country_pattern.finditer(self.content))
        
        all_countries = {}
        
        for i, match in enumerate(country_matches):
            country_tag = match.group(1)
            start_pos = match.end()
            
            # 确定国家块的结束位置
            if i + 1 < len(country_matches):
                end_pos = country_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+50000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 30000
            
            country_content = self.content[start_pos:end_pos]
            
            # 提取国家信息
            country_info = {
                'tag': country_tag,
                'exists': True,
                'civilized': False,
                'is_vassal': False,
                'overlord': None,
                'capital': None,
                'technology_school': None,
                'government': None,
                'primary_culture': None,
                'religion': None,
                'prestige': 0.0,
                'provinces_owned': 0
            }
            
            # 检查是否文明化
            if re.search(r'civilized=yes', country_content):
                country_info['civilized'] = True
            
            # 检查是否为附庸
            overlord_match = re.search(r'overlord="?([A-Z]{2,3})"?', country_content)
            if overlord_match:
                country_info['is_vassal'] = True
                country_info['overlord'] = overlord_match.group(1)
            
            # 查找首都
            capital_match = re.search(r'capital=(\d+)', country_content)
            if capital_match:
                country_info['capital'] = int(capital_match.group(1))
            
            # 查找技术学派
            tech_match = re.search(r'technology_school="?([^"\\n]+)"?', country_content)
            if tech_match:
                country_info['technology_school'] = tech_match.group(1)
            
            # 查找政府类型
            gov_match = re.search(r'government="?([^"\\n]+)"?', country_content)
            if gov_match:
                country_info['government'] = gov_match.group(1)
            
            # 查找主要文化
            culture_match = re.search(r'primary_culture="?([^"\\n]+)"?', country_content)
            if culture_match:
                country_info['primary_culture'] = culture_match.group(1)
            
            # 查找宗教
            religion_match = re.search(r'religion="?([^"\\n]+)"?', country_content)
            if religion_match:
                country_info['religion'] = religion_match.group(1)
            
            # 查找威望
            prestige_match = re.search(r'prestige=([\\d.-]+)', country_content)
            if prestige_match:
                try:
                    country_info['prestige'] = float(prestige_match.group(1))
                except:
                    pass
            
            all_countries[country_tag] = country_info
            
            # 显示进度
            if (i + 1) % 50 == 0:
                print(f"  处理进度: {i + 1}/{len(country_matches)} ({(i + 1)/len(country_matches)*100:.1f}%)")
        
        print(f"✅ 找到 {len(all_countries)} 个国家")
        return all_countries
    
    def analyze_provinces_by_owner(self):
        """分析省份归属"""
        print("🗺️ 分析省份归属...")
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        province_owners = {}
        
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
            
            # 查找拥有者
            owner_match = re.search(r'owner="?([A-Z]{2,3})"?', province_content)
            if owner_match:
                owner = owner_match.group(1)
                if owner not in province_owners:
                    province_owners[owner] = []
                province_owners[owner].append(province_id)
            
            # 显示进度
            if (i + 1) % 500 == 0:
                print(f"  处理进度: {i + 1}/{len(province_matches)} ({(i + 1)/len(province_matches)*100:.1f}%)")
        
        print(f"✅ 找到 {len(province_owners)} 个拥有省份的国家")
        return province_owners
    
    def generate_comprehensive_report(self):
        """生成全面分析报告"""
        print("📊 开始全面国家分析...")
        
        # 获取所有国家
        all_countries = self.find_all_countries()
        
        # 获取省份归属
        province_owners = self.analyze_provinces_by_owner()
        
        # 更新国家省份数量
        for country_tag in all_countries:
            if country_tag in province_owners:
                all_countries[country_tag]['provinces_owned'] = len(province_owners[country_tag])
        
        # 分类国家
        countries_with_provinces = {}
        countries_without_provinces = {}
        vassal_countries = {}
        civilized_countries = {}
        
        for tag, info in all_countries.items():
            if info['provinces_owned'] > 0:
                countries_with_provinces[tag] = info
            else:
                countries_without_provinces[tag] = info
            
            if info['is_vassal']:
                vassal_countries[tag] = info
            
            if info['civilized']:
                civilized_countries[tag] = info
        
        # 生成报告数据
        report_data = {
            'analysis_info': {
                'total_countries': len(all_countries),
                'countries_with_provinces': len(countries_with_provinces),
                'countries_without_provinces': len(countries_without_provinces),
                'vassal_countries': len(vassal_countries),
                'civilized_countries': len(civilized_countries),
                'analysis_date': datetime.now().isoformat(),
                'file_analyzed': getattr(self.modifier, 'current_filename', 'unknown')
            },
            'all_countries': all_countries,
            'countries_with_provinces': countries_with_provinces,
            'countries_without_provinces': countries_without_provinces,
            'vassal_countries': vassal_countries,
            'civilized_countries': civilized_countries,
            'province_owners': province_owners
        }
        
        # 显示统计摘要
        print(f"\\n📈 全面统计摘要:")
        print(f"   总国家数: {len(all_countries)}")
        print(f"   有省份的国家: {len(countries_with_provinces)}")
        print(f"   无省份的国家: {len(countries_without_provinces)}")
        print(f"   附庸国家: {len(vassal_countries)}")
        print(f"   文明化国家: {len(civilized_countries)}")
        
        print(f"\\n🏆 有省份的前10大国家:")
        sorted_with_provinces = sorted(countries_with_provinces.items(), 
                                     key=lambda x: x[1]['provinces_owned'], reverse=True)[:10]
        for i, (tag, info) in enumerate(sorted_with_provinces, 1):
            vassal_status = " (附庸)" if info['is_vassal'] else ""
            civ_status = " (文明)" if info['civilized'] else ""
            print(f"   {i:2d}. {tag}: {info['provinces_owned']} 个省份{vassal_status}{civ_status}")
        
        print(f"\\n🔍 无省份国家样例 (前20个):")
        no_province_list = list(countries_without_provinces.keys())[:20]
        for i, tag in enumerate(no_province_list, 1):
            info = countries_without_provinces[tag]
            vassal_status = f" (附庸于{info['overlord']})" if info['is_vassal'] else ""
            civ_status = " (文明)" if info['civilized'] else ""
            print(f"   {i:2d}. {tag}{vassal_status}{civ_status}")
        
        if len(countries_without_provinces) > 20:
            print(f"   ... 还有 {len(countries_without_provinces) - 20} 个无省份国家")
        
        return report_data
    
    def save_comprehensive_analysis(self, filename=None):
        """保存全面分析到JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_country_analysis_{timestamp}.json"
        
        print(f"💾 保存全面分析到: {filename}")
        
        # 生成报告
        report_data = self.generate_comprehensive_report()
        
        # 保存到JSON文件
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 全面分析已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            return None

def main():
    """主函数"""
    print("🌍 Victoria II 全面国家分析工具")
    print("=" * 40)
    
    filename = 'autosave.v2'
    if not os.path.exists(filename):
        print(f"❌ 未找到文件: {filename}")
        return
    
    try:
        analyzer = ComprehensiveCountryAnalyzer(filename)
        result_file = analyzer.save_comprehensive_analysis()
        
        if result_file:
            print(f"\\n🎉 全面分析完成！")
        else:
            print(f"\\n❌ 分析失败")
            
    except Exception as e:
        print(f"❌ 分析出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import os
    main()
