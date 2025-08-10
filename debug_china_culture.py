#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试中国文化设置
"""

import re

def debug_china_culture():
    """调试中国文化设置"""
    with open('ChinaUseIt.v2', 'r', encoding='latin1') as f:
        content = f.read()
    
    print("调试中国文化设置...")
    
    # 找到中国块
    china_match = re.search(r'^CHI=\s*{', content, re.MULTILINE)
    if not china_match:
        print("未找到中国块")
        return
    
    print(f"找到中国块起始位置: {china_match.start()}")
    
    start_pos = china_match.end()
    
    # 找到中国块结束位置
    next_country = re.search(r'\n[A-Z]{2,3}=\s*{', content[start_pos:start_pos+500000])
    if next_country:
        end_pos = start_pos + next_country.start()
        next_country_tag = next_country.group().strip().split('=')[0]
        print(f"中国块结束位置: {end_pos} (下一个国家: {next_country_tag})")
    else:
        end_pos = start_pos + 300000
        print(f"未找到下一个国家，使用默认结束位置: {end_pos}")
    
    china_content = content[start_pos:end_pos]
    print(f"中国块大小: {len(china_content)} 字符")
    
    # 显示中国块的前2000字符
    print("\n中国块内容 (前2000字符):")
    print("=" * 50)
    print(china_content[:2000])
    print("=" * 50)
    
    # 搜索primary_culture
    primary_matches = re.findall(r'primary_culture\s*=\s*([a-z_]+)', china_content)
    print(f"\n找到的primary_culture: {primary_matches}")
    
    # 搜索accepted_culture的各种可能格式
    print("\n搜索accepted_culture...")
    
    # 格式1: accepted_culture = culture_name
    accepted1 = re.findall(r'accepted_culture\s*=\s*([a-z_]+)', china_content)
    print(f"格式1 (直接): {accepted1}")
    
    # 格式2: accepted_culture = "culture_name"
    accepted2 = re.findall(r'accepted_culture\s*=\s*"([a-z_]+)"', china_content)
    print(f"格式2 (引号): {accepted2}")
    
    # 格式3: 查找包含accepted_culture的行
    accepted_lines = []
    for line_num, line in enumerate(china_content.split('\n')):
        if 'accepted_culture' in line.lower():
            accepted_lines.append((line_num, line.strip()))
    
    print(f"包含accepted_culture的行 ({len(accepted_lines)}个):")
    for line_num, line in accepted_lines:
        print(f"  行{line_num}: {line}")
    
    # 搜索包含这些文化的上下文
    print("\n搜索文化相关上下文...")
    target_cultures = ['nanfaren', 'manchu', 'yankee', 'dixie', 'beifaren']
    
    for culture in target_cultures:
        matches = list(re.finditer(culture, china_content))
        print(f"\n文化 '{culture}' 出现 {len(matches)} 次:")
        for i, match in enumerate(matches[:3]):  # 只显示前3个
            start_context = max(0, match.start() - 100)
            end_context = min(len(china_content), match.end() + 100)
            context = china_content[start_context:end_context]
            print(f"  出现{i+1}: ...{context}...")
    
    # 搜索可能的文化块或列表
    print("\n搜索可能的文化相关块...")
    
    # 查找包含多个文化的块
    culture_block_patterns = [
        r'primary_culture\s*=\s*([a-z_]+).*?accepted_culture.*?=.*?([a-z_]+)',
        r'{[^{}]*(?:nanfaren|manchu|yankee|beifaren)[^{}]*}',
        r'culture.*?{[^{}]*(?:nanfaren|manchu|yankee|beifaren)[^{}]*}'
    ]
    
    for pattern in culture_block_patterns:
        matches = re.findall(pattern, china_content, re.DOTALL)
        if matches:
            print(f"模式 '{pattern[:50]}...': {matches}")
    
    # 查找在相对位置出现primary_culture的地方
    print("\n搜索primary_culture在更大范围内...")
    full_search_content = content[max(0, start_pos - 50000):end_pos + 50000]
    primary_in_full = re.findall(r'primary_culture\s*=\s*([a-z_]+)', full_search_content)
    print(f"扩大搜索范围找到的primary_culture: {primary_in_full}")
    
    # 搜索beifaren周围的内容
    beifaren_matches = list(re.finditer(r'beifaren', china_content))
    print(f"\nbeifaren 出现 {len(beifaren_matches)} 次:")
    for i, match in enumerate(beifaren_matches[:2]):
        start_context = max(0, match.start() - 200)
        end_context = min(len(china_content), match.end() + 200)
        context = china_content[start_context:end_context]
        print(f"  beifaren上下文{i+1}:")
        print(f"    ...{context}...")

if __name__ == "__main__":
    debug_china_culture()
