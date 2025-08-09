#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('autosave.v2', 'r', encoding='utf-8-sig', errors='ignore') as f:
    content = f.read()

print('🔍 查找CHI的civilized=yes...')
yes_matches = list(re.finditer(r'civilized\s*=\s*yes', content))

for i, match in enumerate(yes_matches):
    # 向前查找最近的国家代码
    start_pos = max(0, match.start() - 2000)  # 查找前2000字符
    before_context = content[start_pos:match.start()]
    
    # 查找国家代码模式
    country_matches = list(re.finditer(r'([A-Z]{2,3})\s*=\s*\{', before_context))
    if country_matches:
        last_country = country_matches[-1].group(1)  # 最后一个匹配的国家代码
        print(f'匹配 {i+1}: civilized=yes 属于国家 {last_country}')
        
        if last_country == 'CHI':
            print('  🎯 找到了！这是中国的civilized=yes!')
            # 显示更多上下文
            context_start = max(0, match.start() - 500)
            context_end = min(len(content), match.end() + 500)
            chi_context = content[context_start:context_end]
            print(f'  中国块内容: {chi_context}')
            break
    else:
        print(f'匹配 {i+1}: 无法确定所属国家')
