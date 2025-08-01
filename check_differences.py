#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Victoria II存档文件的差异和问题
"""

import re

def check_population_format(filename, sample_provinces=3):
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        print(f'=== 检查 {filename} 的人口格式 ===')
        
        # 查找中国省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(content))
        
        chinese_provinces = []
        for i, match in enumerate(province_matches[:50]):  # 只检查前50个省份
            province_id = int(match.group(1))
            start_pos = match.end()
            
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                end_pos = start_pos + 10000
            
            province_content = content[start_pos:end_pos]
            
            # 检查是否为中国拥有
            if 'owner=CHI' in province_content or 'owner="CHI"' in province_content:
                chinese_provinces.append((province_id, province_content))
                if len(chinese_provinces) >= sample_provinces:
                    break
        
        print(f'找到 {len(chinese_provinces)} 个中国省份样本')
        
        # 检查人口格式
        for i, (province_id, province_content) in enumerate(chinese_provinces):
            print(f'\n--- 省份 {province_id} ---')
            
            # 查找第一个人口块
            pop_match = re.search(r'(farmers|craftsmen|labourers)=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', province_content, re.DOTALL)
            
            if pop_match:
                pop_type = pop_match.group(1)
                pop_content = pop_match.group(2)
                
                print(f'{pop_type} 内容前200字符:')
                print(repr(pop_content[:200]))
                
                # 检查文化=宗教格式
                culture_religion = re.search(r'(\w+)=(\w+)', pop_content)
                if culture_religion:
                    print(f'文化=宗教: {culture_religion.group(0)}')
                else:
                    print('未找到文化=宗教格式')
                
                # 检查意识形态格式
                ideology_match = re.search(r'ideology=\s*{([^{}]*)}', pop_content, re.DOTALL)
                if ideology_match:
                    ideology_content = ideology_match.group(1)
                    print(f'意识形态内容: {repr(ideology_content[:100])}')
                else:
                    print('未找到意识形态格式')
                    
    except Exception as e:
        print(f'检查失败: {e}')

def main():
    # 检查原始文件和修改后文件的人口格式
    print("检查原始备份文件:")
    check_population_format('China1836_01_01_chinese_pop_backup_20250727_012244.v2')
    
    print('\n' + '='*80 + '\n')
    
    print("检查修改后文件:")
    check_population_format('China1836_01_01.v2')

if __name__ == "__main__":
    main()
