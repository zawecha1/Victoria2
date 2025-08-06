# 测试修改所有中国省份内的人口意识形态
import re

print("准备修改所有中国省份内的人口意识形态...")

# 读取存档文件
with open('China1841_12_17.v2', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# 查找一个具体的省份测试
test_province_id = 1  # 从分析中知道这是中国省份

province_pattern = f'^{test_province_id}=\\s*{{'
province_match = re.search(province_pattern, content, re.MULTILINE)

if province_match:
    print(f"找到省份 {test_province_id}")
    
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
        
        # 查找所有意识形态块
        ideology_matches = list(re.finditer(r'ideology=\\s*\\{([^}]*)\\}', province_content, re.DOTALL))
        print(f"省份内找到 {len(ideology_matches)} 个意识形态块")
        
        # 显示前3个意识形态块的详情
        for i, match in enumerate(ideology_matches[:3]):
            ideology_content = match.group(1).strip()
            print(f"\\n意识形态块 {i+1}: {ideology_content}")
            
            # 检查是否包含旧意识形态
            ideology_pairs = re.findall(r'(\\d+)=([\\d.]+)', ideology_content)
            ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
            old_ideologies = {id: val for id, val in ideology_dist.items() if id in [1, 2, 4, 5, 7] and val > 0}
            
            if old_ideologies:
                print(f"  需要转换的旧意识形态: {old_ideologies}")
                
                # 计算新的分布
                total_old = sum(old_ideologies.values())
                conservative_current = ideology_dist.get(3, 0)
                liberal_current = ideology_dist.get(6, 0)
                
                # 按60/40比例分配
                conservative_new = conservative_current + total_old * 0.6
                liberal_new = liberal_current + total_old * 0.4
                
                print(f"  转换后: Conservative(3)={conservative_new:.5f}, Liberal(6)={liberal_new:.5f}")
                print(f"  旧意识形态将设为0")
            else:
                print(f"  无需转换")
    else:
        print("省份块结构错误")
else:
    print(f"未找到省份 {test_province_id}")

print(f"\\n总体统计：")
total_ideologies = len(re.findall(r'ideology=\\s*\\{', content))
print(f"整个存档中的意识形态块数量: {total_ideologies}")

# 统计各种文化的数量
cultures_with_mahayana = re.findall(r'(\\w+)=mahayana', content)
culture_counts = {}
for culture in cultures_with_mahayana:
    culture_counts[culture] = culture_counts.get(culture, 0) + 1

print(f"\\n各文化的mahayana数量:")
for culture, count in sorted(culture_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {culture}: {count}")
