#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人口调试工具 - 查看中国省份的实际人口情况
"""

import os
import re
import json
from datetime import datetime

def load_file_simple(filename):
    """简单文件加载"""
    encodings = ['latin1', 'utf-8', 'utf-8-sig']
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"文件加载成功 (编码: {encoding}), 大小: {len(content):,} 字符")
            return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"加载失败: {e}")
            return None
    return None

def debug_china_populations(filename):
    """调试中国人口情况"""
    print("=" * 60)
    print("中国人口调试工具")
    print("=" * 60)
    
    content = load_file_simple(filename)
    if not content:
        return
    
    # 查找中国的前几个省份
    print("\n查找中国省份...")
    china_provinces = []
    
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    for i, match in enumerate(province_matches[:20]):  # 只检查前20个省份
        province_id = int(match.group(1))
        start_pos = match.end()
        
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+20000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 10000
        
        province_content = content[start_pos:end_pos]
        
        # 检查是否属于中国
        owner_match = re.search(r'owner="?CHI"?', province_content)
        if owner_match:
            name_match = re.search(r'name="([^"]+)"', province_content)
            province_name = name_match.group(1) if name_match else f"Province_{province_id}"
            
            print(f"\n省份 {province_id}: {province_name}")
            
            # 分析人口 - 改进人口检测
            pop_types = ['aristocrats', 'artisans', 'bureaucrats', 'capitalists', 'clergymen', 
                        'clerks', 'craftsmen', 'farmers', 'labourers', 'officers', 'soldiers']
            
            total_pops_found = 0
            
            # 使用更宽松的匹配模式
            for pop_type in pop_types:
                # 匹配模式：pop_type = { ... }
                pop_pattern = re.compile(rf'{pop_type}\s*=\s*{{([^{{}}]*?)}}', re.DOTALL)
                pop_matches = list(pop_pattern.finditer(province_content))
                
                for pop_match in pop_matches:
                    pop_content = pop_match.group(1)  # 获取大括号内的内容
                    total_pops_found += 1
                    
                    culture_match = re.search(r'culture\s*=\s*"?([a-z_]+)"?', pop_content)
                    size_match = re.search(r'size\s*=\s*"?([0-9.]+)"?', pop_content)
                    
                    if culture_match:
                        culture = culture_match.group(1)
                        size = float(size_match.group(1)) if size_match else 0
                        print(f"  {pop_type}: {culture} (人口: {size:.0f})")
                    else:
                        print(f"  {pop_type}: 未找到文化信息")
                        # 显示这个人口单位的内容用于调试
                        print(f"    内容: {pop_content[:100]}")
            
            if total_pops_found == 0:
                print("  未找到任何人口单位")
                # 显示省份内容的一部分用于调试
                print(f"  省份内容前500字符: {province_content[:500]}")
            else:
                print(f"  总共找到 {total_pops_found} 个人口单位")
            
            china_provinces.append(province_id)
            
            if len(china_provinces) >= 3:  # 只显示前3个省份
                break
    
    print(f"\n找到 {len(china_provinces)} 个中国省份示例")

if __name__ == "__main__":
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else 'autosave.v2'
    debug_china_populations(filename)
