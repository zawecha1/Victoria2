#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找真正的CHI国家定义块
"""

import re

def find_chi_in_countries():
    """在countries块中查找CHI国家定义"""
    try:
        with open('autosave.v2', 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        print('🔍 查找countries块中的CHI国家定义...')
        
        # 查找包含countries={}的顶级块
        countries_pattern = r'countries\s*=\s*\{'
        match = re.search(countries_pattern, content)
        
        if match:
            print('✅ 找到countries块')
            
            # 获取countries块的内容
            bracket_count = 0
            countries_start = match.end() - 1  # 从{开始
            countries_end = countries_start
            
            for i, char in enumerate(content[countries_start:], countries_start):
                if char == '{':
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        countries_end = i
                        break
            
            countries_content = content[countries_start:countries_end + 1]
            print(f'📦 countries块大小: {len(countries_content)} 字符')
            
            # 在countries块中查找CHI - 使用更复杂的正则
            chi_pattern = r'CHI\s*=\s*\{[^}]*\}'
            chi_matches = list(re.finditer(chi_pattern, countries_content))
            
            if chi_matches:
                print(f'🎯 在countries块中找到 {len(chi_matches)} 个CHI块')
                
                for i, match in enumerate(chi_matches):
                    chi_block = match.group(0)
                    print(f'\\n📄 CHI块 {i+1}:')
                    print(f'    大小: {len(chi_block)} 字符')
                    print(f'    内容预览: {chi_block[:200]}...')
                    
                    if 'civilized' in chi_block:
                        civilized_match = re.search(r'civilized\s*=\s*"?([^"\\s}]+)"?', chi_block)
                        if civilized_match:
                            print(f'    ✅ 找到civilized: {civilized_match.group(0)}')
                        else:
                            print(f'    ❓ 包含civilized但无法解析')
                    else:
                        print(f'    ❌ 无civilized字段')
            else:
                print('❌ countries块中未找到CHI块')
                
                # 试试更宽松的搜索
                print('\\n🔍 尝试更宽松的CHI搜索...')
                loose_chi_pattern = r'CHI\s*='
                loose_matches = list(re.finditer(loose_chi_pattern, countries_content))
                print(f'找到 {len(loose_matches)} 个CHI引用')
                
                if loose_matches:
                    for i, match in enumerate(loose_matches[:3]):  # 只看前3个
                        start_pos = match.start()
                        context_start = max(0, start_pos - 50)
                        context_end = min(len(countries_content), start_pos + 200)
                        context = countries_content[context_start:context_end]
                        print(f'  匹配 {i+1}: {context}')
        else:
            print('❌ 未找到countries块')
        
        # 也尝试在整个文件中搜索包含civilized的CHI块
        print('\\n🔍 在整个文件中搜索包含civilized的CHI块...')
        civilized_chi_pattern = r'CHI\s*=\s*\{[^}]*civilized[^}]*\}'
        civilized_chi_matches = list(re.finditer(civilized_chi_pattern, content))
        
        if civilized_chi_matches:
            print(f'🎯 找到 {len(civilized_chi_matches)} 个包含civilized的CHI块')
            
            for i, match in enumerate(civilized_chi_matches):
                chi_block = match.group(0)
                print(f'\\n📄 包含civilized的CHI块 {i+1}:')
                print(f'    位置: {match.start()}-{match.end()}')
                print(f'    大小: {len(chi_block)} 字符')
                print(f'    内容: {chi_block}')
                
                civilized_match = re.search(r'civilized\s*=\s*"?([^"\\s}]+)"?', chi_block)
                if civilized_match:
                    print(f'    ✅ civilized值: {civilized_match.group(1)}')
        else:
            print('❌ 整个文件中未找到包含civilized的CHI块')
            
    except Exception as e:
        print(f'错误: {e}')

if __name__ == "__main__":
    find_chi_in_countries()
