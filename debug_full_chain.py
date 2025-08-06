#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：追踪意识形态修改的完整调用链路
"""

import sys
import os
import re

# 添加模块路径
sys.path.append(r'z:\Users\Administrator\Documents\Paradox Interactive\Victoria II\save games')

from victoria2_main_modifier import Victoria2Modifier

def debug_full_ideology_chain():
    """完整调试意识形态修改调用链路"""
    print("🔍 开始完整调试意识形态修改调用链路...")
    
    # 初始化修改器
    modifier = Victoria2Modifier(debug_mode=True)
    
    # 测试文件路径 - 使用备份文件测试
    test_file = r'z:\Users\Administrator\Documents\Paradox Interactive\Victoria II\save games\China1836_02_20_unified_backup_20250806_022505.v2'
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    print(f"📂 加载测试文件: {test_file}")
    if not modifier.load_file(test_file):
        print("❌ 文件加载失败")
        return
    
    # 步骤1：检查初始状态
    print("\n🔍 步骤1：检查初始化状态...")
    print(f"  文件大小: {len(modifier.content):,} 字符")
    print(f"  结构已初始化: {modifier.structure is not None}")
    
    # 步骤2：查找中国省份（结构化方法）
    print("\n🔍 步骤2：查找中国省份...")
    chinese_provinces = modifier.find_chinese_provinces_structured()
    print(f"  找到中国省份数量: {len(chinese_provinces)}")
    
    if len(chinese_provinces) == 0:
        print("❌ 未找到任何中国省份，检查省份ID范围...")
        # 查看是否有任何以CHI为owner的省份
        chi_blocks = re.findall(r'(\d+)=\s*\{[^{}]*owner=["\']?CHI["\']?[^{}]*\}', modifier.content, re.DOTALL)
        print(f"  在文件中找到包含owner=CHI的省份块: {len(chi_blocks)} 个")
        return
    
    # 步骤3：检查前几个省份的结构
    print(f"\n🔍 步骤3：检查前3个中国省份的结构...")
    for i, province_block in enumerate(chinese_provinces[:3]):
        print(f"  省份 {i+1}: ID={province_block.name}, 内容长度={len(province_block.content)} 字符")
        
        # 检查是否包含人口类型
        pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                    'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                    'bureaucrats', 'intellectuals']
        
        found_pops = []
        for child_block in province_block.children:
            if child_block.name.strip() in pop_types:
                found_pops.append(child_block.name.strip())
        
        print(f"    找到人口类型: {found_pops} ({len(found_pops)} 个)")
        
        # 检查第一个人口块是否包含ideology
        if found_pops:
            first_pop_block = next(child for child in province_block.children if child.name.strip() in pop_types)
            ideology_match = re.search(r'ideology=\s*\{[^}]*\}', first_pop_block.content, re.DOTALL)
            print(f"    第一个人口块包含ideology: {'是' if ideology_match else '否'}")
            
            if ideology_match:
                ideology_content = ideology_match.group(0)
                print(f"    ideology内容预览: {ideology_content[:100]}...")
                
                # 检查是否有旧意识形态
                ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
                ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
                has_old_ideologies = any(ideology_dist.get(old_id, 0) > 0 for old_id in [1, 2, 4, 5, 7])
                print(f"    包含需要转换的旧意识形态: {'是' if has_old_ideologies else '否'}")
                if has_old_ideologies:
                    old_values = {old_id: ideology_dist.get(old_id, 0) for old_id in [1, 2, 4, 5, 7] if ideology_dist.get(old_id, 0) > 0}
                    print(f"    需要转换的意识形态: {old_values}")
    
    # 步骤4：测试_collect_province_modifications
    print(f"\n🔍 步骤4：测试修改收集功能...")
    first_province = chinese_provinces[0]
    modifications = modifier._collect_province_modifications(first_province)
    print(f"  第一个省份的修改数量: {len(modifications)}")
    
    if len(modifications) > 0:
        print(f"  第一个修改的详情:")
        mod = modifications[0]
        print(f"    位置: {mod['start_pos']} - {mod['end_pos']}")
        print(f"    原内容长度: {len(mod['old_content'])} 字符")
        print(f"    新内容长度: {len(mod['new_content'])} 字符")
        print(f"    内容是否相同: {'是' if mod['old_content'] == mod['new_content'] else '否'}")
    
    # 步骤5：测试单个人口块修改
    print(f"\n🔍 步骤5：测试单个人口块修改...")
    first_province = chinese_provinces[0]
    pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                'bureaucrats', 'intellectuals']
    
    for child_block in first_province.children:
        if child_block.name.strip() in pop_types:
            print(f"  测试人口类型: {child_block.name.strip()}")
            old_content = child_block.content
            new_content = modifier._modify_single_population_structured(old_content)
            
            print(f"    原内容长度: {len(old_content)} 字符")
            print(f"    新内容长度: {len(new_content)} 字符")
            print(f"    内容已修改: {'是' if old_content != new_content else '否'}")
            
            # 检查意识形态修改
            old_ideology = re.search(r'ideology=\s*\{([^}]*)\}', old_content, re.DOTALL)
            new_ideology = re.search(r'ideology=\s*\{([^}]*)\}', new_content, re.DOTALL)
            
            if old_ideology and new_ideology:
                old_ideology_content = old_ideology.group(1)
                new_ideology_content = new_ideology.group(1)
                print(f"    意识形态内容已修改: {'是' if old_ideology_content != new_ideology_content else '否'}")
                
                if old_ideology_content != new_ideology_content:
                    print(f"    原意识形态: {old_ideology_content.strip()}")
                    print(f"    新意识形态: {new_ideology_content.strip()}")
            
            break  # 只测试第一个人口块
    
    print("\n✅ 调试完成")

if __name__ == "__main__":
    debug_full_ideology_chain()
