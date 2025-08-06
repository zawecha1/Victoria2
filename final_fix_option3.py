#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终完善选项3功能
"""

import re

def final_fix_option3(filename):
    """最终完善选项3：确保中国=0，其他=10"""
    print("🔧 最终完善选项3功能...")
    
    # 读取文件
    with open(filename, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 中国省份范围
    chinese_provinces = set(str(i) for i in range(2687, 2741))
    
    # 查找所有省份
    province_pattern = r'^(\d+)=\s*{'
    province_matches = list(re.finditer(province_pattern, content, re.MULTILINE))
    
    chinese_fixes = 0
    non_chinese_fixes = 0
    
    print(f"🔍 检查 {len(province_matches)} 个省份...")
    
    for i, match in enumerate(province_matches):
        province_id = match.group(1)
        start_pos = match.start()
        
        # 找到这个省份的结束位置
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            end_pos = len(content)
        
        province_content = content[start_pos:end_pos]
        
        # 查找loyalty_value
        loyalty_pattern = r'loyalty_value=([\d.]+)'
        loyalty_matches = list(re.finditer(loyalty_pattern, province_content))
        
        if loyalty_matches:
            new_province_content = province_content
            is_chinese = province_id in chinese_provinces
            
            # 从后往前替换
            for match_loyalty in reversed(loyalty_matches):
                old_value = float(match_loyalty.group(1))
                
                if is_chinese:
                    # 中国省份应该是0
                    if abs(old_value - 0.0) > 0.001:
                        new_loyalty = 'loyalty_value=0.00000'
                        new_province_content = (new_province_content[:match_loyalty.start()] + 
                                              new_loyalty + 
                                              new_province_content[match_loyalty.end():])
                        chinese_fixes += 1
                        print(f"  🔄 中国省份 {province_id}: {old_value} -> 0.0")
                else:
                    # 非中国省份应该是10
                    if abs(old_value - 10.0) > 0.001:
                        new_loyalty = 'loyalty_value=10.00000'
                        new_province_content = (new_province_content[:match_loyalty.start()] + 
                                              new_loyalty + 
                                              new_province_content[match_loyalty.end():])
                        non_chinese_fixes += 1
                        if non_chinese_fixes <= 5:  # 只显示前5个
                            print(f"  🌍 非中国省份 {province_id}: {old_value} -> 10.0")
            
            # 更新文件内容
            if new_province_content != province_content:
                content = (content[:start_pos] + 
                          new_province_content + 
                          content[end_pos:])
    
    # 保存文件
    with open(filename, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    print(f"\n✅ 最终修复完成!")
    print(f"📊 修复统计:")
    print(f"  - 中国省份修复: {chinese_fixes} 个")
    print(f"  - 非中国省份修复: {non_chinese_fixes} 个")
    print(f"💾 文件已保存: {filename}")
    
    return chinese_fixes + non_chinese_fixes

if __name__ == "__main__":
    filename = "China1837_01_24.v2"
    
    total_fixes = final_fix_option3(filename)
    
    if total_fixes > 0:
        print(f"\n🎉 完善完成! 总共修复 {total_fixes} 个值")
        print("🔄 现在选项3功能应该完全正确了")
    else:
        print(f"\n✅ 选项3功能已经完全正确")
