#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查修改后文件中是否还有未转换的意识形态
"""

import re
import sys

def check_remaining_ideologies(filename):
    """检查文件中是否还有未转换的意识形态"""
    print(f"🔍 检查文件: {filename}")
    print("查找未转换的意识形态...")
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        print(f"✅ 文件读取成功，大小: {len(content):,} 字符")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 查找所有意识形态块
    ideology_pattern = r'ideology=\s*\{([^}]*)\}'
    ideology_matches = list(re.finditer(ideology_pattern, content, re.DOTALL))
    
    print(f"📊 找到 {len(ideology_matches)} 个意识形态块")
    
    # 需要转换的旧意识形态ID
    old_ideologies = [1, 2, 4, 5, 7]
    
    problematic_blocks = []
    total_checked = 0
    
    for i, match in enumerate(ideology_matches):
        ideology_content = match.group(1)
        
        # 解析意识形态数据
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
        ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
        
        # 检查是否有旧意识形态
        has_old = any(ideology_dist.get(old_id, 0) > 0 for old_id in old_ideologies)
        
        if has_old:
            # 找到这个意识形态块所在的上下文
            start_pos = max(0, match.start() - 200)
            end_pos = min(len(content), match.end() + 200)
            context = content[start_pos:end_pos]
            
            # 尝试找到所属的省份或人口组
            province_match = re.search(r'(\d+)=\s*{[^{}]*$', content[:match.start()][::-1])
            if province_match:
                province_id = province_match.group(1)[::-1]
            else:
                province_id = "未知"
            
            problematic_blocks.append({
                'position': match.start(),
                'ideology_dist': ideology_dist,
                'province_id': province_id,
                'context': context
            })
        
        total_checked += 1
        
        # 进度显示
        if (i + 1) % 1000 == 0:
            print(f"已检查 {i + 1}/{len(ideology_matches)} 个意识形态块...")
    
    print(f"\n📋 检查结果:")
    print(f"总计检查: {total_checked} 个意识形态块")
    print(f"发现问题: {len(problematic_blocks)} 个未转换的意识形态块")
    
    if problematic_blocks:
        print(f"\n⚠️ 发现 {len(problematic_blocks)} 个未转换的意识形态块:")
        
        for i, block in enumerate(problematic_blocks[:10]):  # 只显示前10个
            print(f"\n--- 问题块 {i+1} ---")
            print(f"位置: {block['position']}")
            print(f"省份ID: {block['province_id']}")
            print(f"意识形态分布: {block['ideology_dist']}")
            
            # 显示需要转换的意识形态
            old_values = {id: val for id, val in block['ideology_dist'].items() 
                         if id in old_ideologies and val > 0}
            if old_values:
                print(f"需要转换: {old_values}")
            
            # 显示部分上下文
            context_lines = block['context'].split('\n')
            relevant_lines = [line.strip() for line in context_lines if line.strip() and ('=' in line or '{' in line or '}' in line)][:5]
            print(f"上下文:")
            for line in relevant_lines:
                print(f"  {line}")
        
        if len(problematic_blocks) > 10:
            print(f"\n... 还有 {len(problematic_blocks) - 10} 个问题块未显示")
    else:
        print("✅ 所有意识形态都已正确转换!")

def main():
    # 检查命令行参数
    import sys
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'autosave.v2'
    
    # 检查当前存档文件
    check_remaining_ideologies(filename)

if __name__ == "__main__":
    main()
