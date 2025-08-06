#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查斗争性的实际格式
"""

import re

def check_militancy_format():
    """检查斗争性的实际格式"""
    
    print("🔍 检查斗争性的实际格式")
    print("=" * 50)
    
    filename = 'China1837_01_24.v2'
    
    # 读取文件
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        print(f"✅ 文件读取成功")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 搜索包含militancy的所有行
    print("\n🔍 搜索包含'militancy'的行...")
    
    lines = content.split('\n')
    militancy_lines = []
    
    for i, line in enumerate(lines):
        if 'militancy' in line.lower():
            militancy_lines.append((i+1, line.strip()))
            if len(militancy_lines) >= 20:  # 限制输出
                break
    
    if militancy_lines:
        print(f"找到 {len(militancy_lines)} 行包含'militancy':")
        for line_num, line_content in militancy_lines:
            print(f"  行{line_num}: {line_content}")
    else:
        print("❌ 没有找到包含'militancy'的行")
        
        # 尝试搜索相关词汇
        print("\n🔍 尝试搜索相关词汇...")
        
        related_terms = ['militant', 'combat', 'fighting', 'rebel', 'revolt']
        for term in related_terms:
            if term in content.lower():
                print(f"  ✅ 找到 '{term}'")
                # 显示第一个匹配的上下文
                pos = content.lower().find(term)
                start = max(0, pos - 50)
                end = min(len(content), pos + 100)
                context = content[start:end]
                print(f"    上下文: {repr(context)}")
                break
            else:
                print(f"  ❌ 未找到 '{term}'")
    
    # 检查省份1的结构，看看人口数据的格式
    print(f"\n🔍 检查省份1的人口数据格式...")
    
    province_pattern = r'^1=\s*{'
    province_match = re.search(province_pattern, content, re.MULTILINE)
    
    if province_match:
        # 提取省份内容
        start_pos = province_match.end()
        brace_count = 1
        current_pos = start_pos
        while current_pos < len(content) and brace_count > 0:
            char = content[current_pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            current_pos += 1
        
        province_content = content[start_pos:current_pos-1]
        
        # 查找人口类型
        pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                    'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                    'bureaucrats', 'intellectuals']
        
        for pop_type in pop_types:
            if pop_type in province_content:
                print(f"  ✅ 找到人口类型: {pop_type}")
                
                # 提取这个人口类型的完整块
                pattern = f'{pop_type}=\\s*{{[^}}]*}}'
                pop_match = re.search(pattern, province_content, re.DOTALL)
                
                if pop_match:
                    pop_block = pop_match.group(0)
                    print(f"  人口块长度: {len(pop_block)}")
                    
                    # 显示前500个字符
                    preview = pop_block[:500] + "..." if len(pop_block) > 500 else pop_block
                    print(f"  内容预览:")
                    print(f"  {preview}")
                    
                    # 检查是否有数字等号的模式（可能是斗争性）
                    numeric_patterns = re.findall(r'([a-zA-Z_]+)=([\d.]+)', pop_block)
                    print(f"  找到的数值属性:")
                    for attr_name, attr_value in numeric_patterns:
                        print(f"    {attr_name}={attr_value}")
                
                break

if __name__ == "__main__":
    check_militancy_format()
