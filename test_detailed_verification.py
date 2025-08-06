#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import sys

# Force reload the module
if 'victoria2_main_modifier' in sys.modules:
    importlib.reload(sys.modules['victoria2_main_modifier'])

from victoria2_main_modifier import Victoria2Modifier

# Test verification function on more provinces
modifier = Victoria2Modifier()
modifier.debug_mode = False
print('Loading file...')
modifier.load_file('China1836_02_20.v2')

# Get all Chinese provinces
chinese_provinces = modifier.find_chinese_provinces_structured()
print(f'Found {len(chinese_provinces)} Chinese provinces total')

# Check the first 50 provinces instead of just 10
print('\nChecking ideology distribution in first 50 provinces...')

pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
             'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
             'bureaucrats', 'intellectuals']

total_ideology_blocks = 0
failed_conversions = 0
all_ideology_distributions = []

for i, province_block in enumerate(chinese_provinces[:50]):  # Check first 50 provinces
    province_id_match = re.match(r'^(\d+)=', province_block.content)
    province_id = province_id_match.group(1) if province_id_match else f"Province_{i+1}"
    
    province_ideology_blocks = 0
    
    for child_block in province_block.children:
        if any(pop_type in child_block.content for pop_type in pop_types):
            # Look for ideology blocks
            ideology_pattern = r'ideology=\s*\{([^}]*)\}'
            ideology_match = re.search(ideology_pattern, child_block.content, re.DOTALL)
            
            if ideology_match:
                total_ideology_blocks += 1
                province_ideology_blocks += 1
                ideology_content = ideology_match.group(1)
                
                # Extract ideology data
                ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
                ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
                
                # Check for old ideologies
                old_ideologies = {id: val for id, val in ideology_dist.items() if id in [1, 2, 4, 5, 7] and val > 0}
                
                if old_ideologies:
                    failed_conversions += 1
                    print(f"❌ 省份 {province_id}: 残留旧意识形态 {old_ideologies}")
                    print(f"   完整分布: {ideology_dist}")
                
                all_ideology_distributions.append(ideology_dist)
    
    if i < 10 and province_ideology_blocks == 0:
        print(f"Province {province_id}: 无意识形态块")

print(f'\n📊 检查结果:')
print(f'总意识形态块数: {total_ideology_blocks}')
print(f'有残留旧意识形态的块数: {failed_conversions}')

if all_ideology_distributions:
    # Show a sample of ideology distributions
    print(f'\n📝 前5个意识形态分布样本:')
    for i, dist in enumerate(all_ideology_distributions[:5]):
        print(f'  {i+1}: {dist}')
else:
    print('❌ 未找到任何意识形态分布数据')

import re
