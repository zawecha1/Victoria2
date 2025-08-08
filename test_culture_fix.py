import re

def parse_culture_block_old(culture_content):
    """旧版本的文化解析 - 有问题的版本"""
    culture_matches = re.findall(r'"([^"]+)"', culture_content)
    return culture_matches

def parse_culture_block_new(culture_content):
    """新版本的文化解析 - 修复版本"""
    current_accepted = []
    lines = culture_content.split('\n')
    for line in lines:
        line = line.strip()
        # 只匹配形如 "culture_name" 的行（独立的文化项，不包含等号）
        if re.match(r'^"[^"]+"\s*$', line) and '=' not in line:
            match = re.search(r'"([^"]+)"', line)
            if match:
                culture_name = match.group(1)
                # 过滤掉明显不是文化的项目
                if culture_name != "noculture" and not culture_name.startswith("no"):
                    current_accepted.append(culture_name)
    return current_accepted

# 测试不同的文化块内容
test_cases = [
    # 正常情况
    '''culture=
{
    "nanfaren"
    "manchu"
    "yankee"
}''',
    
    # 包含noculture的情况
    '''culture=
{
    "nanfaren"
    "manchu"
    "yankee"
    some_setting="noculture"
}''',
    
    # 复杂情况
    '''culture=
{
    "nanfaren"
    "manchu"
    "yankee"
    technology_school="tech_school"
    civilized="yes"
    some_field="noculture"
    another="something"
}'''
]

print("文化解析测试对比:")
print("="*50)

for i, test_content in enumerate(test_cases, 1):
    print(f"\n测试用例 {i}:")
    print("内容:", repr(test_content))
    
    old_result = parse_culture_block_old(test_content)
    new_result = parse_culture_block_new(test_content)
    
    print(f"旧版本结果: {old_result}")
    print(f"新版本结果: {new_result}")
    
    if "noculture" in old_result and "noculture" not in new_result:
        print("✅ 修复成功：移除了不正确的noculture")
    elif old_result == new_result and "noculture" not in old_result:
        print("✅ 正常情况：两版本结果一致且正确")
    else:
        print("⚠️ 需要检查")
