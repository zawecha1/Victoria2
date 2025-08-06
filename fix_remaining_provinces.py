#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门修正中国省份loyalty_value的脚本
解决剩余4个省份的问题：2689, 2690, 2692, 2693
"""

import re

def fix_remaining_chinese_provinces(filename):
    """修正剩余的中国省份loyalty_value"""
    print("🔧 专门修正剩余4个中国省份的loyalty_value...")
    
    # 读取文件
    with open(filename, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    print(f"📁 文件大小: {len(content):,} 字符")
    
    # 需要修正的省份
    problem_provinces = ['2689', '2690', '2692', '2693']
    modifications = 0
    
    for province_id in problem_provinces:
        print(f"\n🎯 处理省份 {province_id}")
        
        # 查找省份块
        province_pattern = f'^{province_id}=\\s*{{'
        province_match = re.search(province_pattern, content, re.MULTILINE)
        
        if not province_match:
            print(f"  ❌ 未找到省份 {province_id}")
            continue
        
        print(f"  ✅ 找到省份 {province_id}")
        
        # 提取省份内容 - 使用括号匹配
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
        print(f"  📦 省份内容长度: {len(province_content)} 字符")
        
        # 查找并替换loyalty_value
        loyalty_pattern = r'loyalty_value=([\d.]+)'
        loyalty_matches = list(re.finditer(loyalty_pattern, province_content))
        
        print(f"  🔍 找到 {len(loyalty_matches)} 个loyalty_value")
        
        if loyalty_matches:
            new_province_content = province_content
            
            # 从后往前替换，避免位置偏移
            for match in reversed(loyalty_matches):
                old_value = match.group(1)
                print(f"    🔄 将 loyalty_value={old_value} 改为 0.00000")
                
                new_loyalty = 'loyalty_value=0.00000'
                new_province_content = (new_province_content[:match.start()] + 
                                      new_loyalty + 
                                      new_province_content[match.end():])
                modifications += 1
            
            # 更新文件内容
            content = (content[:start_pos] + 
                      new_province_content + 
                      content[current_pos-1:])
            
            print(f"  ✅ 省份 {province_id} 修改完成")
    
    # 保存文件
    with open(filename, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    print(f"\n🎉 修正完成!")
    print(f"📊 总共修改了 {modifications} 个loyalty_value")
    print(f"💾 文件已保存: {filename}")
    
    return modifications

if __name__ == "__main__":
    filename = "China1837_01_24.v2"
    
    print("🧪 修正剩余中国省份loyalty_value")
    print("=" * 50)
    
    # 修正文件
    modifications = fix_remaining_chinese_provinces(filename)
    
    if modifications > 0:
        print("\n✅ 修正成功!")
    else:
        print("\n❌ 没有找到需要修正的值")
