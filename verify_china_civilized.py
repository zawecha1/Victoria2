#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证中国文明化状态修改结果
"""

import re

def verify_china_civilized():
    """验证中国的文明化状态"""
    try:
        with open('autosave.v2', 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        print('🔍 验证中国civilized状态...')
        
        # 使用正则表达式找CHI块
        chi_pattern = r'CHI\s*=\s*\{'
        match = re.search(chi_pattern, content)
        
        if match:
            # 获取CHI块的内容
            bracket_count = 0
            chi_block_start = match.end() - 1  # 从{开始
            chi_block_end = chi_block_start
            
            for i, char in enumerate(content[chi_block_start:], chi_block_start):
                if char == '{':
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        chi_block_end = i
                        break
            
            chi_content = content[chi_block_start:chi_block_end + 1]
            print(f'📄 CHI块大小: {len(chi_content)} 字符')
            
            # 在CHI块中搜索civilized
            if 'civilized' in chi_content:
                lines = chi_content.split('\n')
                for line in lines:
                    if 'civilized' in line:
                        print(f'🎯 找到: {line.strip()}')
                        
                        # 检查值
                        if 'civilized=yes' in line:
                            print('✅ 验证成功: 中国civilized=yes')
                        elif 'civilized="yes"' in line:
                            print('✅ 验证成功: 中国civilized="yes"')
                        elif 'civilized=no' in line:
                            print('❌ 验证失败: 中国civilized=no')
                        elif 'civilized="no"' in line:
                            print('❌ 验证失败: 中国civilized="no"')
                        else:
                            print(f'⚠️  其他值: {line.strip()}')
                        break
            else:
                print('❌ CHI块中没有找到civilized字段')
                
        else:
            print('❌ 未找到CHI块')
            
    except Exception as e:
        print(f'错误: {e}')

if __name__ == "__main__":
    verify_china_civilized()
