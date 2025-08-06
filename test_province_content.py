# 直接测试省份内容和人口匹配
import re

# 读取存档文件
with open('China1841_12_17.v2', 'r', encoding='utf-8-sig') as f:
    content = f.read()

print("查找省份1496的内容...")

# 查找省份1496（应该是中国省份）
province_1496_pattern = r'^1496\s*=\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
match = re.search(province_1496_pattern, content, re.MULTILINE | re.DOTALL)

if match:
    province_content = match.group(1)
    print(f"省份1496内容长度: {len(province_content)}")
    print(f"前500字符:\n{province_content[:500]}")
    
    # 检查是否包含owner=CHI
    if 'owner="CHI"' in province_content or 'owner=CHI' in province_content:
        print("✅ 确认是中国省份")
    else:
        print("❌ 不是中国省份")
    
    # 检查是否包含人口数据
    pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists']
    
    found_pops = []
    for pop_type in pop_types:
        if f'{pop_type}=' in province_content:
            found_pops.append(pop_type)
    
    print(f"找到的人口类型: {found_pops}")
    
    # 检查第一个人口类型的详细内容
    if found_pops:
        first_pop = found_pops[0]
        pop_pattern = rf'{first_pop}=\s*\{{([^}}]*(?:\{{[^}}]*\}}[^}}]*)*)\}}'
        pop_match = re.search(pop_pattern, province_content, re.DOTALL)
        
        if pop_match:
            pop_content = pop_match.group(1)
            print(f"\n{first_pop}人口内容:")
            print(pop_content[:300])
            
            # 检查是否包含意识形态
            if 'ideology=' in pop_content:
                print(f"✅ {first_pop}包含意识形态数据")
            else:
                print(f"❌ {first_pop}不包含意识形态数据")
else:
    print("未找到省份1496")

print("\n" + "="*50)
print("查找任意省份的人口数据...")

# 查找任意包含ideology的内容
ideology_matches = re.finditer(r'ideology=\s*\{([^}]*)\}', content, re.DOTALL)
count = 0

for match in ideology_matches:
    if count >= 3:
        break
    
    ideology_content = match.group(1)
    
    # 找到这个意识形态块所在的上下文
    start = max(0, match.start() - 500)
    end = min(len(content), match.end() + 200)
    context = content[start:end]
    
    print(f"\n意识形态块 {count + 1}:")
    print(f"内容: {ideology_content.strip()}")
    print(f"上下文: ...{context[450:]}...")
    
    count += 1
