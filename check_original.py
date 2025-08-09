#!/usr/bin/env python3
"""
检查原始文件的完整性
"""

import re

def check_original_file():
    filename = 'China1839_08_08_unified_backup_20250808_001305.v2'
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        print(f"文件: {filename}")
        print(f"大小: {len(content):,} 字符")
        print(f"开括号: {open_braces}")
        print(f"闭括号: {close_braces}")
        print(f"平衡: {'✅ 平衡' if open_braces == close_braces else '❌ 不平衡'}")
        
        # 检查结构问题
        triple_close = len(re.findall(r'\}\s*\}\s*\}', content))
        quad_close = len(re.findall(r'\}\s*\}\s*\}\s*\}', content))
        
        print(f"三重闭括号: {triple_close}")
        print(f"四重闭括号: {quad_close}")
        
        # 检查人口数据
        size_matches = re.findall(r'size\s*=\s*([\d.]+)', content)
        sizes = [float(x) for x in size_matches if float(x) > 0]
        
        print(f"size字段总数: {len(size_matches)}")
        print(f"非零人口数: {len(sizes)}")
        print(f"总人口: {sum(sizes):,.0f}")
        
        # 检查civilized状态
        civilized_no = len(re.findall(r'civilized\s*=\s*"?no"?', content))
        print(f"civilized='no' 数量: {civilized_no}")
        
        return len(content), open_braces == close_braces, triple_close == 0
        
    except Exception as e:
        print(f"错误: {e}")
        return None, False, False

if __name__ == "__main__":
    check_original_file()
