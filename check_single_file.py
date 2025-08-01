#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接检查单个文件的意识形态分布
"""

import re
import sys

def analyze_single_file(filename, province_count=3):
    """分析单个文件的意识形态分布"""
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"无法读取文件 {filename}: {e}")
        return
    
    print(f"=== 检查 {filename} 的多个省份 ===")
    
    # 查找中国省份
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    chinese_province_count = 0
    
    for i, match in enumerate(province_matches):
        if chinese_province_count >= province_count:
            break
            
        province_id = int(match.group(1))
        start_pos = match.end()
        
        # 确定省份块的结束位置
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+20000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 10000
        
        province_content = content[start_pos:end_pos]
        
        # 检查是否为中国拥有
        owner_match = re.search(r'owner="?CHI"?', province_content)
        if owner_match:
            chinese_province_count += 1
            print(f"--- 中国省份 {province_id} ---")
            
            # 查找所有意识形态分布
            ideology_pattern = r'ideology=\s*{([^{}]*)}'
            ideology_matches = re.findall(ideology_pattern, province_content, re.DOTALL)
            
            if ideology_matches:
                # 汇总所有意识形态数据
                total_ideology_dist = {}
                
                for ideology_content in ideology_matches:
                    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
                    for id_str, value_str in ideology_pairs:
                        ideology_id = int(id_str)
                        value = float(value_str)
                        total_ideology_dist[ideology_id] = total_ideology_dist.get(ideology_id, 0) + value
                
                print("意识形态分布:")
                total = 0
                for ideology_id in sorted(total_ideology_dist.keys()):
                    value = total_ideology_dist[ideology_id]
                    print(f"  {ideology_id}={value:.5f}")
                    total += value
                print(f"  总计: {total:.5f}")
            else:
                print("  未找到意识形态分布")

def main():
    if len(sys.argv) < 2:
        print("用法: python check_single_file.py <文件名> [省份数量]")
        return
    
    filename = sys.argv[1]
    province_count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    analyze_single_file(filename, province_count)

if __name__ == "__main__":
    main()
