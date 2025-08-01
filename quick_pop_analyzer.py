#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 人口属性快速分析器
快速版本，专注于枚举人口的各种属性
"""

import re
from collections import defaultdict, Counter

def analyze_population_attributes(filename: str):
    """快速分析人口属性"""
    print(f"分析文件: {filename}")
    
    # 读取文件
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        print(f"文件大小: {len(content):,} 字符")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 收集人口类型
    pop_types = set()
    cultures = set()
    religions = set()
    
    # 查找所有人口类型
    known_pops = ['farmers', 'labourers', 'slaves', 'clerks', 'artisans', 'craftsmen',
                  'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                  'bureaucrats', 'intellectuals']
    
    for pop_type in known_pops:
        # 查找该人口类型的所有实例
        pattern = f'{pop_type}=\s*{{([^{{}}]*(?:{{[^{{}}]*}}[^{{}}]*)*)}}'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            pop_types.add(pop_type)
            print(f"找到 {len(matches)} 个 {pop_type} 人口组")
            
            # 分析前5个样本
            for i, match in enumerate(matches[:5]):
                # 查找文化=宗教组合
                culture_religion = re.findall(r'(\w+)=(\w+)', match)
                for culture, religion in culture_religion:
                    # 排除数字和已知非文化字段
                    if (not culture.isdigit() and not religion.isdigit() and 
                        culture not in ['size', 'money', 'con', 'mil', 'literacy', 'id', 'type', 'everyday', 'luxury'] and
                        religion not in ['size', 'money', 'con', 'mil', 'literacy', 'id', 'type', 'everyday', 'luxury']):
                        cultures.add(culture)
                        religions.add(religion)
                        if i == 0:  # 只显示第一个样本
                            print(f"  样本: {culture}={religion}")
    
    # 显示结果
    print(f"\n{'='*60}")
    print("人口属性枚举汇总")
    print(f"{'='*60}")
    
    print(f"\n👥 人口类型 ({len(pop_types)} 种):")
    for i, pop_type in enumerate(sorted(pop_types), 1):
        print(f"  {i:2d}. {pop_type}")
    
    print(f"\n🎭 文化类型 ({len(cultures)} 种):")
    for i, culture in enumerate(sorted(cultures), 1):
        if i <= 30:  # 显示前30个
            print(f"  {i:2d}. {culture}")
        elif i == 31:
            print(f"  ... 还有 {len(cultures) - 30} 个文化")
            break
    
    print(f"\n⛪ 宗教类型 ({len(religions)} 种):")
    for i, religion in enumerate(sorted(religions), 1):
        print(f"  {i:2d}. {religion}")
    
    # 查找政治议题
    print(f"\n🗳️  政治议题分析:")
    issues_pattern = r'issues=\s*{([^{}]*)}'
    issues_blocks = re.findall(issues_pattern, content)
    if issues_blocks:
        print(f"找到 {len(issues_blocks)} 个政治议题块")
        # 分析第一个块的结构
        first_block = issues_blocks[0]
        issue_pairs = re.findall(r'(\d+)=([\d.]+)', first_block)
        print(f"  议题数量: {len(issue_pairs)}")
        print(f"  样本议题ID: {[pair[0] for pair in issue_pairs[:10]]}")
    
    # 查找意识形态
    print(f"\n💭 意识形态分析:")
    ideology_pattern = r'ideology=\s*{([^{}]*)}'
    ideology_blocks = re.findall(ideology_pattern, content)
    if ideology_blocks:
        print(f"找到 {len(ideology_blocks)} 个意识形态块")
        first_block = ideology_blocks[0]
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', first_block)
        print(f"  意识形态数量: {len(ideology_pairs)}")
        print(f"  样本意识形态ID: {[pair[0] for pair in ideology_pairs[:10]]}")
    
    # 查找需求
    print(f"\n🛒 需求分析:")
    needs_patterns = ['everyday_needs', 'luxury_needs']
    for need_type in needs_patterns:
        need_matches = re.findall(f'{need_type}=([\d.]+)', content)
        if need_matches:
            avg_need = sum(float(x) for x in need_matches[:100]) / min(len(need_matches), 100)
            print(f"  {need_type}: {len(need_matches)} 个记录, 平均值: {avg_need:.3f}")

def main():
    filename = input("请输入存档文件名 (默认: China1836_04_29.v2): ").strip()
    if not filename:
        filename = "China1836_04_29.v2"
    
    analyze_population_attributes(filename)

if __name__ == "__main__":
    main()
