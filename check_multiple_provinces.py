#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查多个省份的意识形态转换
"""

import re

def check_multiple_provinces(filename):
    with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
        content = f.read()
    
    print(f'=== 检查 {filename} 的多个省份 ===')
    
    # 查找中国省份的人口意识形态
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    chinese_provinces_found = 0
    for i, match in enumerate(province_matches[:50]):
        province_id = int(match.group(1))
        start_pos = match.end()
        
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            end_pos = start_pos + 10000
        
        province_content = content[start_pos:end_pos]
        
        if 'owner=CHI' in province_content or 'owner="CHI"' in province_content:
            chinese_provinces_found += 1
            
            if chinese_provinces_found <= 3:  # 只显示前3个
                print(f'\n--- 中国省份 {province_id} ---')
                
                # 查找人口意识形态
                pop_match = re.search(r'(farmers|craftsmen|labourers)=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', province_content, re.DOTALL)
                
                if pop_match:
                    pop_content = pop_match.group(2)
                    ideology_match = re.search(r'ideology=\s*{([^{}]*?)}', pop_content, re.DOTALL)
                    
                    if ideology_match:
                        ideology_content = ideology_match.group(1)
                        ideology_lines = []
                        total = 0.0
                        for line in ideology_content.split('\n'):
                            line = line.strip()
                            if line and '=' in line:
                                ideology_lines.append(line)
                                parts = line.split('=')
                                if len(parts) == 2:
                                    try:
                                        total += float(parts[1])
                                    except:
                                        pass
                        
                        print('意识形态分布:')
                        for line in ideology_lines:
                            print(f'  {line}')
                        print(f'  总计: {total:.5f}')

def main():
    print("原始文件:")
    check_multiple_provinces('China1836_01_01_chinese_pop_backup_20250727_012244.v2')
    print('\n' + '='*60 + '\n')
    print("修改后文件:")
    check_multiple_provinces('China1836_01_01.v2')

if __name__ == "__main__":
    main()
