#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正斗争性修改功能
"""

import re

def fix_militancy_modification():
    """修正斗争性修改功能"""
    
    print("🔧 修正斗争性修改功能")
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
    
    # 检查loyalty_value的分布
    print("\n🔍 分析loyalty_value的分布...")
    
    loyalty_pattern = r'loyalty_value=([\d.]+)'
    loyalty_matches = re.findall(loyalty_pattern, content)
    
    print(f"找到 {len(loyalty_matches)} 个loyalty_value值")
    
    if loyalty_matches:
        # 显示前10个值
        print("前10个值:")
        for i, value in enumerate(loyalty_matches[:10]):
            print(f"  {i+1}: {value}")
        
        # 统计分布
        values = [float(v) for v in loyalty_matches]
        zero_count = sum(1 for v in values if v == 0.0)
        non_zero_count = len(values) - zero_count
        
        print(f"\n📊 分布统计:")
        print(f"  为0的值: {zero_count}")
        print(f"  非0的值: {non_zero_count}")
        print(f"  最小值: {min(values):.5f}")
        print(f"  最大值: {max(values):.5f}")
        print(f"  平均值: {sum(values)/len(values):.5f}")
    
    # 检查中国省份的loyalty_value
    print(f"\n🔍 检查中国省份的loyalty_value...")
    
    chinese_provinces = range(1, 30)  # 中国省份1-29
    
    china_loyalty_values = []
    
    for province_id in list(chinese_provinces)[:5]:  # 检查前5个省份
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
        
        # 查找该省份中的loyalty_value
        province_loyalty_matches = re.findall(loyalty_pattern, province_content)
        
        print(f"省份 {province_id}: {len(province_loyalty_matches)} 个loyalty_value")
        
        for i, value in enumerate(province_loyalty_matches):
            china_loyalty_values.append(float(value))
            if i < 3:  # 只显示前3个
                print(f"  值{i+1}: {value}")
    
    if china_loyalty_values:
        print(f"\n📊 中国省份loyalty_value统计:")
        zero_count = sum(1 for v in china_loyalty_values if v == 0.0)
        non_zero_count = len(china_loyalty_values) - zero_count
        
        print(f"  总数: {len(china_loyalty_values)}")
        print(f"  为0的值: {zero_count}")
        print(f"  非0的值: {non_zero_count}")
        
        if non_zero_count > 0:
            print(f"  ⚠️ 发现 {non_zero_count} 个非零值，需要修改为0")
        else:
            print(f"  ✅ 所有值都为0")
    
    # 建议修正方案
    print(f"\n💡 修正建议:")
    print(f"1. 将代码中的 'militancy=' 改为 'loyalty_value='")
    print(f"2. 中国省份的loyalty_value应该设为0.0")
    print(f"3. 其他省份的loyalty_value可以保持原值或设为较高值")

if __name__ == "__main__":
    fix_militancy_modification()
