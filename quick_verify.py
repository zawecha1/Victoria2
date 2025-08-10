#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

content = open('autosave.v2', 'r', encoding='latin1').read()
print('文件验证:')
print(f'大小: {len(content):,} 字符')
print(f'花括号: 开={content.count("{"):,}, 闭={content.count("}"):,}, 差异={content.count("{") - content.count("}")}')

# 快速检查孤立引用
province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
province_matches = list(province_pattern.finditer(content))

valid_pop_ids = set()
china_count = 0
for i, match in enumerate(province_matches[:1000]):
    province_id = int(match.group(1))
    start_pos = match.end()
    if i + 1 < len(province_matches):
        end_pos = province_matches[i + 1].start()
    else:
        next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+10000])
        end_pos = start_pos + next_section.start() if next_section else start_pos + 8000
    
    province_content = content[start_pos:end_pos]
    if 'owner="CHI"' in province_content or 'owner=CHI' in province_content:
        china_count += 1
        pop_ids = re.findall(r'id\s*=\s*(\d+)', province_content)
        valid_pop_ids.update(pop_ids)

pop_pattern = r'pop=\s*{\s*id=(\d+)\s*type=(\d+)\s*}'
pop_matches = list(re.finditer(pop_pattern, content))
orphaned = sum(1 for match in pop_matches if match.group(1) not in valid_pop_ids)

print(f'中国省份: {china_count} 个')
print(f'有效人口ID: {len(valid_pop_ids)} 个')
print(f'总pop引用: {len(pop_matches)} 个')
print(f'孤立引用: {orphaned} 个')
print('状态:', '✅ 完美修复!' if orphaned == 0 else f'❌ 还有{orphaned}个孤立引用')
