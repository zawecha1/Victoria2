import re

# 模拟一个culture块的内容，可能包含问题
sample_culture_content = '''culture=
{
    "nanfaren"
    "manchu" 
    "yankee"
    # 可能还有其他内容
    some_field="noculture"
    another_setting="something"
}'''

print("测试文化解析:")
print("原始内容:")
print(sample_culture_content)
print()

# 当前使用的正则表达式
culture_matches = re.findall(r'"([^"]+)"', sample_culture_content)
print("当前正则表达式结果:", culture_matches)
print()

# 更安全的解析方法 - 只匹配在花括号内且独占一行的引号内容
safer_matches = []
lines = sample_culture_content.split('\n')
for line in lines:
    line = line.strip()
    # 只匹配形如 "culture_name" 的行（独立的文化项）
    if re.match(r'^"[^"]+"\s*$', line):
        match = re.search(r'"([^"]+)"', line)
        if match:
            safer_matches.append(match.group(1))

print("更安全的解析结果:", safer_matches)
