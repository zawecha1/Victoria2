#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找修改过程中的花括号丢失问题
"""

def analyze_modifications():
    """分析修改过程中的问题"""
    
    # 读取文件
    original_file = "China1841_12_17_selective_backup_20250806_015342.v2"
    modified_file = "China1841_12_17.v2"
    
    encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252']
    
    original_content = None
    modified_content = None
    
    # 读取原始文件
    for encoding in encodings:
        try:
            with open(original_file, 'r', encoding=encoding) as f:
                original_content = f.read()
            print(f"✅ 原始文件编码: {encoding}")
            break
        except:
            continue
    
    # 读取修改文件
    for encoding in encodings:
        try:
            with open(modified_file, 'r', encoding=encoding) as f:
                modified_content = f.read()
            print(f"✅ 修改文件编码: {encoding}")
            break
        except:
            continue
    
    if not original_content or not modified_content:
        print("❌ 无法读取文件")
        return
    
    print(f"\n📊 基本统计:")
    print(f"原始文件: {len(original_content):,} 字符")
    print(f"修改文件: {len(modified_content):,} 字符")
    print(f"差异: {len(modified_content) - len(original_content):+,} 字符")
    
    print(f"\n🔍 花括号统计:")
    orig_open = original_content.count('{')
    orig_close = original_content.count('}')
    mod_open = modified_content.count('{')
    mod_close = modified_content.count('}')
    
    print(f"原始: {{ {orig_open}, }} {orig_close} (差异: {orig_open - orig_close})")
    print(f"修改: {{ {mod_open}, }} {mod_close} (差异: {mod_open - mod_close})")
    print(f"丢失: {{ {orig_open - mod_open}, }} {orig_close - mod_close}")
    
    # 查找第一个差异位置
    print(f"\n🔍 查找第一个差异...")
    min_len = min(len(original_content), len(modified_content))
    
    for i in range(min_len):
        if original_content[i] != modified_content[i]:
            start = max(0, i - 200)
            end = min(len(original_content), i + 200)
            
            print(f"\n第一个差异在位置 {i}")
            print(f"原始内容:\n{repr(original_content[start:end])}")
            print(f"修改内容:\n{repr(modified_content[start:end])}")
            break
    else:
        if len(original_content) != len(modified_content):
            print(f"文件长度不同，差异在位置 {min_len}")
    
    # 检查宗教修改
    print(f"\n🔍 检查宗教修改...")
    mahayana_orig = original_content.count('mahayana')
    mahayana_mod = modified_content.count('mahayana')
    print(f"mahayana: 原始={mahayana_orig}, 修改={mahayana_mod}, 增加={mahayana_mod - mahayana_orig}")

if __name__ == "__main__":
    analyze_modifications()
