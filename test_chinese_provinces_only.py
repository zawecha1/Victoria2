#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试只修改中国省份的loyalty_value
"""

import re
import time

def count_loyalty_values_in_chinese_provinces(content):
    """只统计中国省份的loyalty_value"""
    chinese_provinces = [str(i) for i in range(2687, 2741)]  # 2687-2740
    
    # 省份匹配模式
    province_pattern = r'(\d+)=\s*\{'
    loyalty_pattern = r'loyalty_value=([0-9.]+)'
    
    province_matches = list(re.finditer(province_pattern, content))
    print(f"📊 总共找到 {len(province_matches)} 个省份")
    
    chinese_loyalty_values = []
    chinese_province_count = 0
    
    for i, match in enumerate(province_matches):
        province_id = match.group(1)
        
        if province_id in chinese_provinces:
            chinese_province_count += 1
            start_pos = match.start()
            
            # 找到这个省份的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                end_pos = len(content)
            
            province_content = content[start_pos:end_pos]
            
            # 在这个省份内查找loyalty_value
            loyalty_matches = re.findall(loyalty_pattern, province_content)
            
            print(f"🏪 中国省份 {province_id}: 找到 {len(loyalty_matches)} 个 loyalty_value")
            for j, value in enumerate(loyalty_matches[:3]):  # 只显示前3个
                val = float(value)
                status = "✅" if val == 0.0 else "❌"
                print(f"  值{j+1}: {val:.5f} {status}")
                chinese_loyalty_values.append(val)
            
            if len(loyalty_matches) > 3:
                print(f"  ... 还有 {len(loyalty_matches) - 3} 个值")
                chinese_loyalty_values.extend([float(v) for v in loyalty_matches[3:]])
    
    zero_count = sum(1 for v in chinese_loyalty_values if v == 0.0)
    non_zero_count = len(chinese_loyalty_values) - zero_count
    
    print(f"\n📊 中国省份 loyalty_value 统计:")
    print(f"  找到的中国省份数量: {chinese_province_count}")
    print(f"  总 loyalty_value 数量: {len(chinese_loyalty_values)}")
    print(f"  为0的值: {zero_count}")
    print(f"  非0的值: {non_zero_count}")
    
    if non_zero_count > 0:
        print(f"  ⚠️  仍有 {non_zero_count} 个非零值需要修改")
    else:
        print(f"  ✅ 所有中国省份的 loyalty_value 都已设为0")
    
    return chinese_loyalty_values

def main():
    print("🧪 测试中国省份 loyalty_value 状态")
    print("=" * 50)
    
    filename = "China1837_01_24.v2"
    
    print(f"🔍 读取文件: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        print(f"✅ 文件读取成功，大小: {len(content):,} 字符")
        
        # 统计中国省份的loyalty_value
        chinese_values = count_loyalty_values_in_chinese_provinces(content)
        
        print(f"\n📈 详细数值分布:")
        unique_values = list(set(chinese_values))
        unique_values.sort()
        
        for value in unique_values:
            count = chinese_values.count(value)
            print(f"  {value:.5f}: {count} 个")
        
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
