# 查找真正的人口数据格式
import re

# 读取存档文件
with open('China1841_12_17.v2', 'r', encoding='utf-8-sig') as f:
    content = f.read()

print("寻找人口数据模式...")

# 查找culture="chinese"的模式
chinese_culture_matches = re.finditer(r'culture="chinese"', content, re.IGNORECASE)
count = 0

print('查找前5个包含culture="chinese"的位置:')
for match in chinese_culture_matches:
    if count >= 5:
        break
    
    start = max(0, match.start() - 300)
    end = min(len(content), match.end() + 300)
    context = content[start:end]
    
    print(f'\n匹配 {count + 1}:')
    print(f'位置: {match.start()}-{match.end()}')
    print(f'上下文:\n{context}')
    print('-' * 50)
    
    count += 1

# 总数
chinese_culture_count = len(re.findall(r'culture="chinese"', content, re.IGNORECASE))
print(f'\n总共找到 {chinese_culture_count} 个 culture="chinese"')

# 也查找type="chinese"
print('\n查找type="chinese"...')
chinese_type_matches = re.finditer(r'type="chinese"', content, re.IGNORECASE)
count = 0

print('查找前3个包含type="chinese"的位置:')
for match in chinese_type_matches:
    if count >= 3:
        break
    
    start = max(0, match.start() - 300)
    end = min(len(content), match.end() + 300)
    context = content[start:end]
    
    print(f'\n匹配 {count + 1}:')
    print(f'位置: {match.start()}-{match.end()}')
    print(f'上下文:\n{context}')
    print('-' * 50)
    
    count += 1

chinese_type_count = len(re.findall(r'type="chinese"', content, re.IGNORECASE))
print(f'\n总共找到 {chinese_type_count} 个 type="chinese"')
