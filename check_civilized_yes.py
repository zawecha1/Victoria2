#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

# 检查是否有任何包含civilized=yes的内容
with open('autosave.v2', 'r', encoding='utf-8-sig', errors='ignore') as f:
    content = f.read()

print('🔍 搜索所有civilized=yes...')
yes_matches = list(re.finditer(r'civilized\s*=\s*[\'\"]*yes[\'\"]*', content))
print(f'找到 {len(yes_matches)} 个 civilized=yes')

if yes_matches:
    for i, match in enumerate(yes_matches[:5]):  # 只显示前5个
        start_pos = max(0, match.start() - 100)
        end_pos = min(len(content), match.end() + 100)
        context = content[start_pos:end_pos]
        print(f'匹配 {i+1}: 位置 {match.start()}')
        print(f'上下文: {context}')
        print('---')
        
        # 看看这个yes是不是在CHI块中
        chi_context_start = max(0, match.start() - 500)
        chi_context_end = min(len(content), match.end() + 500)
        chi_context = content[chi_context_start:chi_context_end]
        if 'CHI' in chi_context:
            print(f'  ✅ 这个civilized=yes可能与CHI相关')
            print(f'  CHI上下文: {chi_context}')
else:
    print('❌ 没有找到任何civilized=yes')
    
    # 检查所有civilized字段的值分布
    print('\n📊 检查所有civilized值分布...')
    all_civilized = list(re.finditer(r'civilized\s*=\s*[\'\"]*([^\'\"\\s}]+)[\'\"]*', content))
    values = {}
    for match in all_civilized:
        value = match.group(1)
        values[value] = values.get(value, 0) + 1
    
    print('值分布:')
    for value, count in sorted(values.items()):
        print(f'  {value}: {count} 次')
