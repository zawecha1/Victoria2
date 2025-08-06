#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 检查最新的备份文件与当前文件的花括号平衡
def check_braces(filename):
    encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"文件: {filename}")
            print(f"编码: {encoding}")
            print(f"文件大小: {len(content):,} 字符")
            print(f"开括号: {content.count('{')}")
            print(f"闭括号: {content.count('}')}")
            print(f"差异: {content.count('{') - content.count('}')}")
            return
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"文件不存在: {filename}")
            return

# 检查两个文件
check_braces("China1836_04_17.v2")
print("-" * 50)
check_braces("China1836_04_17_manu_bak.v2")
