#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 快速检查花括号平衡
def check_braces(filename):
    encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"文件: {filename}")
            print(f"编码: {encoding}")
            print(f"开括号: {content.count('{')}")
            print(f"闭括号: {content.count('}')}")
            print(f"差异: {content.count('{') - content.count('}')}")
            return
        except UnicodeDecodeError:
            continue

# 检查两个文件
check_braces("China1841_12_17.v2")
print("-" * 40)
check_braces("China1841_12_17_selective_backup_20250806_012240.v2")
