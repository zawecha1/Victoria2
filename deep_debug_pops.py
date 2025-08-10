#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强化人口调试工具 - 深度分析人口结构
"""

import os
import re

def load_file_simple(filename):
    """简单文件加载"""
    encodings = ['latin1', 'utf-8', 'utf-8-sig']
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"文件加载成功 (编码: {encoding}), 大小: {len(content):,} 字符")
            return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"加载失败: {e}")
            return None
    return None

def deep_debug_province(province_content, province_id, province_name):
    """深度调试省份内容"""
    print(f"\n" + "="*50)
    print(f"深度分析省份 {province_id}: {province_name}")
    print("="*50)
    
    # 1. 查看整个省份内容长度
    print(f"省份内容长度: {len(province_content)} 字符")
    
    # 2. 查找所有以 = 开头的行（可能的数据字段）
    lines = province_content.split('\n')
    data_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if '=' in stripped and not stripped.startswith('#'):
            data_lines.append((i, stripped))
    
    print(f"找到 {len(data_lines)} 个数据字段")
    
    # 3. 查找人口相关的行
    pop_types = ['aristocrats', 'artisans', 'bureaucrats', 'capitalists', 'clergymen', 
                'clerks', 'craftsmen', 'farmers', 'labourers', 'officers', 'soldiers']
    
    pop_lines = []
    for line_num, line in data_lines:
        for pop_type in pop_types:
            if pop_type in line:
                pop_lines.append((line_num, line, pop_type))
    
    print(f"找到 {len(pop_lines)} 个人口相关行:")
    for line_num, line, pop_type in pop_lines[:10]:  # 只显示前10个
        print(f"  行{line_num}: {line}")
    
    # 4. 使用不同的正则表达式模式搜索人口块
    print(f"\n测试不同的人口匹配模式:")
    
    # 模式1: 简单匹配
    for pop_type in pop_types[:3]:  # 只测试前3个类型
        pattern1 = rf'{pop_type}\s*=\s*{{([^{{}}]*?)}}' 
        matches1 = re.findall(pattern1, province_content, re.DOTALL)
        print(f"  {pop_type} (模式1): {len(matches1)} 个匹配")
        
        if matches1:
            for i, match in enumerate(matches1[:2]):  # 只显示前2个
                print(f"    匹配{i+1}: {match[:100]}...")
    
    # 5. 手动搜索第一个人口块
    print(f"\n手动搜索人口块:")
    for pop_type in pop_types:
        start_idx = province_content.find(f'{pop_type}=')
        if start_idx != -1:
            print(f"找到 {pop_type} 在位置 {start_idx}")
            # 显示周围的内容
            context_start = max(0, start_idx - 50)
            context_end = min(len(province_content), start_idx + 200)
            context = province_content[context_start:context_end]
            print(f"  上下文: {context}")
            break

def main():
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else 'ChinaUseIt.v2'
    
    content = load_file_simple(filename)
    if not content:
        return
    
    # 找第一个中国省份
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    for i, match in enumerate(province_matches[:50]):  # 检查前50个省份
        province_id = int(match.group(1))
        start_pos = match.end()
        
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            # 使用更大的搜索范围
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+50000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 30000
        
        province_content = content[start_pos:end_pos]
        
        # 检查是否属于中国
        owner_match = re.search(r'owner="?CHI"?', province_content)
        if owner_match:
            name_match = re.search(r'name="([^"]+)"', province_content)
            province_name = name_match.group(1) if name_match else f"Province_{province_id}"
            
            deep_debug_province(province_content, province_id, province_name)
            break  # 只分析第一个找到的中国省份

if __name__ == "__main__":
    main()
