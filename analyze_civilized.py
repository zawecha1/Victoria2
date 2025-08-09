#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 civilized 文明状态字段的所有枚举值
"""

import re
from collections import Counter

def analyze_civilized_values(filename='autosave.v2'):
    """分析文明状态字段的所有可能值"""
    print("🔍 分析 civilized 文明状态字段...")
    
    # 读取文件
    try:
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                print(f"✅ 文件读取成功 (编码: {encoding})")
                break
            except UnicodeDecodeError:
                continue
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 查找所有国家块
    print("🏛️ 查找国家块...")
    country_pattern = r'([A-Z]{3})\s*=\s*\{'
    country_matches = list(re.finditer(country_pattern, content))
    
    civilized_values = Counter()
    civilized_examples = {}
    total_countries = 0
    
    print(f"📊 找到 {len(country_matches)} 个潜在国家块，分析中...")
    
    for match in country_matches:
        tag = match.group(1)
        start_pos = match.end() - 1  # 指向开始的 {
        
        # 找到匹配的结束花括号
        end_pos = find_matching_brace(content, start_pos)
        
        if end_pos != -1:
            block_content = content[start_pos + 1:end_pos]
            
            # 判断是否为国家定义块
            if is_country_definition(block_content):
                total_countries += 1
                
                # 查找 civilized 字段
                civilized_match = re.search(r'civilized\s*=\s*([^\n\s]+)', block_content)
                if civilized_match:
                    value = civilized_match.group(1).strip().strip('"')
                    civilized_values[value] += 1
                    
                    # 保存示例
                    if value not in civilized_examples or len(civilized_examples[value]) < 5:
                        if value not in civilized_examples:
                            civilized_examples[value] = []
                        civilized_examples[value].append(tag)
                else:
                    # 没有 civilized 字段的国家
                    civilized_values['<未设置>'] += 1
                    if '<未设置>' not in civilized_examples:
                        civilized_examples['<未设置>'] = []
                    if len(civilized_examples['<未设置>']) < 5:
                        civilized_examples['<未设置>'].append(tag)
    
    # 显示结果
    print(f"\n" + "="*60)
    print(f"🏛️ Victoria II civilized 文明状态字段分析")
    print(f"="*60)
    print(f"📊 总分析国家数: {total_countries}")
    print(f"🎯 发现的 civilized 值类型: {len(civilized_values)}")
    
    print(f"\n📋 civilized 字段所有枚举值:")
    print(f"{'值':<15} {'数量':<8} {'百分比':<10} {'示例国家'}")
    print("-" * 60)
    
    for value, count in civilized_values.most_common():
        percentage = count / total_countries * 100
        examples = ', '.join(civilized_examples[value][:5])
        print(f"{value:<15} {count:<8} {percentage:>6.1f}%    {examples}")
    
    # 详细说明
    print(f"\n📚 civilized 字段含义说明:")
    print("-" * 60)
    
    field_meanings = {
        'yes': '已文明化国家 - 可以进行完整的外交、贸易、科技研发',
        'no': '未文明化国家 - 科技、外交受限，需要通过改革实现文明化',
        '<未设置>': '默认值 - 通常表示未文明化状态'
    }
    
    for value in civilized_values.keys():
        meaning = field_meanings.get(value, '未知状态 - 可能是特殊情况或数据错误')
        print(f"• {value}: {meaning}")
    
    # 文明化vs未文明化统计
    print(f"\n🌍 文明化状态统计:")
    print("-" * 60)
    
    civilized_count = civilized_values.get('yes', 0)
    uncivilized_count = total_countries - civilized_count
    
    print(f"已文明化国家 (yes): {civilized_count} 个 ({civilized_count/total_countries*100:.1f}%)")
    print(f"未文明化国家 (no/未设置): {uncivilized_count} 个 ({uncivilized_count/total_countries*100:.1f}%)")
    
    return civilized_values

def find_matching_brace(content: str, start_pos: int) -> int:
    """找到匹配的结束花括号"""
    if start_pos >= len(content) or content[start_pos] != '{':
        return -1
    
    brace_count = 1
    pos = start_pos + 1
    
    while pos < len(content) and brace_count > 0:
        char = content[pos]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        pos += 1
    
    return pos - 1 if brace_count == 0 else -1

def is_country_definition(block_content: str) -> bool:
    """判断是否为国家定义块"""
    indicators = ['primary_culture', 'capital', 'government', 'technology', 
                 'money', 'prestige', 'consciousness', 'literacy']
    
    count = sum(1 for indicator in indicators if indicator in block_content)
    return count >= 3

def analyze_civilization_requirements():
    """分析文明化要求相关字段"""
    print(f"\n🎓 Victoria II 文明化机制说明:")
    print("="*60)
    
    requirements = [
        "文明化需要满足以下条件之一:",
        "1. 军事点数 (Army tech) 达到一定水平",
        "2. 海军点数 (Navy tech) 达到一定水平", 
        "3. 工业点数 (Commerce tech) 达到一定水平",
        "4. 文化点数 (Culture tech) 达到一定水平",
        "",
        "文明化后的变化:",
        "• 可以进行完整的外交活动",
        "• 可以建造工厂和铁路",
        "• 可以殖民非洲等地区",
        "• 可以使用所有科技",
        "• 人口增长和教育效率提高"
    ]
    
    for req in requirements:
        print(f"  {req}")

def main():
    """主函数"""
    print("🚀 Victoria II civilized 字段分析器")
    print("="*60)
    
    # 分析 civilized 字段
    civilized_values = analyze_civilized_values()
    
    # 显示文明化机制说明
    analyze_civilization_requirements()
    
    print(f"\n✅ 分析完成!")
    print(f"💡 总结: civilized 字段主要有 'yes' 和 'no' 两个值，控制国家的文明化状态")

if __name__ == "__main__":
    main()
