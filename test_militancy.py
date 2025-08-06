#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试人口斗争性修改
"""

import re

def test_militancy_modification():
    """测试人口斗争性修改"""
    
    print("🔍 测试人口斗争性修改")
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
    
    # 检查中国省份的斗争性
    print("\n🔍 检查中国省份的斗争性...")
    
    chinese_provinces = list(range(1, 30))  # 中国省份1-29
    
    total_militancy_found = 0
    zero_militancy_count = 0
    non_zero_militancy_count = 0
    
    for province_id in chinese_provinces[:10]:  # 检查前10个省份避免输出太长
        print(f"\n省份 {province_id}:")
        
        # 查找省份
        province_pattern = f'^{province_id}=\\s*{{'
        province_match = re.search(province_pattern, content, re.MULTILINE)
        
        if not province_match:
            print(f"  ❌ 未找到省份{province_id}")
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
        
        # 查找militancy值
        militancy_pattern = r'militancy=([\d.]+)'
        militancy_matches = re.findall(militancy_pattern, province_content)
        
        print(f"  找到 {len(militancy_matches)} 个militancy值:")
        
        for i, militancy_value in enumerate(militancy_matches):
            total_militancy_found += 1
            militancy_float = float(militancy_value)
            
            if militancy_float == 0.0:
                zero_militancy_count += 1
                print(f"    militancy{i+1}: {militancy_value} ✅")
            else:
                non_zero_militancy_count += 1
                print(f"    militancy{i+1}: {militancy_value} ❌")
    
    print(f"\n📊 斗争性统计:")
    print(f"总找到的militancy值: {total_militancy_found}")
    print(f"为0的值: {zero_militancy_count}")
    print(f"非0的值: {non_zero_militancy_count}")
    
    if non_zero_militancy_count > 0:
        print(f"⚠️ 发现 {non_zero_militancy_count} 个非零的斗争性值")
        print("斗争性修改可能没有生效或有问题")
    else:
        print("✅ 所有检查的斗争性值都为0")
    
    # 检查非中国省份的斗争性（应该为10）
    print(f"\n🔍 检查非中国省份的斗争性（应该为10）...")
    
    non_chinese_provinces = [30, 31, 32, 50, 100]  # 一些非中国省份
    
    for province_id in non_chinese_provinces:
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
        
        # 查找militancy值
        militancy_pattern = r'militancy=([\d.]+)'
        militancy_matches = re.findall(militancy_pattern, province_content)
        
        print(f"省份 {province_id}: {len(militancy_matches)} 个militancy值")
        
        for i, militancy_value in enumerate(militancy_matches[:3]):  # 只显示前3个
            militancy_float = float(militancy_value)
            expected = "✅" if militancy_float == 10.0 else "❌"
            print(f"  militancy{i+1}: {militancy_value} {expected}")
        
        break  # 只检查找到的第一个非中国省份

if __name__ == "__main__":
    test_militancy_modification()
