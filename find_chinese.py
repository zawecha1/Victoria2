# 查找存档中chinese的实际格式
import re

# 读取存档文件
with open('China1841_12_17.v2', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# 搜索包含'chinese'的所有内容
chinese_matches = re.finditer(r'chinese', content, re.IGNORECASE)
count = 0

print('查找前5个包含"chinese"的位置:')
for match in chinese_matches:
    if count >= 5:
        break
    
    start = max(0, match.start() - 200)
    end = min(len(content), match.end() + 200)
    context = content[start:end]
    
    print(f'\n匹配 {count + 1}:')
    print(f'位置: {match.start()}-{match.end()}')
    print(f'上下文:\n{context}')
    print('-' * 50)
    
    count += 1

# 总共有多少个chinese
chinese_count = len(re.findall(r'chinese', content, re.IGNORECASE))
print(f'\n总共找到 {chinese_count} 个 "chinese"')
