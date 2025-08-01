#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
政党信息搜索工具
用于查找Victoria II存档中的政党定义
"""

import re
from pathlib import Path


def search_party_definitions(save_file_path: str):
    """搜索所有政党定义"""
    
    with open(save_file_path, 'r', encoding='latin-1') as f:
        content = f.read()
    
    print("搜索政党定义...")
    
    # 查找可能的政党定义模式
    patterns = [
        r'(\d+)=\s*\{[^}]*name="([^"]*)"[^}]*\}',  # 标准政党定义
        r'party=\s*\{[^}]*name="([^"]*)"[^}]*\}',   # 政党块
        r'name="([^"]*)"[^}]*religious_policy="([^"]*)"',  # 含宗教政策的名称
    ]
    
    for i, pattern in enumerate(patterns):
        print(f"\n--- 模式 {i+1}: {pattern} ---")
        matches = list(re.finditer(pattern, content, re.DOTALL))
        print(f"找到 {len(matches)} 个匹配项")
        
        for j, match in enumerate(matches[:5]):  # 只显示前5个
            print(f"匹配 {j+1}: {match.group(0)[:200]}...")
    
    # 专门搜索1431相关的内容
    print(f"\n--- 搜索ID为1431的内容 ---")
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        if '1431' in line and ('=' in line or '{' in line):
            start = max(0, line_num - 3)
            end = min(len(lines), line_num + 3)
            print(f"\n行 {line_num}: {line.strip()}")
            print("上下文:")
            for ctx_line_num in range(start, end):
                marker = ">>> " if ctx_line_num == line_num - 1 else "    "
                print(f"{marker}{ctx_line_num + 1}: {lines[ctx_line_num].strip()}")
    
    # 搜索政党相关的字段
    print(f"\n--- 搜索政党相关字段 ---")
    party_fields = [
        'religious_policy=',
        'name="zhiqiang"',
        'secularized',
        'atheism',
        'party=',
        'active_party=',
        'ruling_party='
    ]
    
    for field in party_fields:
        matches = []
        for line_num, line in enumerate(lines, 1):
            if field in line:
                matches.append((line_num, line.strip()))
        
        if matches:
            print(f"\n{field}: {len(matches)} 个匹配项")
            for line_num, line in matches[:3]:  # 显示前3个
                print(f"  行 {line_num}: {line}")


def main():
    save_file = "China1836_04_29.v2"
    search_party_definitions(save_file)


if __name__ == "__main__":
    main()
