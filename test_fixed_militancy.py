#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修正后的斗争性修改功能
"""

import sys
from victoria2_main_modifier import Victoria2Modifier

def test_fixed_militancy():
    """测试修正后的斗争性修改功能"""
    
    print("🧪 测试修正后的斗争性修改功能")
    print("=" * 50)
    
    filename = 'China1837_01_24.v2'
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=True)
    
    print("🔄 执行load_file...")
    if modifier.load_file(filename):
        print("✅ load_file成功")
        
        print("🔄 执行modify_militancy...")
        if modifier.modify_militancy():
            print(f"✅ modify_militancy成功")
            print(f"   修改数量: {modifier.militancy_changes}")
            
            print("🔄 执行save_file...")
            if modifier.save_file(filename):
                print("✅ save_file成功")
                
                # 立即验证
                print("\n🔍 立即验证修改效果...")
                verify_militancy_fix(filename)
                
            else:
                print("❌ save_file失败")
        else:
            print("❌ modify_militancy失败")
    else:
        print("❌ load_file失败")

def verify_militancy_fix(filename):
    """验证斗争性修改效果"""
    
    import re
    
    # 读取文件
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        print(f"✅ 验证文件读取成功")
    except Exception as e:
        print(f"❌ 验证文件读取失败: {e}")
        return
    
    # 检查中国省份的loyalty_value
    chinese_provinces = range(1, 30)  # 中国省份1-29
    
    china_loyalty_values = []
    
    for province_id in list(chinese_provinces)[:10]:  # 检查前10个省份
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
        loyalty_pattern = r'loyalty_value=([\d.]+)'
        province_loyalty_matches = re.findall(loyalty_pattern, province_content)
        
        print(f"省份 {province_id}: {len(province_loyalty_matches)} 个loyalty_value")
        
        for i, value in enumerate(province_loyalty_matches):
            china_loyalty_values.append(float(value))
            if i < 3:  # 只显示前3个
                status = "✅" if float(value) == 0.0 else "❌"
                print(f"  值{i+1}: {value} {status}")
    
    if china_loyalty_values:
        print(f"\n📊 中国省份验证结果:")
        zero_count = sum(1 for v in china_loyalty_values if v == 0.0)
        non_zero_count = len(china_loyalty_values) - zero_count
        
        print(f"  总数: {len(china_loyalty_values)}")
        print(f"  为0的值: {zero_count}")
        print(f"  非0的值: {non_zero_count}")
        
        if non_zero_count == 0:
            print(f"  🎉 完美！所有中国省份的loyalty_value都已设为0")
        else:
            print(f"  ⚠️ 仍有 {non_zero_count} 个非零值")

if __name__ == "__main__":
    test_fixed_militancy()
