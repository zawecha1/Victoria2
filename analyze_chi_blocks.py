#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析autosave.v2中所有CHI相关的块
"""

import re

def analyze_chi_blocks():
    """分析所有CHI相关的块"""
    try:
        with open('autosave.v2', 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        print('🔍 分析所有CHI相关块...')
        
        # 查找所有CHI相关的模式
        patterns = [
            (r'CHI\s*=\s*\{', "CHI国家块"),
            (r'\bCHI\s*=', "CHI赋值"),
            (r'"CHI"', "CHI字符串"),
            (r'\bCHI\b', "CHI关键词"),
        ]
        
        total_found = 0
        
        for pattern, description in patterns:
            matches = list(re.finditer(pattern, content))
            print(f'\n📊 {description}: 找到 {len(matches)} 个')
            
            if matches:
                total_found += len(matches)
                
                # 显示前几个匹配的上下文
                for i, match in enumerate(matches[:5]):  # 只显示前5个
                    start_pos = max(0, match.start() - 50)
                    end_pos = min(len(content), match.end() + 50)
                    context = content[start_pos:end_pos]
                    
                    print(f'  匹配 {i+1}: 位置 {match.start()}')
                    context_clean = context.replace(chr(10), "\\n").replace(chr(13), "\\r")[:100]
                    print(f'    上下文: {context_clean}...')
                    
                    # 对于CHI={}块，提取完整内容
                    if pattern == r'CHI\s*=\s*\{':
                        print(f'    🔎 分析CHI块结构...')
                        
                        # 获取CHI块的内容
                        bracket_count = 0
                        chi_block_start = match.end() - 1  # 从{开始
                        chi_block_end = chi_block_start
                        
                        for j, char in enumerate(content[chi_block_start:], chi_block_start):
                            if char == '{':
                                bracket_count += 1
                            elif char == '}':
                                bracket_count -= 1
                                if bracket_count == 0:
                                    chi_block_end = j
                                    break
                        
                        chi_block_content = content[chi_block_start:chi_block_end + 1]
                        print(f'    📦 块大小: {len(chi_block_content)} 字符')
                        print(f'    📄 内容: {chi_block_content[:200]}...')
                        
                        # 检查是否有civilized字段
                        if 'civilized' in chi_block_content:
                            civilized_match = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', chi_block_content)
                            if civilized_match:
                                print(f'    ✅ 找到civilized字段: {civilized_match.group(0)}')
                            else:
                                print(f'    ❓ 包含civilized但无法解析')
                        else:
                            print(f'    ❌ 无civilized字段')
                
                if len(matches) > 5:
                    print(f'    ... 还有 {len(matches) - 5} 个匹配')
        
        print(f'\n📈 总计找到 {total_found} 个CHI相关引用')
        
        # 特别分析civilized字段在整个文件中的分布
        print('\n🔍 分析整个文件中的civilized字段...')
        civilized_matches = list(re.finditer(r'civilized\s*=\s*"?([^"\s}]+)"?', content))
        print(f'📊 总共找到 {len(civilized_matches)} 个civilized字段')
        
        if civilized_matches:
            # 统计值分布
            values = {}
            for match in civilized_matches:
                value = match.group(1)
                values[value] = values.get(value, 0) + 1
            
            print('📈 值分布:')
            for value, count in sorted(values.items()):
                print(f'  {value}: {count} 次')
        
    except Exception as e:
        print(f'错误: {e}')

if __name__ == "__main__":
    analyze_chi_blocks()
