#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版省份重分配测试工具
"""

import os
import re
from victoria2_main_modifier import Victoria2Modifier

def test_capital_protection():
    """测试首都保护逻辑"""
    print("测试首都保护逻辑...")
    
    filename = 'autosave.v2'
    if not os.path.exists(filename):
        print("文件不存在:", filename)
        return
    
    try:
        modifier = Victoria2Modifier(filename, debug_mode=True)
        content = modifier.content
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(content))
        
        print(f"找到 {len(province_matches)} 个省份")
        
        countries_data = {}
        provinces_data = {}
        
        # 分析前10个省份作为测试
        for i, match in enumerate(province_matches[:100]):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            if i + 1 < len(province_matches[:100]):
                end_pos = province_matches[i + 1].start()
            else:
                end_pos = start_pos + 5000
            
            province_content = content[start_pos:end_pos]
            
            # 查找拥有者
            owner_match = re.search(r'owner="?([A-Z]{2,3})"?', province_content)
            if owner_match:
                owner = owner_match.group(1)
                
                if owner not in countries_data:
                    countries_data[owner] = {'provinces': []}
                countries_data[owner]['provinces'].append(province_id)
                
                # 查找省份名称
                name_match = re.search(r'name="([^"]+)"', province_content)
                name = name_match.group(1) if name_match else 'Unknown'
                
                provinces_data[province_id] = {
                    'name': name,
                    'owner': owner
                }
        
        # 查找各国首都
        country_pattern = re.compile(r'^([A-Z]{2,3})=\s*{', re.MULTILINE)
        country_matches = list(country_pattern.finditer(content))
        
        for i, match in enumerate(country_matches[:20]):
            country_tag = match.group(1)
            start_pos = match.end()
            
            if i + 1 < len(country_matches[:20]):
                end_pos = country_matches[i + 1].start()
            else:
                end_pos = start_pos + 30000
            
            country_content = content[start_pos:end_pos]
            
            # 查找首都
            capital_match = re.search(r'capital=(\d+)', country_content)
            if capital_match and country_tag in countries_data:
                capital_id = int(capital_match.group(1))
                countries_data[country_tag]['capital'] = capital_id
        
        # 测试重分配逻辑
        print("\\n首都保护测试结果:")
        for country_tag, country_info in countries_data.items():
            if country_tag == 'CHI':
                continue
                
            provinces = country_info['provinces']
            capital = country_info.get('capital')
            
            if not provinces:
                continue
                
            if capital and capital in provinces:
                kept_province = capital
                status = "首都保护"
            else:
                kept_province = provinces[0]
                status = "替代省份"
            
            transferred_count = len(provinces) - 1
            kept_name = provinces_data.get(kept_province, {}).get('name', 'Unknown')
            
            print(f"  {country_tag}: 保留 {kept_name} ({status}), 转移 {transferred_count} 个省份")
        
        print("\\n测试完成!")
        
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_capital_protection()
