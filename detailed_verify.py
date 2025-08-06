#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细验证脚本 - 检查具体哪里不对
"""

import re

def detailed_verification():
    """详细验证意识形态修改"""
    
    print("🔍 详细验证意识形态修改")
    print("=" * 50)
    
    filename = 'China1837_01_24.v2'
    
    # 读取文件
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        print(f"✅ 文件读取成功，大小: {len(content):,}")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    print("📋 意识形态ID对照表:")
    ideology_names = {
        1: "Reactionary(反动派)",
        2: "Fascist(法西斯)",
        3: "Conservative(保守派)",
        4: "Socialist(社会主义)",
        5: "Anarcho-Liberal(无政府自由主义)",
        6: "Liberal(自由派)",
        7: "Communist(共产主义)"
    }
    
    for id_num, name in ideology_names.items():
        print(f"  {id_num} = {name}")
    
    print(f"\n🎯 转换规则:")
    print(f"  Reactionary(1) + Socialist(4) + Communist(7) → Conservative(3)")
    print(f"  Fascist(2) + Anarcho-Liberal(5) → Liberal(6)")
    
    print(f"\n🔍 检查具体省份...")
    
    # 检查几个关键省份
    key_provinces = [1, 2, 5, 10, 15, 20]
    
    total_ideology_blocks = 0
    problem_blocks = 0
    
    for province_id in key_provinces:
        # 查找省份
        province_pattern = f'^{province_id}=\\s*{{'
        province_match = re.search(province_pattern, content, re.MULTILINE)
        
        if not province_match:
            continue
        
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
        
        # 查找该省份中的ideology块
        ideology_pattern = r'ideology=\s*\{([^}]*)\}'
        ideology_matches = list(re.finditer(ideology_pattern, province_content, re.DOTALL))
        
        print(f"\n省份 {province_id}: {len(ideology_matches)} 个意识形态块")
        
        for i, match in enumerate(ideology_matches):
            total_ideology_blocks += 1
            ideology_content = match.group(1)
            
            # 解析意识形态数据
            ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
            ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
            
            # 检查所有意识形态
            print(f"  块{i+1}:")
            for id_num in range(1, 8):
                value = ideology_dist.get(id_num, 0)
                name = ideology_names.get(id_num, f"未知{id_num}")
                if value > 0.01:  # 只显示有意义的值
                    print(f"    {name}: {value:.2f}%")
            
            # 检查问题
            old_ideologies = [1, 2, 4, 5, 7]
            has_old_values = any(ideology_dist.get(old_id, 0) > 0.01 for old_id in old_ideologies)
            
            if has_old_values:
                problem_blocks += 1
                print(f"    ❌ 仍有旧意识形态值！")
                old_values = {id_val: ideology_dist.get(id_val, 0) for id_val in old_ideologies if ideology_dist.get(id_val, 0) > 0.01}
                print(f"    问题值: {old_values}")
            else:
                # 检查是否正确转换到Conservative和Liberal
                conservative = ideology_dist.get(3, 0)
                liberal = ideology_dist.get(6, 0)
                total_new = conservative + liberal
                
                if total_new < 50:  # 如果新意识形态总和太低，可能有问题
                    print(f"    ⚠️ 新意识形态总和较低: {total_new:.2f}%")
                else:
                    print(f"    ✅ 转换正确")
    
    print(f"\n📊 总结:")
    print(f"检查的意识形态块: {total_ideology_blocks}")
    print(f"有问题的块: {problem_blocks}")
    print(f"成功率: {((total_ideology_blocks-problem_blocks)/total_ideology_blocks*100):.1f}%" if total_ideology_blocks > 0 else "N/A")
    
    if problem_blocks == 0:
        print("🎉 所有检查的意识形态块都已正确转换！")
        print("\n可能的问题:")
        print("1. 游戏需要重新加载存档才能看到变化")
        print("2. 你期望的是不同的意识形态分配")
        print("3. 你查看的是非中国省份(修改只影响中国省份)")
        print("4. 你期望的是其他特定的意识形态(如Reactionary等)")
    else:
        print("⚠️ 发现问题块，需要进一步修复")

if __name__ == "__main__":
    detailed_verification()
