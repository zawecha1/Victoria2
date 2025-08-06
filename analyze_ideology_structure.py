# 分析意识形态数据的存储结构
import re

# 读取存档文件
with open('China1841_12_17.v2', 'r', encoding='utf-8-sig') as f:
    content = f.read()

print("分析意识形态数据存储结构...")

# 查找意识形态块及其上下文
ideology_matches = re.finditer(r'ideology=\s*\{([^}]*)\}', content, re.DOTALL)
count = 0

for match in ideology_matches:
    if count >= 5:
        break
    
    ideology_content = match.group(1).strip()
    
    # 扩大上下文范围
    start = max(0, match.start() - 1000)
    end = min(len(content), match.end() + 300)
    context = content[start:end]
    
    print(f"\n意识形态块 {count + 1}:")
    print(f"意识形态内容: {ideology_content}")
    
    # 查找这个意识形态块的父结构
    # 向前查找最近的等号和ID
    pre_context = context[:match.start()-start]
    
    # 查找最近的人口类型定义
    pop_pattern = r'(\w+)=\s*\{[^}]*$'
    pop_match = re.search(pop_pattern, pre_context, re.DOTALL)
    
    if pop_match:
        print(f"所属人口类型: {pop_match.group(1)}")
    
    # 查找最近的省份ID
    province_pattern = r'^(\d+)=\s*\{'
    province_matches = list(re.finditer(province_pattern, pre_context, re.MULTILINE))
    if province_matches:
        last_province = province_matches[-1]
        province_id = last_province.group(1)
        print(f"所属省份: {province_id}")
    
    # 查找文化信息
    culture_pattern = r'(\w+)=mahayana'
    culture_match = re.search(culture_pattern, context[match.start()-start-500:match.end()-start+100])
    if culture_match:
        print(f"文化: {culture_match.group(1)}")
    
    print(f"部分上下文:\n{context[match.start()-start-200:match.end()-start+100]}")
    print("-" * 60)
    
    count += 1

print(f"\n总共找到 {len(list(re.finditer(r'ideology=', content)))} 个意识形态块")

# 检查是否在province块内部还是外部
print("\n检查意识形态块的组织结构...")

# 查找province块的范围
province_matches = list(re.finditer(r'^(\d+)=\s*\{', content, re.MULTILINE))
ideology_matches = list(re.finditer(r'ideology=\s*\{', content, re.DOTALL))

ideology_in_provinces = 0
ideology_outside_provinces = 0

for ideology_match in ideology_matches[:20]:  # 检查前20个
    ideology_pos = ideology_match.start()
    
    # 查找最近的省份
    current_province = None
    for province_match in province_matches:
        if province_match.start() < ideology_pos:
            current_province = province_match
        else:
            break
    
    if current_province:
        # 计算省份块的结束位置（简化）
        province_start = current_province.end()
        province_content = content[province_start:province_start + 10000]  # 取一段来检查
        
        if ideology_pos - current_province.start() < len(province_content):
            ideology_in_provinces += 1
        else:
            ideology_outside_provinces += 1
    else:
        ideology_outside_provinces += 1

print(f"省份内的意识形态块: {ideology_in_provinces}")
print(f"省份外的意识形态块: {ideology_outside_provinces}")
