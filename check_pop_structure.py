#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入检查人口块的完整结构
"""

import re

def check_population_structure():
    """检查人口块的完整结构"""
    
    print("🔍 检查人口块的完整结构")
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
    
    # 查找省份1
    province_pattern = r'^1=\s*{'
    province_match = re.search(province_pattern, content, re.MULTILINE)
    
    if not province_match:
        print("❌ 未找到省份1")
        return
    
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
    
    # 查找第一个人口块
    pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                'bureaucrats', 'intellectuals']
    
    for pop_type in pop_types:
        pattern = f'{pop_type}=\\s*{{[^}}]*}}'
        pop_match = re.search(pattern, province_content, re.DOTALL)
        
        if pop_match:
            pop_block = pop_match.group(0)
            print(f"\n📋 找到 {pop_type} 人口块:")
            print(f"完整内容:")
            print(pop_block)
            
            # 分析所有属性
            print(f"\n📊 分析属性:")
            
            # 查找所有 key=value 模式
            attribute_pattern = r'([a-zA-Z_]+)=([\d.]+|[a-zA-Z_]+|\{[^}]*\})'
            attributes = re.findall(attribute_pattern, pop_block, re.DOTALL)
            
            for attr_name, attr_value in attributes:
                # 清理多行值
                clean_value = attr_value.strip()
                if '\n' in clean_value:
                    clean_value = clean_value.replace('\n', ' ').replace('\t', ' ')
                    clean_value = re.sub(r'\s+', ' ', clean_value)
                    if len(clean_value) > 50:
                        clean_value = clean_value[:50] + "..."
                
                print(f"  {attr_name} = {clean_value}")
            
            break
    
    # 搜索可能与斗争性相关的词汇
    print(f"\n🔍 搜索可能与斗争性相关的词汇...")
    
    militancy_related = ['militancy', 'militant', 'rebel', 'revolt', 'unrest', 
                        'consciousness', 'loyalty', 'loyalty_value', 'loyalty_factor',
                        'happiness', 'anger', 'discontent', 'satisfaction']
    
    for term in militancy_related:
        if term in content.lower():
            print(f"  ✅ 找到 '{term}'")
            
            # 查找第一个匹配的上下文
            pattern = f'{term}[=\\s]*[\\d\\.]+'
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            count = 0
            for match in matches:
                if count >= 3:  # 只显示前3个匹配
                    break
                    
                start = max(0, match.start() - 30)
                end = min(len(content), match.end() + 30)
                context = content[start:end].replace('\n', ' ').replace('\t', ' ')
                context = re.sub(r'\s+', ' ', context)
                
                print(f"    匹配{count+1}: ...{context}...")
                count += 1
        else:
            print(f"  ❌ 未找到 '{term}'")

if __name__ == "__main__":
    check_population_structure()
