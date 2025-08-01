#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修改结果 - 检查主修改器的效果
"""

import re
import sys

def verify_chinese_population_modifications(filename):
    """验证中国人口修改结果"""
    print(f"验证文件: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"文件读取失败: {e}")
        return
    
    # 查找中国省份
    chinese_provinces = []
    province_pattern = re.compile(r'^(\d+)=\\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    for i, match in enumerate(province_matches):
        province_id = int(match.group(1))
        start_pos = match.end()
        
        # 确定省份块的结束位置
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            next_section = re.search(r'\\n[a-z_]+=\\s*{', content[start_pos:start_pos+20000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 10000
        
        province_content = content[start_pos:end_pos]
        
        # 检查是否为中国拥有
        owner_match = re.search(r'owner="?CHI"?', province_content)
        if owner_match:
            chinese_provinces.append(province_id)
    
    print(f"找到中国省份: {len(chinese_provinces)} 个")
    
    # 验证前5个中国省份
    mahayana_count = 0
    ideology_liberal_count = 0
    ideology_conservative_count = 0
    
    for province_id in chinese_provinces[:5]:
        province_pattern = f'^{province_id}=\\s*{{'
        province_match = re.search(province_pattern, content, re.MULTILINE)
        if province_match:
            start_pos = province_match.end()
            province_content = content[start_pos:start_pos+15000]
            
            # 检查mahayana宗教
            mahayana_matches = len(re.findall(r'\\w+=mahayana', province_content))
            mahayana_count += mahayana_matches
            
            # 检查意识形态
            ideology_blocks = re.findall(r'ideology=\\s*{([^{}]*)}', province_content, re.DOTALL)
            for ideology_block in ideology_blocks:
                liberal_match = re.search(r'6=([\\d.]+)', ideology_block)
                conservative_match = re.search(r'3=([\\d.]+)', ideology_block)
                
                if liberal_match and float(liberal_match.group(1)) > 0:
                    ideology_liberal_count += 1
                if conservative_match and float(conservative_match.group(1)) > 0:
                    ideology_conservative_count += 1
    
    print(f"验证结果 (前5省份样本):")
    print(f"- mahayana宗教人口组: {mahayana_count}")
    print(f"- Liberal意识形态人口组: {ideology_liberal_count}")
    print(f"- Conservative意识形态人口组: {ideology_conservative_count}")
    
    # 检查中国恶名度
    china_pattern = r'CHI=\\s*{[^{}]*(?:{[^{}]*}[^{}]*)*}'
    china_match = re.search(china_pattern, content, re.DOTALL)
    if china_match:
        china_block = china_match.group(0)
        badboy_match = re.search(r'badboy=([\\d.]+)', china_block)
        if badboy_match:
            badboy_value = float(badboy_match.group(1))
            print(f"- 中国恶名度: {badboy_value}")
        else:
            print("- 中国恶名度: 未找到badboy字段")
    else:
        print("- 中国配置: 未找到")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("请输入要验证的存档文件名: ").strip()
    
    if filename:
        verify_chinese_population_modifications(filename)
    else:
        print("未提供文件名")
