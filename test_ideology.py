#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
from victoria2_main_modifier import Victoria2Modifier

# Load the file to see how many population groups we have
modifier = Victoria2Modifier()
modifier.debug_mode = True
filename = 'China1836_02_20.v2'

print('Loading file and finding Chinese population groups...')
modifier.load_file(filename)
chinese_provinces = modifier.find_chinese_provinces_structured()
print(f'Found {len(chinese_provinces)} Chinese provinces')

# Count total population groups
total_pops = 0
for i, province in enumerate(chinese_provinces[:5]):  # Check first 5 provinces
    pops = modifier.find_population_groups_in_province(province)
    total_pops += len(pops)
    print(f'Province {i+1}: {len(pops)} population groups')

print(f'Total population groups in first 5 provinces: {total_pops}')

# Now test running the modification on a small subset
print('\n=== Testing ideology modification on first 2 provinces ===')
test_provinces = chinese_provinces[:2]
for i, province in enumerate(test_provinces):
    print(f'\nProcessing province {i+1}...')
    pops = modifier.find_population_groups_in_province(province)
    for j, pop in enumerate(pops[:2]):  # Only first 2 pops per province
        print(f'  Processing population group {j+1}...')
        result = modifier._modify_single_population_structured(pop)
        if result:
            print(f'    ✅ Modified population group {j+1}')
        else:
            print(f'    ⏭️ No changes needed for population group {j+1}')
