#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接检查当前意识形态状态
"""

import re

def check_current_ideology_status():
    """检查当前意识形态状态"""
    
    print("🔍 检查当前意识形态状态")
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
    
    # 检查前几个中国省份的意识形态状态
    provinces_to_check = [1, 2, 3, 4, 5]
    
    for province_id in provinces_to_check:
        print(f"\n🔍 检查省份 {province_id}:")
        
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
        
        # 查找该省份中的ideology块
        ideology_pattern = r'ideology=\s*\{([^}]*)\}'
        ideology_matches = list(re.finditer(ideology_pattern, province_content, re.DOTALL))
        
        print(f"  📊 找到 {len(ideology_matches)} 个意识形态块")
        
        # 检查前3个意识形态块
        for i, match in enumerate(ideology_matches[:3]):
            ideology_content = match.group(1)
            
            # 解析意识形态数据
            ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
            ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
            
            # 检查旧意识形态
            old_ideologies = [1, 2, 4, 5, 7]
            old_values = {id_val: ideology_dist.get(id_val, 0) for id_val in old_ideologies}
            
            # 检查新意识形态
            conservative = ideology_dist.get(3, 0)
            liberal = ideology_dist.get(6, 0)
            
            print(f"    块{i+1}: 旧值={old_values}, Conservative(3)={conservative:.2f}, Liberal(6)={liberal:.2f}")
            
            # 判断状态
            has_old_values = any(val > 0.01 for val in old_values.values())
            if has_old_values:
                print(f"    ⚠️ 仍有旧意识形态值")
            else:
                print(f"    ✅ 旧意识形态已清零")
    
    # 全局统计
    print(f"\n📊 全局统计:")
    
    all_ideology_matches = list(re.finditer(r'ideology=\s*\{([^}]*)\}', content, re.DOTALL))
    total_blocks = len(all_ideology_matches)
    
    blocks_with_old_values = 0
    blocks_converted = 0
    
    for match in all_ideology_matches[:100]:  # 检查前100个块避免太慢
        ideology_content = match.group(1)
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
        ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
        
        old_ideologies = [1, 2, 4, 5, 7]
        has_old_values = any(ideology_dist.get(old_id, 0) > 0.01 for old_id in old_ideologies)
        
        if has_old_values:
            blocks_with_old_values += 1
        else:
            blocks_converted += 1
    
    print(f"检查的前100个意识形态块中:")
    print(f"  转换成功: {blocks_converted}")
    print(f"  仍有旧值: {blocks_with_old_values}")
    print(f"  转换率: {(blocks_converted/(blocks_converted+blocks_with_old_values)*100):.1f}%" if (blocks_converted+blocks_with_old_values) > 0 else "N/A")

if __name__ == "__main__":
    check_current_ideology_status()
