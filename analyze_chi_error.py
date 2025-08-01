#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细分析CHI块的错误修改
"""

import re

def load_file(filename):
    """加载文件内容"""
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None

def find_chi_block_detailed(content):
    """详细查找CHI块"""
    # 查找所有CHI=模式
    chi_patterns = list(re.finditer(r'\bCHI=\s*\{', content, re.MULTILINE))
    
    print(f"找到 {len(chi_patterns)} 个CHI=模式:")
    
    for i, match in enumerate(chi_patterns):
        start_pos = match.start()
        # 获取上下文
        context_start = max(0, start_pos - 200)
        context_end = min(len(content), start_pos + 300)
        context = content[context_start:context_end]
        
        print(f"\nCHI={i+1} (位置 {start_pos}):")
        print("上下文:")
        print(repr(context))

def main():
    backup_file = "China2281_01_01_selective_backup_20250728_213116.v2"
    current_file = "China2281_01_01.v2"
    
    print("=" * 70)
    print("详细分析CHI块修改错误")
    print("=" * 70)
    
    backup_content = load_file(backup_file)
    current_content = load_file(current_file)
    
    if not backup_content or not current_content:
        return
    
    print("备份文件中的CHI块:")
    find_chi_block_detailed(backup_content)
    
    print("\n" + "=" * 50)
    print("当前文件中的CHI块:")
    find_chi_block_detailed(current_content)

if __name__ == "__main__":
    main()
