#!/usr/bin/env python3
"""
检查文件编码和具体的格式问题
"""

import os
import chardet

def check_file_encoding():
    """检查文件编码"""
    print("🔍 检查文件编码")
    print("="*60)
    
    files = [
        "China1839_08_08_unified_backup_20250808_001305.v2",  # 原始
        "autosave.v2"  # 修改后
    ]
    
    for filename in files:
        if not os.path.exists(filename):
            continue
            
        print(f"\n📄 {filename}:")
        
        # 检查文件编码
        with open(filename, 'rb') as f:
            raw_data = f.read(10000)  # 读取前10K字节
            encoding_result = chardet.detect(raw_data)
            print(f"  编码检测: {encoding_result}")
        
        # 检查BOM
        with open(filename, 'rb') as f:
            first_bytes = f.read(3)
            if first_bytes == b'\xef\xbb\xbf':
                print(f"  BOM: UTF-8 BOM")
            elif first_bytes[:2] == b'\xff\xfe':
                print(f"  BOM: UTF-16 LE BOM")
            elif first_bytes[:2] == b'\xfe\xff':
                print(f"  BOM: UTF-16 BE BOM")
            else:
                print(f"  BOM: 无BOM")
        
        # 检查文件结尾
        with open(filename, 'rb') as f:
            f.seek(-100, 2)  # 移到文件末尾前100字节
            end_data = f.read()
            print(f"  文件结尾: {repr(end_data[-20:])}")
        
        # 使用不同编码方式读取文件，看是否有差异
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    size = len(content)
                    print(f"  {encoding}: {size:,} 字符")
            except Exception as e:
                print(f"  {encoding}: 读取失败 - {e}")

def check_specific_differences():
    """检查具体的差异"""
    print(f"\n" + "="*60)
    print("🔍 检查具体差异")
    print("="*60)
    
    try:
        # 读取两个文件
        with open("China1839_08_08_unified_backup_20250808_001305.v2", 'r', encoding='utf-8-sig', errors='ignore') as f:
            original_content = f.read()
        
        with open("autosave.v2", 'r', encoding='utf-8-sig', errors='ignore') as f:
            modified_content = f.read()
        
        print(f"原始文件大小: {len(original_content):,}")
        print(f"修改文件大小: {len(modified_content):,}")
        print(f"大小差异: {len(modified_content) - len(original_content):+,}")
        
        # 查找第一个不同的位置
        min_len = min(len(original_content), len(modified_content))
        first_diff = -1
        
        for i in range(min_len):
            if original_content[i] != modified_content[i]:
                first_diff = i
                break
        
        if first_diff >= 0:
            print(f"\n第一个差异位置: {first_diff}")
            start = max(0, first_diff - 50)
            end = min(len(original_content), first_diff + 50)
            
            print(f"原始文件上下文:")
            print(repr(original_content[start:end]))
            
            print(f"修改文件上下文:")
            print(repr(modified_content[start:end]))
        else:
            print(f"没有找到字符级别的差异")
        
        # 检查文件是否被截断
        if len(modified_content) < len(original_content):
            print(f"❌ 修改后的文件被截断了！少了 {len(original_content) - len(modified_content):,} 字符")
        elif len(modified_content) > len(original_content):
            print(f"✅ 修改后的文件增大了 {len(modified_content) - len(original_content):,} 字符")
            
    except Exception as e:
        print(f"❌ 比较文件时出错: {e}")

if __name__ == "__main__":
    check_file_encoding()
    check_specific_differences()
