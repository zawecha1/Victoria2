#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复选项3：将非中国省份的loyalty_value设为10.0
"""

import re

def fix_non_chinese_provinces(filename):
    """修复非中国省份的loyalty_value为10.0"""
    print("🔧 修复选项3：将非中国省份的loyalty_value设为10.0")
    print("=" * 60)
    
    # 读取文件
    with open(filename, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    print(f"📁 文件大小: {len(content):,} 字符")
    
    # 中国省份范围
    chinese_provinces = set(str(i) for i in range(2687, 2741))
    
    # 查找所有省份
    province_pattern = r'^(\d+)=\s*{'
    province_matches = list(re.finditer(province_pattern, content, re.MULTILINE))
    
    print(f"📊 总共找到 {len(province_matches)} 个省份")
    
    modifications = 0
    non_chinese_processed = 0
    
    for i, match in enumerate(province_matches):
        province_id = match.group(1)
        
        # 只处理非中国省份
        if province_id in chinese_provinces:
            continue
        
        non_chinese_processed += 1
        
        # 显示进度（每500个省份）
        if non_chinese_processed % 500 == 0:
            print(f"  🌍 进度: {non_chinese_processed} 个非中国省份已处理...")
        
        start_pos = match.start()
        
        # 找到这个省份的结束位置
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            end_pos = len(content)
        
        province_content = content[start_pos:end_pos]
        
        # 查找并替换loyalty_value
        loyalty_pattern = r'loyalty_value=([\d.]+)'
        loyalty_matches = list(re.finditer(loyalty_pattern, province_content))
        
        if loyalty_matches:
            new_province_content = province_content
            
            # 从后往前替换，避免位置偏移
            for match_loyalty in reversed(loyalty_matches):
                old_value = match_loyalty.group(1)
                old_val = float(old_value)
                
                # 只修改不是10.0的值
                if abs(old_val - 10.0) > 0.001:
                    new_loyalty = 'loyalty_value=10.00000'
                    new_province_content = (new_province_content[:match_loyalty.start()] + 
                                          new_loyalty + 
                                          new_province_content[match_loyalty.end():])
                    modifications += 1
            
            # 更新文件内容
            if new_province_content != province_content:
                content = (content[:start_pos] + 
                          new_province_content + 
                          content[end_pos:])
    
    # 保存文件
    with open(filename, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    print(f"\n🎉 修复完成!")
    print(f"📊 统计:")
    print(f"  - 处理的非中国省份: {non_chinese_processed} 个")
    print(f"  - 修改的loyalty_value: {modifications} 个")
    print(f"💾 文件已保存: {filename}")
    
    return modifications

if __name__ == "__main__":
    filename = "China1837_01_24.v2"
    
    print("🔧 开始修复选项3功能...")
    modifications = fix_non_chinese_provinces(filename)
    
    if modifications > 0:
        print("\n✅ 修复成功!")
        print("🔄 建议再次运行测试脚本验证结果")
    else:
        print("\n✅ 无需修复，所有非中国省份已正确设为10.0")
