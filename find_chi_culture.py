#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找CHI国家的文化和恶名度设置
"""

def main():
    with open('China2281_01_01.v2', 'r', encoding='utf-8-sig') as f:
        content = f.read()

    import re

    # 找到CHI块的位置
    chi_start_match = re.search(r'^CHI=\s*\{', content, re.MULTILINE)
    if chi_start_match:
        start_pos = chi_start_match.start()
        
        # 找到CHI块的结束 - 查找下一个国家
        next_country_match = re.search(r'\n[A-Z]{3}=\s*\{', content[start_pos + 100:])
        if next_country_match:
            end_pos = start_pos + 100 + next_country_match.start()
        else:
            end_pos = len(content)
        
        chi_block = content[start_pos:end_pos]
        
        print(f"CHI块大小: {len(chi_block):,} 字符")
        print(f"CHI块位置: {start_pos}-{end_pos}")
        
        # 查找主文化
        primary_match = re.search(r'primary_culture="([^"]+)"', chi_block)
        if primary_match:
            print(f"CHI主文化: {primary_match.group(1)}")
        else:
            print("CHI主文化: 未找到")
        
        # 查找接受文化
        accepted_pattern = r'accepted_culture=\s*\{\s*([^}]+)\s*\}'
        accepted_match = re.search(accepted_pattern, chi_block, re.DOTALL)
        if accepted_match:
            cultures = re.findall(r'"([^"]+)"', accepted_match.group(1))
            print(f"CHI接受文化: {cultures}")
        else:
            print("CHI接受文化: 未找到")
        
        # 查找恶名度
        badboy_match = re.search(r'badboy=([\d.]+)', chi_block)
        if badboy_match:
            print(f"CHI恶名度: {badboy_match.group(1)}")
        else:
            print("CHI恶名度: 未找到")
        
        # 显示CHI块的前1000字符，看看结构
        print(f"\nCHI块前1000字符:")
        print(chi_block[:1000])
        
    else:
        print("未找到CHI块")

if __name__ == "__main__":
    main()
