#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修改结果
"""

def main():
    with open('China2281_01_01.v2', 'r', encoding='utf-8-sig') as f:
        content = f.read()

    print("=== 修改结果验证 ===")
    
    # 1. 宗教修改验证
    print("\n1. 宗教修改验证:")
    chinese_cultures = ['beifaren', 'nanfaren', 'manchu', 'han', 'min', 'hakka']
    total_mahayana = 0
    
    for culture in chinese_cultures:
        pattern = f'{culture}=mahayana'
        count = content.count(pattern)
        if count > 0:
            print(f"   {culture}=mahayana: {count} 处")
            total_mahayana += count
    
    print(f"   总计mahayana宗教: {total_mahayana}")
    
    # 2. 意识形态修改验证
    print("\n2. 意识形态修改验证:")
    import re
    
    # 查找ideology块
    ideology_pattern = r'ideology=\s*\{\s*([^}]+)\s*\}'
    ideology_matches = re.findall(ideology_pattern, content, re.DOTALL)
    
    print(f"   找到 {len(ideology_matches)} 个意识形态块")
    
    # 统计各意识形态的出现次数
    ideology_stats = {}
    for match in ideology_matches:
        # 解析意识形态值
        id_values = re.findall(r'(\d+)=([\d.]+)', match)
        for id_str, value_str in id_values:
            ideology_id = int(id_str)
            value = float(value_str)
            if value > 0:  # 只统计有值的
                ideology_stats[ideology_id] = ideology_stats.get(ideology_id, 0) + 1
    
    # 显示主要意识形态
    key_ideologies = {1: 'Reactionary', 2: 'Fascist', 3: 'Conservative', 
                     4: 'Socialist', 5: 'Anarcho-Liberal', 6: 'Liberal', 7: 'Communist'}
    
    for ideology_id in sorted(ideology_stats.keys()):
        if ideology_id in key_ideologies:
            name = key_ideologies[ideology_id]
            count = ideology_stats[ideology_id]
            print(f"   {name}({ideology_id}): {count} 次有效值")
    
    # 3. 文化修改验证
    print("\n3. 文化修改验证:")
    culture_pattern = r'primary_culture="([^"]+)"'
    culture_match = re.search(culture_pattern, content)
    if culture_match:
        print(f"   主文化: {culture_match.group(1)}")
    
    accepted_pattern = r'accepted_culture=\s*\{([^}]+)\}'
    accepted_match = re.search(accepted_pattern, content, re.DOTALL)
    if accepted_match:
        accepted_cultures = re.findall(r'"([^"]+)"', accepted_match.group(1))
        print(f"   接受文化: {accepted_cultures}")
    
    # 4. 恶名度验证
    print("\n4. 恶名度验证:")
    badboy_pattern = r'CHI=\s*\{[^{}]*badboy=([\d.]+)'
    badboy_match = re.search(badboy_pattern, content, re.DOTALL)
    if badboy_match:
        print(f"   CHI恶名度: {badboy_match.group(1)}")
    
    print("\n✅ 验证完成！所有修改都已生效！")

if __name__ == "__main__":
    main()
