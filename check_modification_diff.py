#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查修改前后文件的差异
找出中国人口属性修改功能的问题
"""

import re
import sys

def check_file_differences():
    """检查修改前后文件的关键差异"""
    
    # 文件路径
    original_file = "China1841_12_17_selective_backup_20250806_012240.v2"
    modified_file = "China1841_12_17.v2"
    
    print("🔍 检查文件修改差异...")
    print(f"原始文件: {original_file}")
    print(f"修改文件: {modified_file}")
    
    try:
        # 读取文件
        print("\n📖 读取原始文件...")
        with open(original_file, 'r', encoding='utf-8-sig') as f:
            original_content = f.read()
        
        print("📖 读取修改文件...")
        with open(modified_file, 'r', encoding='utf-8-sig') as f:
            modified_content = f.read()
        
        # 基本统计
        print(f"\n📊 文件大小对比:")
        print(f"原始文件: {len(original_content):,} 字符")
        print(f"修改文件: {len(modified_content):,} 字符")
        print(f"差异: {len(modified_content) - len(original_content):+,} 字符")
        
        # 检查是否有严重的结构问题
        if abs(len(modified_content) - len(original_content)) > 100000:
            print("⚠️ 警告: 文件大小差异过大，可能存在严重问题!")
        
        # 检查宗教修改
        print(f"\n🔍 检查宗教修改...")
        original_mahayana = len(re.findall(r'mahayana', original_content))
        modified_mahayana = len(re.findall(r'mahayana', modified_content))
        print(f"原始文件中的 mahayana: {original_mahayana}")
        print(f"修改文件中的 mahayana: {modified_mahayana}")
        print(f"新增 mahayana: {modified_mahayana - original_mahayana}")
        
        # 检查意识形态修改
        print(f"\n🔍 检查意识形态修改...")
        ideology_patterns = {
            'Conservative(3)': r'3=([\d.]+)',
            'Liberal(6)': r'6=([\d.]+)',
            'Reactionary(1)': r'1=([\d.]+)',
            'Socialist(4)': r'4=([\d.]+)',
            'Communist(7)': r'7=([\d.]+)',
            'Fascist(2)': r'2=([\d.]+)',
            'Anarcho-Liberal(5)': r'5=([\d.]+)'
        }
        
        for name, pattern in ideology_patterns.items():
            original_matches = re.findall(pattern, original_content)
            modified_matches = re.findall(pattern, modified_content)
            
            # 统计非零值
            original_nonzero = len([m for m in original_matches if float(m) > 0])
            modified_nonzero = len([m for m in modified_matches if float(m) > 0])
            
            print(f"{name}: 原始={original_nonzero}, 修改={modified_nonzero}, 差异={modified_nonzero - original_nonzero}")
        
        # 检查花括号平衡
        print(f"\n🔍 检查花括号平衡...")
        original_open = original_content.count('{')
        original_close = original_content.count('}')
        modified_open = modified_content.count('{')
        modified_close = modified_content.count('}')
        
        print(f"原始文件: {{ {original_open}, }} {original_close}, 平衡: {original_open == original_close}")
        print(f"修改文件: {{ {modified_open}, }} {modified_close}, 平衡: {modified_open == modified_close}")
        
        if modified_open != modified_close:
            print("❌ 错误: 修改后文件花括号不平衡!")
            print(f"差异: {modified_open - modified_close}")
            return False
        
        # 检查具体的差异位置
        print(f"\n🔍 查找第一个差异位置...")
        for i, (orig_char, mod_char) in enumerate(zip(original_content, modified_content)):
            if orig_char != mod_char:
                start = max(0, i - 100)
                end = min(len(original_content), i + 100)
                
                print(f"第一个差异在位置 {i}")
                print(f"原始内容上下文:\n{original_content[start:end]}")
                print(f"修改内容上下文:\n{modified_content[start:end]}")
                break
        else:
            if len(original_content) != len(modified_content):
                print(f"文件长度不同: 原始={len(original_content)}, 修改={len(modified_content)}")
            else:
                print("✅ 文件内容完全相同")
        
        # 检查省份结构
        print(f"\n🔍 检查省份结构...")
        original_provinces = len(re.findall(r'^\d+=\s*{', original_content, re.MULTILINE))
        modified_provinces = len(re.findall(r'^\d+=\s*{', modified_content, re.MULTILINE))
        print(f"原始省份数: {original_provinces}")
        print(f"修改省份数: {modified_provinces}")
        
        if original_provinces != modified_provinces:
            print("❌ 错误: 省份数量发生变化!")
            return False
        
        print(f"\n✅ 基本检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        return False

if __name__ == "__main__":
    success = check_file_differences()
    sys.exit(0 if success else 1)
