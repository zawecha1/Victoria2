# 分析文化分布
import re

with open('China1841_12_17.v2', 'r', encoding='utf-8-sig') as f:
    content = f.read()

cultures_with_mahayana = re.findall(r'(\w+)=mahayana', content)
culture_counts = {}
for culture in cultures_with_mahayana:
    culture_counts[culture] = culture_counts.get(culture, 0) + 1

chinese_cultures = ['beifaren', 'nanfaren', 'manchu', 'han', 'cantonese', 'min', 'hakka']

print('中文文化统计:')
chinese_total = 0
for culture in chinese_cultures:
    count = culture_counts.get(culture, 0)
    chinese_total += count
    print(f'  {culture}: {count}')
print(f'中文文化总计: {chinese_total}')

print('\n所有文化排序:')
for culture, count in sorted(culture_counts.items(), key=lambda x: x[1], reverse=True):
    is_chinese = "✅" if culture in chinese_cultures else "❌"
    print(f'  {is_chinese} {culture}: {count}')

total_mahayana = sum(culture_counts.values())
print(f'\nmahayana总数: {total_mahayana}')
print(f'中文文化占比: {chinese_total/total_mahayana*100:.1f}%')
