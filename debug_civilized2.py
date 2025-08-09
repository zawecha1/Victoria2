#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('autosave.v2', 'r', encoding='utf-8-sig', errors='ignore') as f:
    content = f.read()

print('🔍 调试查找civilized=yes...')
yes_matches = list(re.finditer(r'civilized\s*=\s*yes', content))
print(f'找到 {len(yes_matches)} 个civilized=yes')

# 只看第一个匹配的详细信息
if yes_matches:
    match = yes_matches[0]
    print(f'\\n第一个匹配位置: {match.start()}-{match.end()}')
    
    # 向前查找2000字符的上下文
    start_pos = max(0, match.start() - 2000)
    before_context = content[start_pos:match.start()]
    
    print(f'前面2000字符的内容: {before_context[-500:]}')  # 只显示最后500字符
    
    # 查找国家代码模式 
    country_pattern = r'([A-Z]{2,3})\s*=\s*\{'
    country_matches = list(re.finditer(country_pattern, before_context))
    
    print(f'\\n在前面内容中找到 {len(country_matches)} 个国家代码匹配')
    
    if country_matches:
        for i, cm in enumerate(country_matches[-5:]):  # 显示最后5个
            print(f'  国家匹配 {len(country_matches)-4+i}: {cm.group(1)} 在位置 {cm.start()}')
        
        last_country = country_matches[-1].group(1)
        print(f'\\n最近的国家代码: {last_country}')
    else:
        print('\\n❌ 没有找到国家代码匹配')
        
        # 尝试其他模式
        print('\\n尝试查找其他模式...')
        other_patterns = [
            (r'[A-Z]{3}\s*=', '3字母代码='),
            (r'[A-Z]{2}\s*=', '2字母代码='),
            (r'\\b[A-Z]{2,3}\\b', '2-3字母单词'),
        ]
        
        for pattern, desc in other_patterns:
            matches = list(re.finditer(pattern, before_context))
            print(f'  {desc}: 找到 {len(matches)} 个')
            if matches:
                for m in matches[-3:]:  # 显示最后3个
                    print(f'    {m.group(0)} 在位置 {m.start()}')
