#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
省份重分配工具 - 首都保护版
保留各国首都，其余省份分配给中国
"""

from victoria2_main_modifier import Victoria2Modifier
import sys
import os
import re
from typing import Dict, List, Tuple

def safe_preview_redistribution(filename='autosave.v2'):
    """安全的预览重分配方案（无表情符号）"""
    print("省份重分配预览模式")
    print("=" * 40)
    
    if not os.path.exists(filename):
        print(f"未找到文件: {filename}")
        return False
    
    try:
        redistributor = ProvinceRedistributor(filename)
        countries_data, provinces_data = redistributor.analyze_country_provinces()
        
        print("\\n规划首都保护重分配方案...")
        
        redistribution_plan = {
            'kept_provinces': {},
            'transferred_provinces': [],
            'china_gains': 0,
            'affected_countries': 0,
            'capital_protected': 0,
            'no_capital_countries': []
        }
        
        # 分析各国首都信息
        country_pattern = re.compile(r'^([A-Z]{2,3})=\s*{', re.MULTILINE)
        country_matches = list(country_pattern.finditer(redistributor.content))
        
        capitals_info = {}
        for i, match in enumerate(country_matches):
            country_tag = match.group(1)
            start_pos = match.end()
            
            if i + 1 < len(country_matches):
                end_pos = country_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', redistributor.content[start_pos:start_pos+50000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 30000
            
            country_content = redistributor.content[start_pos:end_pos]
            capital_match = re.search(r'capital=(\d+)', country_content)
            if capital_match:
                capitals_info[country_tag] = int(capital_match.group(1))
        
        # 执行重分配规划
        for country_tag, country_info in countries_data.items():
            if country_tag == 'CHI':
                continue
                
            provinces = country_info['provinces']
            capital = capitals_info.get(country_tag)
            
            if not provinces:
                continue
            
            # 首都保护逻辑
            if capital and capital in provinces:
                kept_province = capital
                redistribution_plan['capital_protected'] += 1
                reason = "首都保护"
            else:
                kept_province = provinces[0]
                redistribution_plan['no_capital_countries'].append(country_tag)
                reason = "替代省份"
            
            redistribution_plan['kept_provinces'][country_tag] = {
                'province_id': kept_province,
                'province_name': provinces_data[kept_province]['name'],
                'reason': reason
            }
            
            # 转移其余省份
            if len(provinces) > 1:
                redistribution_plan['affected_countries'] += 1
                for province_id in provinces:
                    if province_id != kept_province:
                        redistribution_plan['transferred_provinces'].append({
                            'province_id': province_id,
                            'province_name': provinces_data[province_id]['name'],
                            'original_owner': country_tag
                        })
                        redistribution_plan['china_gains'] += 1
        
        # 显示结果
        print(f"\\n重分配方案统计:")
        print(f"  总国家数: {len(countries_data)} 个")
        print(f"  首都保护成功: {redistribution_plan['capital_protected']} 个")
        print(f"  使用替代省份: {len(redistribution_plan['no_capital_countries'])} 个")
        print(f"  受影响国家: {redistribution_plan['affected_countries']} 个")
        print(f"  中国将获得: {redistribution_plan['china_gains']} 个省份")
        
        china_current = len(countries_data.get('CHI', {}).get('provinces', []))
        print(f"  中国当前省份: {china_current} 个")
        print(f"  重分配后省份: {china_current + redistribution_plan['china_gains']} 个")
        
        print(f"\\n各国保留的省份 (前20个):")
        kept_items = list(redistribution_plan['kept_provinces'].items())[:20]
        for i, (country_tag, info) in enumerate(kept_items, 1):
            print(f"  {i:2d}. {country_tag}: {info['province_name']} ({info['reason']})")
        
        if len(redistribution_plan['kept_provinces']) > 20:
            print(f"  ... 还有 {len(redistribution_plan['kept_provinces']) - 20} 个国家")
        
        print(f"\\n转移给中国的省份 (前15个):")
        for i, info in enumerate(redistribution_plan['transferred_provinces'][:15], 1):
            print(f"  {i:2d}. {info['province_name']} <- {info['original_owner']}")
        
        if len(redistribution_plan['transferred_provinces']) > 15:
            print(f"  ... 还有 {len(redistribution_plan['transferred_provinces']) - 15} 个省份")
        
        print(f"\\n预览完成! 这将创造一个中国世界统一的局面。")
        return True
        
    except Exception as e:
        print(f"预览出错: {e}")
        import traceback
        traceback.print_exc()
        return False

class ProvinceRedistributor:
    """省份重分配器"""
    
    def __init__(self, filename: str):
        self.modifier = Victoria2Modifier(filename, debug_mode=True)
        self.content = self.modifier.content
        
    def analyze_country_provinces(self) -> Dict[str, Dict]:
        """分析各国的省份分布"""
        print("分析国家省份分布...")
        
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        countries_data = {}
        provinces_data = {}
        
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+20000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 10000
            
            province_content = self.content[start_pos:end_pos]
            
            province_info = {
                'id': province_id,
                'name': 'Unknown',
                'owner': None,
                'start_pos': match.start(),
                'end_pos': end_pos,
                'content': province_content
            }
            
            name_match = re.search(r'name="([^"]+)"', province_content)
            if name_match:
                province_info['name'] = name_match.group(1)
            
            owner_match = re.search(r'owner="?([A-Z]{2,3})"?', province_content)
            if owner_match:
                province_info['owner'] = owner_match.group(1)
            
            provinces_data[province_id] = province_info
            
            if province_info['owner']:
                owner = province_info['owner']
                if owner not in countries_data:
                    countries_data[owner] = {
                        'tag': owner,
                        'provinces': []
                    }
                countries_data[owner]['provinces'].append(province_id)
            
            if (i + 1) % 500 == 0:
                print(f"  处理进度: {i + 1}/{len(province_matches)}")
        
        print(f"分析完成: {len(countries_data)} 个国家, {len(provinces_data)} 个省份")
        return countries_data, provinces_data

def main():
    """主函数"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "preview":
            safe_preview_redistribution()
        else:
            print(f"未知模式: {mode}")
            print(f"支持的模式: preview")
    else:
        safe_preview_redistribution()

if __name__ == "__main__":
    main()
