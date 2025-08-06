# 测试条件检测逻辑
import re

# 读取存档文件
with open('China1841_12_17.v2', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# 查找中国人口
chinese_population_pattern = r'(\d+)\s*=\s*\{\s*type\s*=\s*"chinese"[^}]*culture\s*=\s*"chinese"[^}]*\}'
chinese_matches = re.findall(chinese_population_pattern, content, re.DOTALL)

print(f"找到中国人口: {len(chinese_matches)} 个")

# 测试完整的人口块匹配
chinese_pop_full_pattern = r'(\d+)\s*=\s*\{[^}]*type\s*=\s*"chinese"[^}]*\}'
chinese_pop_matches = re.finditer(chinese_pop_full_pattern, content, re.DOTALL)

ideology_change_count = 0
for i, match in enumerate(chinese_pop_matches):
    if i >= 5:  # 只检查前5个
        break
        
    pop_content = match.group(0)
    print(f"\n人口块 {i+1}:")
    print(f"  内容长度: {len(pop_content)}")
    
    # 检查是否包含意识形态
    if 'ideology=' in pop_content:
        print(f"  包含意识形态数据")
        
        # 提取意识形态块
        ideology_pattern = r'ideology=\s*\{([^}]*)\}'
        ideology_match = re.search(ideology_pattern, pop_content, re.DOTALL)
        
        if ideology_match:
            ideology_content = ideology_match.group(1)
            
            # 解析意识形态数据
            ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
            ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
            
            # 检查是否有旧意识形态（这是关键的检测条件！）
            has_old_ideologies = any(ideology_dist.get(old_id, 0) > 0 for old_id in [1, 2, 4, 5, 7])
            
            print(f"  意识形态分布: {ideology_dist}")
            print(f"  有旧意识形态: {has_old_ideologies}")
            
            if has_old_ideologies:
                ideology_change_count += 1
        else:
            print(f"  意识形态数据格式错误")
    else:
        print(f"  无意识形态数据")

print(f"\n应该修改的意识形态块数量: {ideology_change_count}")
