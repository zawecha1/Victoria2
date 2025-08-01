#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查意识形态格式差异
"""

import re

def check_ideology_format(filename):
    with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
        content = f.read()
    
    print(f'=== 检查 {filename} 的意识形态格式 ===')
    
    # 查找中国省份的人口意识形态
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    for i, match in enumerate(province_matches[:20]):
        province_id = int(match.group(1))
        start_pos = match.end()
        
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            end_pos = start_pos + 10000
        
        province_content = content[start_pos:end_pos]
        
        if 'owner=CHI' in province_content or 'owner="CHI"' in province_content:
            print(f'\n--- 中国省份 {province_id} ---')
            
            # 查找人口意识形态
            pop_match = re.search(r'(farmers|craftsmen|labourers)=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', province_content, re.DOTALL)
            
            if pop_match:
                pop_content = pop_match.group(2)
                ideology_match = re.search(r'ideology=\s*{([^{}]*?)}', pop_content, re.DOTALL)
                
                if ideology_match:
                    ideology_content = ideology_match.group(1)
                    print(f'意识形态内容:')
                    for line in ideology_content.split('\n'):
                        line = line.strip()
                        if line and '=' in line:
                            print(f'  {line}')
            break

def main():
    # 检查备份文件的原始格式
    print("备份文件（原始）:")
    check_ideology_format('China1836_01_01_chinese_pop_backup_20250727_012244.v2')
    print('\n' + '='*60 + '\n')
    # 检查修改后文件的格式
    print("修改后文件:")
    check_ideology_format('China1836_01_01.v2')

if __name__ == "__main__":
    main()
