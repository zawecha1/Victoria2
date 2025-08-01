#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Victoria II修改结果的详细报告
"""

import re

def verify_modifications_detailed(filename):
    """详细验证所有修改结果"""
    print(f"📋 详细验证报告: {filename}")
    print("="*60)
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 1. 验证中国国家配置
    print("\n1. 🇨🇳 中国国家配置验证:")
    china_pattern = r'CHI=\s*{[^{}]*(?:{[^{}]*}[^{}]*)*}'
    china_match = re.search(china_pattern, content, re.DOTALL)
    
    if china_match:
        china_block = china_match.group(0)
        print("✅ 找到中国国家配置")
        
        # 检查恶名度
        badboy_match = re.search(r'badboy=([\d.]+)', china_block)
        if badboy_match:
            badboy_value = float(badboy_match.group(1))
            print(f"✅ 恶名度 (badboy): {badboy_value}")
            if badboy_value == 0.0:
                print("   ✓ 恶名度已设为0 - 符合要求")
            else:
                print("   ⚠️ 恶名度不为0")
        else:
            print("❌ 未找到恶名度字段")
        
        # 检查主文化
        primary_culture_match = re.search(r'primary_culture="?([^"\s]+)"?', china_block)
        if primary_culture_match:
            primary_culture = primary_culture_match.group(1)
            print(f"✅ 主文化: {primary_culture}")
            if primary_culture == "beifaren":
                print("   ✓ 主文化是beifaren - 符合要求")
            else:
                print("   ⚠️ 主文化不是beifaren")
        else:
            print("❌ 未找到主文化字段")
        
        # 检查接受文化
        accepted_cultures = re.findall(r'accepted_culture=\s*\n\s*"([^"]+)"', china_block)
        if not accepted_cultures:
            # 尝试另一种格式
            accepted_pattern = r'accepted_culture=\s*(?:\n\s*"([^"]+)"\s*)*'
            block_after_accepted = re.search(r'accepted_culture=\s*\n((?:\s*"[^"]+"\s*\n)*)', china_block)
            if block_after_accepted:
                accepted_block = block_after_accepted.group(1)
                accepted_cultures = re.findall(r'"([^"]+)"', accepted_block)
        
        if accepted_cultures:
            print(f"✅ 接受文化: {accepted_cultures}")
            expected_cultures = {"nanfaren", "manchu"}
            found_cultures = set(accepted_cultures)
            if expected_cultures.issubset(found_cultures):
                print("   ✓ 包含nanfaren和manchu - 符合要求")
            else:
                missing = expected_cultures - found_cultures
                print(f"   ⚠️ 缺少接受文化: {missing}")
        else:
            print("❌ 未找到接受文化字段")
    else:
        print("❌ 未找到中国国家配置")
    
    # 2. 验证人口宗教
    print("\n2. 🙏 人口宗教验证:")
    mahayana_count = len(re.findall(r'=mahayana\b', content))
    print(f"✅ 找到 {mahayana_count} 个mahayana宗教记录")
    if mahayana_count > 1000:
        print("   ✓ 大量人口已转换为mahayana - 符合要求")
    else:
        print("   ⚠️ mahayana记录较少，可能修改不完整")
    
    # 3. 验证意识形态
    print("\n3. 🗳️ 意识形态验证:")
    liberal_count = len(re.findall(r'6=[\d.]+', content))
    conservative_count = len(re.findall(r'3=[\d.]+', content))
    print(f"✅ Liberal意识形态记录: {liberal_count}")
    print(f"✅ Conservative意识形态记录: {conservative_count}")
    
    # 检查是否有转换前的意识形态残留
    reactionary_count = len(re.findall(r'1=(?!0\.00000)[0-9.]+', content))
    fascist_count = len(re.findall(r'2=(?!0\.00000)[0-9.]+', content))
    socialist_count = len(re.findall(r'4=(?!0\.00000)[0-9.]+', content))
    anarcho_liberal_count = len(re.findall(r'5=(?!0\.00000)[0-9.]+', content))
    communist_count = len(re.findall(r'7=(?!0\.00000)[0-9.]+', content))
    
    old_ideologies = {
        "Reactionary(1)": reactionary_count,
        "Fascist(2)": fascist_count,
        "Socialist(4)": socialist_count,
        "Anarcho-Liberal(5)": anarcho_liberal_count,
        "Communist(7)": communist_count
    }
    
    print("\n   旧意识形态残留检查:")
    for ideology, count in old_ideologies.items():
        if count > 0:
            print(f"   ⚠️ {ideology}: {count} 个非零记录")
        else:
            print(f"   ✓ {ideology}: 已清零")
    
    # 4. 验证中国省份数量
    print("\n4. 🏙️ 中国省份验证:")
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    chinese_provinces = 0
    for i, match in enumerate(province_matches[:100]):  # 只检查前100个省份以节省时间
        province_id = int(match.group(1))
        start_pos = match.end()
        
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            end_pos = start_pos + 10000
        
        province_content = content[start_pos:end_pos]
        if re.search(r'owner="?CHI"?', province_content):
            chinese_provinces += 1
    
    print(f"✅ 检查了前100个省份，发现 {chinese_provinces} 个中国省份")
    
    print("\n" + "="*60)
    print("✅ 验证完成!")

if __name__ == "__main__":
    verify_modifications_detailed("China1885_03_04.v2")
