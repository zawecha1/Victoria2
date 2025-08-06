#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断意识形态修改问题的专用脚本
"""

import re
import sys
from victoria2_main_modifier import Victoria2Modifier

def diagnose_ideology_problem():
    """诊断意识形态修改问题"""
    
    print("🔬 诊断意识形态修改问题")
    print("=" * 50)
    
    # 直接读取文件内容
    filename = 'autosave.v2'
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        print(f"✅ 文件读取成功，大小: {len(content):,} 字符")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 查找一个具体的意识形态块来测试
    print("\n🔍 查找具体的意识形态块...")
    
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
    print(f"✅ 提取省份内容，大小: {len(province_content):,} 字符")
    
    # 查找意识形态块
    ideology_pattern = r'ideology=\s*\{([^}]*)\}'
    ideology_matches = list(re.finditer(ideology_pattern, province_content, re.DOTALL))
    
    print(f"📊 找到 {len(ideology_matches)} 个意识形态块")
    
    if not ideology_matches:
        print("❌ 未找到意识形态块")
        return
    
    # 分析第一个意识形态块
    first_match = ideology_matches[0]
    ideology_content = first_match.group(1)
    
    print(f"\n📋 第一个意识形态块:")
    print(f"原始内容:")
    print(repr(ideology_content))
    print(f"显示内容:")
    print(ideology_content)
    
    # 解析意识形态数据
    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
    ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
    
    print(f"\n📊 解析结果: {ideology_dist}")
    
    # 检查是否有旧意识形态
    old_ideologies = [1, 2, 4, 5, 7]
    has_old = any(ideology_dist.get(old_id, 0) > 0 for old_id in old_ideologies)
    
    print(f"🎯 是否有旧意识形态: {has_old}")
    
    if has_old:
        print("发现旧意识形态，测试转换...")
        
        # 创建修改器实例
        modifier = Victoria2Modifier(debug_mode=True)
        
        # 测试转换函数
        new_content = modifier._modify_ideology_distribution(ideology_content)
        
        print(f"\n转换后内容:")
        print(repr(new_content))
        
        # 测试完整的人口块修改
        print(f"\n🧪 测试完整人口块修改...")
        
        # 查找包含这个意识形态块的人口组
        pop_pattern = r'(farmers|labourers|clerks|artisans|craftsmen|clergymen|officers|soldiers|aristocrats|capitalists|bureaucrats|intellectuals)=\s*\{[^}]*ideology=\s*\{[^}]*\}[^}]*\}'
        pop_matches = list(re.finditer(pop_pattern, province_content, re.DOTALL))
        
        print(f"找到 {len(pop_matches)} 个人口组")
        
        if pop_matches:
            first_pop = pop_matches[0]
            pop_content = first_pop.group(0)
            
            print(f"\n第一个人口组 (长度: {len(pop_content)}):")
            print(pop_content[:500] + "..." if len(pop_content) > 500 else pop_content)
            
            # 测试人口组修改
            modified_pop = modifier._modify_single_population_structured(pop_content)
            
            print(f"\n修改后是否改变: {modified_pop != pop_content}")
            if modified_pop != pop_content:
                print("✅ 人口组内容已修改")
                
                # 显示差异
                print("\n📋 修改前后的意识形态差异:")
                old_ideology = re.search(r'ideology=\s*\{([^}]*)\}', pop_content, re.DOTALL)
                new_ideology = re.search(r'ideology=\s*\{([^}]*)\}', modified_pop, re.DOTALL)
                
                if old_ideology and new_ideology:
                    print("修改前:")
                    print(old_ideology.group(1))
                    print("修改后:")
                    print(new_ideology.group(1))
            else:
                print("❌ 人口组内容未修改")
    else:
        print("✅ 该意识形态块无需转换")

if __name__ == "__main__":
    diagnose_ideology_problem()
