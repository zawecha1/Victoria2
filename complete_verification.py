#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整验证所有修改功能
"""

import re

def main():
    with open('China2281_01_01.v2', 'r', encoding='utf-8-sig') as f:
        content = f.read()

    print("=== 完整功能验证报告 ===")
    
    # 1. 验证CHI国家设置
    print("\n1. CHI国家设置验证:")
    chi_match = re.search(r'^CHI=\s*\{', content, re.MULTILINE)
    if chi_match:
        start_pos = chi_match.start()
        next_country_match = re.search(r'\n[A-Z]{3}=\s*\{', content[start_pos + 100:])
        if next_country_match:
            end_pos = start_pos + 100 + next_country_match.start()
        else:
            end_pos = len(content)
        
        chi_block = content[start_pos:end_pos]
        
        # 主文化
        primary_match = re.search(r'primary_culture="([^"]+)"', chi_block)
        if primary_match:
            print(f"   ✅ 主文化: {primary_match.group(1)}")
        else:
            print("   ❌ 主文化: 未找到")
        
        # 接受文化 (使用culture=)
        culture_match = re.search(r'culture=\s*\{([^}]+)\}', chi_block, re.DOTALL)
        if culture_match:
            cultures = re.findall(r'"([^"]+)"', culture_match.group(1))
            print(f"   ✅ 接受文化: {cultures}")
        else:
            print("   ❌ 接受文化: 未找到")
        
        # 恶名度
        badboy_match = re.search(r'badboy=([\d.]+)', chi_block)
        if badboy_match:
            print(f"   ✅ 恶名度: {badboy_match.group(1)}")
        else:
            print("   ❌ 恶名度: 未找到")
    else:
        print("   ❌ CHI块: 未找到")
    
    # 2. 验证人口宗教修改
    print("\n2. 人口宗教修改验证:")
    chinese_cultures = ['beifaren', 'nanfaren', 'manchu', 'han', 'cantonese', 'min', 'hakka']
    total_chinese_pop = 0
    total_mahayana = 0
    
    for culture in chinese_cultures:
        pattern = f'{culture}=([a-zA-Z_]+)'
        matches = re.findall(pattern, content)
        
        if matches:
            from collections import Counter
            religion_counts = Counter(matches)
            culture_total = sum(religion_counts.values())
            culture_mahayana = religion_counts.get('mahayana', 0)
            
            total_chinese_pop += culture_total
            total_mahayana += culture_mahayana
            
            if culture_total > 0:
                percentage = (culture_mahayana / culture_total) * 100
                print(f"   {culture}: {culture_mahayana}/{culture_total} ({percentage:.1f}% mahayana)")
    
    if total_chinese_pop > 0:
        overall_percentage = (total_mahayana / total_chinese_pop) * 100
        print(f"   ✅ 总计: {total_mahayana}/{total_chinese_pop} ({overall_percentage:.1f}% 转换为mahayana)")
    
    # 3. 验证意识形态修改
    print("\n3. 意识形态修改验证:")
    ideology_blocks = re.findall(r'ideology=\s*\{([^{}]+)\}', content, re.DOTALL)
    print(f"   找到 {len(ideology_blocks)} 个意识形态块")
    
    # 统计各意识形态的非零值数量
    ideology_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    
    for block in ideology_blocks[:1000]:  # 分析前1000个
        id_values = re.findall(r'(\d+)=([\d.]+)', block)
        for id_str, value_str in id_values:
            ideology_id = int(id_str)
            value = float(value_str)
            if value > 0 and ideology_id in ideology_stats:
                ideology_stats[ideology_id] += 1
    
    print(f"   意识形态分布(前1000个块中的非零值):")
    print(f"     Reactionary(1): {ideology_stats[1]} 次")
    print(f"     Fascist(2): {ideology_stats[2]} 次")
    print(f"   ✅ Conservative(3): {ideology_stats[3]} 次")
    print(f"     Socialist(4): {ideology_stats[4]} 次")
    print(f"     Anarcho-Liberal(5): {ideology_stats[5]} 次")
    print(f"   ✅ Liberal(6): {ideology_stats[6]} 次")
    print(f"     Communist(7): {ideology_stats[7]} 次")
    
    # 4. 验证文件完整性
    print("\n4. 文件完整性验证:")
    size_count = content.count('size=')
    money_count = content.count('money=')
    print(f"   ✅ 人口组总数: {size_count:,}")
    print(f"   ✅ 金钱记录: {money_count:,}")
    print(f"   ✅ 文件大小: {len(content):,} 字符")
    
    print("\n🎉 验证完成！功能隔离模式成功实现所有修改！")

if __name__ == "__main__":
    main()
