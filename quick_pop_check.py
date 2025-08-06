#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查人口块识别问题
"""

import re

def quick_population_check():
    """快速检查人口块识别"""
    
    print("⚡ 快速检查人口块识别")
    print("=" * 40)
    
    filename = 'China1837_01_24.v2'
    
    # 直接读取文件找省份1
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
    
    print("✅ 找到省份1")
    
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
    print(f"✅ 提取省份1内容，长度: {len(province_content):,}")
    
    # 人口类型列表
    pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                'bureaucrats', 'intellectuals']
    
    # 查找人口类型
    found_populations = []
    for pop_type in pop_types:
        pattern = f'{pop_type}='
        if pattern in province_content:
            found_populations.append(pop_type)
            print(f"  ✅ 找到人口类型: {pop_type}")
    
    if not found_populations:
        print("❌ 未找到任何人口类型")
        print("🔍 检查省份内容的前1000个字符:")
        print(province_content[:1000])
        return
    
    print(f"\n📊 找到 {len(found_populations)} 种人口类型: {found_populations}")
    
    # 查找第一种人口类型的完整块
    first_pop_type = found_populations[0]
    pattern = f'{first_pop_type}=\\s*{{[^}}]*}}'
    pop_match = re.search(pattern, province_content, re.DOTALL)
    
    if pop_match:
        pop_block = pop_match.group(0)
        print(f"\n📋 {first_pop_type} 块:")
        print(f"长度: {len(pop_block)}")
        print(f"内容:")
        print(pop_block)
        
        # 检查是否包含ideology
        if 'ideology=' in pop_block:
            print(f"✅ {first_pop_type} 块包含ideology")
            
            # 提取ideology部分
            ideology_pattern = r'ideology=\s*\{([^}]*)\}'
            ideology_match = re.search(ideology_pattern, pop_block, re.DOTALL)
            
            if ideology_match:
                ideology_content = ideology_match.group(1)
                print(f"📊 Ideology内容:")
                print(repr(ideology_content))
                
                # 解析意识形态
                ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
                ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
                print(f"解析结果: {ideology_dist}")
                
                # 检查是否需要转换
                old_ideologies = [1, 2, 4, 5, 7]
                needs_conversion = any(ideology_dist.get(old_id, 0) > 0 for old_id in old_ideologies)
                print(f"需要转换: {needs_conversion}")
        else:
            print(f"❌ {first_pop_type} 块不包含ideology")
    else:
        print(f"❌ 无法提取 {first_pop_type} 的完整块")

if __name__ == "__main__":
    quick_population_check()
