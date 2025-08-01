#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本 - 查找中国真实的badboy值
"""
import re

def find_china_badboy_detailed(filename):
    """详细查找中国的badboy值"""
    print(f"调试: 查找文件 {filename} 中的中国badboy值")
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        print(f"文件读取成功，大小: {len(content):,} 字符")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 1. 查找所有CHI= 开头的块
    print("\n1. 查找所有CHI=块:")
    chi_pattern = r'CHI=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*?)}'
    chi_matches = list(re.finditer(chi_pattern, content, re.DOTALL))
    
    print(f"找到 {len(chi_matches)} 个CHI=块")
    
    # 2. 分析每个CHI块
    for i, match in enumerate(chi_matches[:10]):  # 只看前10个
        chi_content = match.group(1)
        start_pos = match.start()
        
        # 查找badboy值
        badboy_match = re.search(r'badboy=([\d.]+)', chi_content)
        primary_culture_match = re.search(r'primary_culture="?([^"\s]+)"?', chi_content)
        technology_match = re.search(r'technology=', chi_content)
        
        print(f"\nCHI块 #{i+1} (位置: {start_pos}):")
        print(f"  - badboy: {badboy_match.group(1) if badboy_match else '未找到'}")
        print(f"  - primary_culture: {primary_culture_match.group(1) if primary_culture_match else '未找到'}")
        print(f"  - 包含technology: {'是' if technology_match else '否'}")
        print(f"  - 内容长度: {len(chi_content)} 字符")
        
        # 如果这个块包含technology，很可能是主要的国家定义
        if technology_match:
            print(f"  ⭐ 这可能是主要国家定义 (包含technology)")
            print(f"  内容预览: {chi_content[:200]}...")
    
    # 3. 搜索所有badboy值
    print(f"\n3. 查找所有badboy值:")
    all_badboy_matches = list(re.finditer(r'badboy=([\d.]+)', content))
    print(f"总共找到 {len(all_badboy_matches)} 个badboy值")
    
    # 显示所有不为0的badboy值
    non_zero_badboy = []
    for match in all_badboy_matches:
        value = float(match.group(1))
        if value > 0:
            non_zero_badboy.append((value, match.start()))
    
    print(f"非零badboy值: {len(non_zero_badboy)} 个")
    for value, pos in non_zero_badboy[:20]:  # 显示前20个
        print(f"  badboy={value} (位置: {pos})")
    
    # 4. 查找包含56.31的badboy值
    print(f"\n4. 查找包含56.31的badboy值:")
    target_badboy_matches = list(re.finditer(r'badboy=56\.31\d*', content))
    if target_badboy_matches:
        for match in target_badboy_matches:
            print(f"找到目标badboy值: {match.group(0)} (位置: {match.start()})")
            
            # 向前查找对应的国家标识
            search_start = max(0, match.start() - 5000)
            search_content = content[search_start:match.start()]
            
            # 查找最近的国家标识
            country_patterns = [r'([A-Z]{3})=\s*{[^{}]*$', r'^([A-Z]{3})=']
            for pattern in country_patterns:
                country_matches = list(re.finditer(pattern, search_content, re.MULTILINE))
                if country_matches:
                    last_country = country_matches[-1].group(1)
                    print(f"  对应国家: {last_country}")
                    break
    else:
        print("未找到badboy=56.31的值")
    
    # 5. 使用更宽松的模式查找CHI主要定义
    print(f"\n5. 使用更宽松的CHI查找:")
    
    # 查找具有大量内容的CHI块
    large_chi_pattern = r'CHI=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*?)}'
    large_chi_matches = []
    
    for match in re.finditer(large_chi_pattern, content, re.DOTALL):
        chi_content = match.group(1)
        if len(chi_content) > 1000:  # 大于1000字符的块
            large_chi_matches.append((match, len(chi_content)))
    
    print(f"找到 {len(large_chi_matches)} 个大型CHI块 (>1000字符)")
    
    for match, size in large_chi_matches[:3]:  # 查看前3个最大的
        chi_content = match.group(1)
        badboy_match = re.search(r'badboy=([\d.]+)', chi_content)
        print(f"  大型CHI块 (大小: {size}): badboy={badboy_match.group(1) if badboy_match else '未找到'}")

if __name__ == "__main__":
    find_china_badboy_detailed("China2281_01_01.v2")
