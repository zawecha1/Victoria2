#!/usr/bin/env python3
"""
快速检查文明化状态
"""

import re

def quick_check():
    with open('autosave.v2', 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # 简单的正则匹配
    civilized_no = content.count('civilized="no"')
    civilized_yes = content.count('civilized="yes"')
    civilized_no_unquoted = content.count('civilized=no')
    civilized_yes_unquoted = content.count('civilized=yes')
    
    print("🔍 文明化状态统计:")
    print(f"  civilized=\"no\": {civilized_no}")
    print(f"  civilized=\"yes\": {civilized_yes}")
    print(f"  civilized=no: {civilized_no_unquoted}")
    print(f"  civilized=yes: {civilized_yes_unquoted}")
    
    # 检查中国
    chi_pattern = r'CHI\s*=\s*\{[^{}]*?civilized\s*=\s*"?([^"\s}]+)"?'
    chi_match = re.search(chi_pattern, content, re.DOTALL)
    
    if chi_match:
        print(f"🇨🇳 中国状态: {chi_match.group(1)}")
    else:
        print("❌ 未找到中国的文明化状态")

if __name__ == "__main__":
    quick_check()
