# 修复正则表达式问题的测试
import re

print("修复版本的意识形态分析...")

# 读取存档文件
with open('China1841_12_17.v2', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# 查找省份1
province_pattern = r'^1\s*=\s*\{'
province_match = re.search(province_pattern, content, re.MULTILINE)

if province_match:
    print(f"找到省份 1")
    
    # 找到省份块的结束位置
    start_pos = province_match.end()
    brace_count = 1
    current_pos = start_pos
    
    while current_pos < len(content) and brace_count > 0:
        char = content[current_pos]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        current_pos += 1
    
    if brace_count == 0:
        province_content = content[start_pos:current_pos-1]
        print(f"省份内容长度: {len(province_content)}")
        
        # 修复正则表达式 - 去掉多余的转义
        ideology_matches = list(re.finditer(r'ideology=\s*\{([^}]*)\}', province_content, re.DOTALL))
        print(f"省份内找到 {len(ideology_matches)} 个意识形态块")
        
        if len(ideology_matches) == 0:
            print("检查省份内容片段:")
            print(province_content[:1000])
            
            # 检查是否包含"ideology"字符串
            if 'ideology' in province_content:
                print(f"✅ 省份内容包含'ideology'字符串")
                ideology_positions = [m.start() for m in re.finditer(r'ideology', province_content)]
                print(f"出现位置: {ideology_positions[:5]}")
            else:
                print("❌ 省份内容不包含'ideology'字符串")
        
        # 显示意识形态块详情
        for i, match in enumerate(ideology_matches[:3]):
            ideology_content = match.group(1).strip()
            print(f"\n意识形态块 {i+1}: {ideology_content}")
            
            # 检查是否包含旧意识形态
            ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
            ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
            old_ideologies = {id: val for id, val in ideology_dist.items() if id in [1, 2, 4, 5, 7] and val > 0}
            
            if old_ideologies:
                print(f"  需要转换的旧意识形态: {old_ideologies}")
            else:
                print(f"  无需转换")
    else:
        print("省份块结构错误")
else:
    print(f"未找到省份 1")

print(f"\n总体统计：")
# 修复正则表达式
total_ideologies = len(re.findall(r'ideology=\s*\{', content))
print(f"整个存档中的意识形态块数量: {total_ideologies}")

# 统计各种文化的数量
cultures_with_mahayana = re.findall(r'(\w+)=mahayana', content)
culture_counts = {}
for culture in cultures_with_mahayana:
    culture_counts[culture] = culture_counts.get(culture, 0) + 1

print(f"\n各文化的mahayana数量:")
for culture, count in sorted(culture_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {culture}: {count}")
    
print(f"\n检查修改函数使用的中文文化列表:")
chinese_cultures = ['beifaren', 'nanfaren', 'manchu', 'han', 'cantonese', 'min', 'hakka']
for culture in chinese_cultures:
    count = culture_counts.get(culture, 0)
    print(f"  {culture}: {count} 个")
    
print(f"\n检查非中文但有mahayana的文化:")
for culture, count in culture_counts.items():
    if culture not in chinese_cultures and count > 100:
        print(f"  {culture}: {count} 个")
