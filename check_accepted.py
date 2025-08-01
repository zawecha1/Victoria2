#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def check_accepted_culture():
    with open('China2281_01_01.v2', 'r', encoding='utf-8-sig') as f:
        content = f.read()

    import re
    chi_match = re.search(r'^CHI=\s*\{', content, re.MULTILINE)
    if chi_match:
        start_pos = chi_match.start()
        next_country_match = re.search(r'\n[A-Z]{3}=\s*\{', content[start_pos + 100:])
        if next_country_match:
            end_pos = start_pos + 100 + next_country_match.start()
        else:
            end_pos = len(content)
        
        chi_block = content[start_pos:end_pos]
        
        print("查找accepted_culture模式:")
        print(f"CHI块大小: {len(chi_block)} 字符")
        
        # 搜索任何包含accepted的内容
        accepted_lines = []
        lines = chi_block.split('\n')
        for i, line in enumerate(lines):
            if 'accepted' in line.lower():
                accepted_lines.append((i, line.strip()))
        
        if accepted_lines:
            print(f"\n包含accepted的行:")
            for line_num, line in accepted_lines[:10]:
                print(f"  行{line_num}: {repr(line)}")
        else:
            print("\n未找到任何包含accepted的行")
            
        # 查找primary_culture附近的内容
        primary_match = re.search(r'primary_culture="([^"]+)"', chi_block)
        if primary_match:
            primary_pos = primary_match.start()
            print(f"\nprimary_culture附近的内容:")
            context = chi_block[primary_pos-100:primary_pos+300]
            print(repr(context))

if __name__ == "__main__":
    check_accepted_culture()
