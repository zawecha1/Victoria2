#!/usr/bin/env python3
# -*- coding: utf-8 -*-

content = open('autosave.v2', 'r', encoding='latin1').read()
print(f'文件大小: {len(content):,} 字符')
print(f'开花括号: {content.count("{"):,}')
print(f'闭花括号: {content.count("}"):,}')
print(f'差异: {content.count("{") - content.count("}")}')
print('✓ 文件完整性正常' if content.count('{') - content.count('}') == -1 else '✗ 花括号不平衡')
