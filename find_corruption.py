#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找存档文件损坏的原因
比较备份文件和当前文件，找出不应该存在的修改
"""

import re
import sys

def load_file(filename):
    """加载文件内容"""
    try:
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding, errors='ignore') as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return None
    except Exception as e:
        print(f"❌ 读取文件失败 {filename}: {e}")
        return None

def find_chi_block(content):
    """查找CHI国家块"""
    # 精确查找CHI=开头的国家定义（作为完整词）
    china_start_pattern = r'\bCHI=\s*\{'
    china_start_match = re.search(china_start_pattern, content, re.MULTILINE)
    
    if not china_start_match:
        return None, 0, 0
    
    start_pos = china_start_match.start()
    
    # 找到CHI块的结束位置 - 查找下一个顶级国家定义
    next_country_pattern = r'\n[A-Z]{3}=\s*{'
    next_country_match = re.search(next_country_pattern, content[start_pos + 100:])
    
    if next_country_match:
        end_pos = start_pos + 100 + next_country_match.start()
    else:
        end_pos = len(content)
    
    return content[start_pos:end_pos], start_pos, end_pos

def analyze_chi_differences(backup_file, current_file):
    """分析CHI块的差异"""
    print("正在分析CHI国家块差异...")
    
    backup_content = load_file(backup_file)
    current_content = load_file(current_file)
    
    if not backup_content or not current_content:
        print("❌ 无法读取文件")
        return
    
    # 获取CHI块
    backup_chi, backup_start, backup_end = find_chi_block(backup_content)
    current_chi, current_start, current_end = find_chi_block(current_content)
    
    if not backup_chi or not current_chi:
        print("❌ 无法找到CHI块")
        return
    
    print(f"备份文件CHI块: 位置 {backup_start}-{backup_end}, 大小 {len(backup_chi):,}")
    print(f"当前文件CHI块: 位置 {current_start}-{current_end}, 大小 {len(current_chi):,}")
    
    # 比较CHI块内容
    if backup_chi == current_chi:
        print("✅ CHI块内容相同")
    else:
        print("❌ CHI块内容不同")
        
        # 分析具体差异
        backup_lines = backup_chi.split('\n')
        current_lines = current_chi.split('\n')
        
        print(f"\n备份文件CHI块行数: {len(backup_lines)}")
        print(f"当前文件CHI块行数: {len(current_lines)}")
        
        # 找出不同的行
        max_lines = max(len(backup_lines), len(current_lines))
        differences = []
        
        for i in range(max_lines):
            backup_line = backup_lines[i] if i < len(backup_lines) else "[缺失]"
            current_line = current_lines[i] if i < len(current_lines) else "[缺失]"
            
            if backup_line != current_line:
                differences.append((i, backup_line, current_line))
        
        print(f"\n发现 {len(differences)} 处差异:")
        for i, (line_num, backup_line, current_line) in enumerate(differences[:10]):  # 只显示前10个差异
            print(f"{i+1}. 行{line_num+1}:")
            print(f"   备份: {backup_line[:100]}...")
            print(f"   当前: {current_line[:100]}...")
    
    return backup_chi, current_chi

def check_file_structure(backup_file, current_file):
    """检查文件整体结构"""
    print("\n正在检查文件整体结构...")
    
    backup_content = load_file(backup_file)
    current_content = load_file(current_file)
    
    if not backup_content or not current_content:
        return
    
    print(f"备份文件大小: {len(backup_content):,} 字符")
    print(f"当前文件大小: {len(current_content):,} 字符")
    print(f"大小差异: {len(current_content) - len(backup_content):+,} 字符")
    
    # 检查是否有语法错误
    print("\n检查文件语法...")
    
    # 检查大括号匹配
    backup_open = backup_content.count('{')
    backup_close = backup_content.count('}')
    current_open = current_content.count('{')
    current_close = current_content.count('}')
    
    print(f"备份文件大括号: {backup_open} 开 / {backup_close} 闭 (差值: {backup_open - backup_close})")
    print(f"当前文件大括号: {current_open} 开 / {current_close} 闭 (差值: {current_open - current_close})")
    
    if (backup_open - backup_close) != (current_open - current_close):
        print("❌ 大括号匹配发生变化，可能导致语法错误!")
    
    # 检查国家代码格式
    backup_countries = len(re.findall(r'\n[A-Z]{3}=\s*{', backup_content))
    current_countries = len(re.findall(r'\n[A-Z]{3}=\s*{', current_content))
    
    print(f"备份文件国家数: {backup_countries}")
    print(f"当前文件国家数: {current_countries}")
    
    if backup_countries != current_countries:
        print("❌ 国家数量发生变化!")

def find_binary_differences(backup_file, current_file):
    """查找二进制差异位置"""
    print("\n正在查找具体差异位置...")
    
    backup_content = load_file(backup_file)
    current_content = load_file(current_file)
    
    if not backup_content or not current_content:
        return
    
    min_length = min(len(backup_content), len(current_content))
    differences = []
    
    # 找出所有不同的字符位置
    for i in range(min_length):
        if backup_content[i] != current_content[i]:
            # 找到差异的上下文
            start = max(0, i - 100)
            end = min(len(backup_content), i + 100)
            
            backup_context = backup_content[start:end]
            current_context = current_content[start:end] if i < len(current_content) else "[文件结束]"
            
            differences.append((i, backup_context, current_context))
            
            # 只记录前5个差异点，避免输出过多
            if len(differences) >= 5:
                break
    
    # 检查长度差异
    if len(current_content) != len(backup_content):
        length_diff_pos = min_length
        print(f"文件长度差异开始位置: {length_diff_pos}")
        
        if len(current_content) > len(backup_content):
            extra_content = current_content[min_length:min_length+200]
            print(f"额外内容: {repr(extra_content)}")
    
    print(f"发现 {len(differences)} 个差异点:")
    for i, (pos, backup_ctx, current_ctx) in enumerate(differences):
        print(f"\n差异 {i+1} (位置 {pos}):")
        print(f"备份: {repr(backup_ctx)}")
        print(f"当前: {repr(current_ctx)}")

def main():
    backup_file = "China2281_01_01_selective_backup_20250728_213116.v2"
    current_file = "China2281_01_01.v2"
    
    print("=" * 70)
    print("存档文件损坏分析")
    print("=" * 70)
    print(f"备份文件: {backup_file}")
    print(f"当前文件: {current_file}")
    
    # 1. 检查文件整体结构
    check_file_structure(backup_file, current_file)
    
    # 2. 分析CHI块差异
    backup_chi, current_chi = analyze_chi_differences(backup_file, current_file)
    
    # 3. 查找具体差异位置
    find_binary_differences(backup_file, current_file)
    
    print("\n" + "=" * 70)
    print("分析完成")

if __name__ == "__main__":
    main()
