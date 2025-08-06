#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查修改后的文件是否有问题
"""

import re
import os

def quick_check():
    """快速检查文件"""
    
    original_file = r"z:\Users\Administrator\Documents\Paradox Interactive\Victoria II\save games\China1841_12_17_selective_backup_20250806_012240.v2"
    modified_file = r"z:\Users\Administrator\Documents\Paradox Interactive\Victoria II\save games\China1841_12_17.v2"
    
    print("=== 快速文件检查 ===")
    
    # 检查文件是否存在
    if not os.path.exists(original_file):
        print(f"❌ 原始文件不存在: {original_file}")
        return
        
    if not os.path.exists(modified_file):
        print(f"❌ 修改文件不存在: {modified_file}")
        return
    
    # 检查文件大小
    original_size = os.path.getsize(original_file)
    modified_size = os.path.getsize(modified_file)
    
    print(f"原始文件大小: {original_size:,} 字节")
    print(f"修改文件大小: {modified_size:,} 字节")
    print(f"大小差异: {modified_size - original_size:+,} 字节")
    
    # 如果大小差异过大，表示有问题
    if abs(modified_size - original_size) > 100000:
        print("⚠️ 警告: 文件大小差异过大!")
    
    # 快速读取文件开头检查编码
    try:
        print("\n检查文件编码...")
        with open(modified_file, 'r', encoding='utf-8-sig') as f:
            header = f.read(1000)
            if header:
                print("✅ 文件可以正常读取")
            else:
                print("❌ 文件为空或无法读取")
                
        # 检查花括号基本平衡
        print("\n检查花括号...")
        with open(modified_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            open_count = content.count('{')
            close_count = content.count('}')
            print(f"开括号: {open_count}, 闭括号: {close_count}")
            if open_count == close_count:
                print("✅ 花括号平衡")
            else:
                print(f"❌ 花括号不平衡，差异: {open_count - close_count}")
                
        # 检查省份数量
        print("\n检查省份结构...")
        province_pattern = re.compile(r'^\d+=\s*{', re.MULTILINE)
        provinces = province_pattern.findall(content)
        print(f"找到省份数量: {len(provinces)}")
        
        if len(provinces) == 0:
            print("❌ 错误: 没有找到任何省份!")
        elif len(provinces) < 2000:
            print("⚠️ 警告: 省份数量似乎偏少")
        else:
            print("✅ 省份数量正常")
            
        # 检查关键字段
        print("\n检查关键字段...")
        if 'CHI=' in content:
            print("✅ 找到CHI国家定义")
        else:
            print("❌ 错误: 没有找到CHI国家定义!")
            
        if 'mahayana' in content:
            print("✅ 找到mahayana宗教")
        else:
            print("⚠️ 没有找到mahayana宗教")
            
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")

if __name__ == "__main__":
    quick_check()
