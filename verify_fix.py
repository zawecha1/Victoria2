#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证意识形态修改效果
"""

import re

def verify_ideology_fix():
    """验证意识形态修复效果"""
    
    print("🔍 验证意识形态修复效果")
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
    
    # 统计信息
    total_ideology_blocks = 0
    converted_blocks = 0
    old_ideology_found = 0
    
    # 查找中国省份（1-29）
    for province_id in range(1, 30):
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
        
        # 查找该省份中所有的ideology块
        ideology_pattern = r'ideology=\s*\{([^}]*)\}'
        ideology_matches = list(re.finditer(ideology_pattern, province_content, re.DOTALL))
        
        province_blocks = len(ideology_matches)
        province_converted = 0
        province_old_found = 0
        
        for match in ideology_matches:
            total_ideology_blocks += 1
            ideology_content = match.group(1)
            
            # 解析意识形态数据
            ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
            ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
            
            # 检查旧意识形态
            old_ideologies = [1, 2, 4, 5, 7]
            has_old_values = any(ideology_dist.get(old_id, 0) > 0 for old_id in old_ideologies)
            
            if has_old_values:
                old_ideology_found += 1
                province_old_found += 1
                print(f"  ⚠️ 省份{province_id}发现旧意识形态: {[f'{id}={ideology_dist.get(id, 0):.2f}' for id in old_ideologies if ideology_dist.get(id, 0) > 0]}")
            else:
                converted_blocks += 1
                province_converted += 1
        
        if province_blocks > 0:
            print(f"🔍 省份{province_id}: {province_blocks}个意识形态块, {province_converted}个已转换, {province_old_found}个仍有旧值")
    
    # 显示总结
    print(f"\n📊 验证结果:")
    print(f"总意识形态块数: {total_ideology_blocks}")
    print(f"成功转换: {converted_blocks}")
    print(f"仍有旧值: {old_ideology_found}")
    print(f"转换成功率: {(converted_blocks/total_ideology_blocks*100):.1f}%" if total_ideology_blocks > 0 else "N/A")
    
    if old_ideology_found == 0:
        print("🎉 完美！所有意识形态都已成功转换！")
    elif old_ideology_found < 10:
        print("✅ 修复效果良好，只有少数块未转换")
    else:
        print("⚠️ 修复效果有限，仍有较多旧意识形态")
    
    # 检查一些具体的样本
    print(f"\n📋 样本检查:")
    
    # 检查省份1的第一个意识形态块
    province_pattern = r'^1=\s*{'
    province_match = re.search(province_pattern, content, re.MULTILINE)
    
    if province_match:
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
        ideology_pattern = r'ideology=\s*\{([^}]*)\}'
        ideology_match = re.search(ideology_pattern, province_content, re.DOTALL)
        
        if ideology_match:
            ideology_content = ideology_match.group(1)
            ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
            ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
            
            print(f"省份1第一个意识形态块: {ideology_dist}")
            
            # 检查转换是否正确
            old_sum = sum(ideology_dist.get(id, 0) for id in [1, 2, 4, 5, 7])
            new_sum = ideology_dist.get(3, 0) + ideology_dist.get(6, 0)
            
            if old_sum < 0.01:  # 基本为0
                print("✅ 旧意识形态已清零")
            else:
                print(f"❌ 旧意识形态仍有值: {old_sum:.5f}")
            
            print(f"新意识形态总值: Conservative(3)={ideology_dist.get(3, 0):.5f}, Liberal(6)={ideology_dist.get(6, 0):.5f}")

if __name__ == "__main__":
    verify_ideology_fix()
