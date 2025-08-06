#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确诊断替换过程的脚本
"""

import re
import sys
from victoria2_main_modifier import Victoria2Modifier

def precise_replacement_diagnosis():
    """精确诊断替换过程"""
    
    print("🔬 精确诊断替换过程")
    print("=" * 50)
    
    filename = 'China1837_01_24.v2'
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=True)
    
    # 加载文件但不修改
    if not modifier.load_file(filename):
        print("❌ 无法加载文件")
        return
    
    print("✅ 文件加载成功")
    
    # 查找第一个中国省份
    chinese_provinces = modifier.find_chinese_provinces_structured()
    if not chinese_provinces:
        print("❌ 未找到中国省份")
        return
    
    print(f"✅ 找到 {len(chinese_provinces)} 个中国省份")
    
    # 获取第一个省份的内容
    first_province = chinese_provinces[0]
    print(f"🎯 分析第一个省份...")
    
    # 查找人口类型块
    pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                'bureaucrats', 'intellectuals']
    
    population_blocks = []
    for child_block in first_province.children:
        if any(pop_type in child_block.content for pop_type in pop_types):
            population_blocks.append(child_block)
    
    print(f"📊 找到 {len(population_blocks)} 个人口块")
    
    if not population_blocks:
        print("❌ 未找到人口块")
        return
    
    # 分析第一个人口块
    first_pop_block = population_blocks[0]
    original_content = first_pop_block.content
    
    print(f"\n📋 第一个人口块内容:")
    print(f"长度: {len(original_content)}")
    print(f"开始位置: {first_pop_block.start_pos}")
    print(f"结束位置: {first_pop_block.end_pos}")
    
    # 查找ideology块
    ideology_pattern = r'ideology=\s*\{[^}]*\}'
    ideology_match = re.search(ideology_pattern, original_content, re.DOTALL)
    
    if not ideology_match:
        print("❌ 未找到ideology块")
        return
    
    full_ideology_block = ideology_match.group(0)
    print(f"\n🎭 找到ideology块:")
    print(f"长度: {len(full_ideology_block)}")
    print(f"内容: {repr(full_ideology_block)}")
    
    # 提取内容
    inner_content_match = re.search(r'ideology=\s*\{([^}]*)\}', full_ideology_block, re.DOTALL)
    if not inner_content_match:
        print("❌ 无法提取ideology内容")
        return
    
    ideology_content = inner_content_match.group(1)
    print(f"\n📊 Ideology内容:")
    print(f"长度: {len(ideology_content)}")
    print(f"内容: {repr(ideology_content)}")
    
    # 解析意识形态数据
    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
    ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
    
    print(f"\n📈 解析结果: {ideology_dist}")
    
    # 检查是否需要转换
    old_ideologies = [1, 2, 4, 5, 7]
    needs_conversion = any(ideology_dist.get(old_id, 0) > 0 for old_id in old_ideologies)
    
    if not needs_conversion:
        print("ℹ️ 该块无需转换")
        return
    
    print("🔄 该块需要转换，开始测试转换过程...")
    
    # 调用修改器的转换方法
    new_ideology_content = modifier._modify_ideology_distribution(ideology_content)
    print(f"\n🔄 转换后内容:")
    print(f"长度: {len(new_ideology_content)}")
    print(f"内容: {repr(new_ideology_content)}")
    
    # 测试替换
    print(f"\n🧪 测试替换过程...")
    
    # 方法1：原始方法
    new_ideology_block_1 = f'ideology=\n\t\t{{\n\t\t\t{new_ideology_content}\n\t\t}}'
    test_result_1 = original_content.replace(full_ideology_block, new_ideology_block_1)
    
    success_1 = test_result_1 != original_content
    print(f"方法1 (原始格式): {'✅ 成功' if success_1 else '❌ 失败'}")
    
    if success_1:
        print(f"  替换后长度变化: {len(original_content)} → {len(test_result_1)}")
    
    # 方法2：保持原格式
    lines = full_ideology_block.split('\n')
    if len(lines) >= 2:
        start_line = lines[0]
        end_line = lines[-1]
        new_ideology_block_2 = start_line + '\n                {\n' + new_ideology_content + '\n' + end_line
        test_result_2 = original_content.replace(full_ideology_block, new_ideology_block_2)
        
        success_2 = test_result_2 != original_content
        print(f"方法2 (保持格式): {'✅ 成功' if success_2 else '❌ 失败'}")
        
        if success_2:
            print(f"  替换后长度变化: {len(original_content)} → {len(test_result_2)}")
    
    # 方法3：直接替换内容
    test_result_3 = original_content.replace(ideology_content, new_ideology_content)
    success_3 = test_result_3 != original_content
    print(f"方法3 (仅替换内容): {'✅ 成功' if success_3 else '❌ 失败'}")
    
    if success_3:
        print(f"  替换后长度变化: {len(original_content)} → {len(test_result_3)}")
    
    # 测试完整的修改函数
    print(f"\n🔧 测试完整修改函数...")
    modified_content = modifier._modify_single_population_structured(original_content)
    
    success_full = modified_content != original_content
    print(f"完整修改函数: {'✅ 成功' if success_full else '❌ 失败'}")
    
    if success_full:
        print(f"  修改后长度变化: {len(original_content)} → {len(modified_content)}")
        
        # 显示修改后的ideology部分
        new_ideology_match = re.search(ideology_pattern, modified_content, re.DOTALL)
        if new_ideology_match:
            new_full_block = new_ideology_match.group(0)
            print(f"  修改后的ideology块:")
            print(f"  {repr(new_full_block)}")
    else:
        print("  ❌ 修改函数没有产生任何改变")
        
        # 检查计数器
        print(f"  意识形态计数器: {modifier.ideology_changes}")
        print(f"  宗教计数器: {modifier.religion_changes}")

if __name__ == "__main__":
    precise_replacement_diagnosis()
