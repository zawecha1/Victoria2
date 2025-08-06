# 验证修改效果
import re

print("验证修改效果...")

# 读取修改后的内容
with open('China1841_12_17.v2', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# 查找意识形态块
ideology_matches = list(re.finditer(r'ideology=\s*\{([^}]*)\}', content, re.DOTALL))
print(f"总共找到 {len(ideology_matches)} 个意识形态块")

# 分析前10个意识形态块
converted_count = 0
not_converted_count = 0

for i, match in enumerate(ideology_matches[:20]):  # 检查前20个
    ideology_content = match.group(1).strip()
    
    # 解析意识形态数据
    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
    ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
    
    # 检查是否有旧意识形态
    old_ideologies = {id: val for id, val in ideology_dist.items() if id in [1, 2, 4, 5, 7] and val > 0}
    
    if old_ideologies:
        not_converted_count += 1
        if not_converted_count <= 3:  # 只显示前3个未转换的
            print(f"\n❌ 未转换 #{i+1}: 仍有旧意识形态 {old_ideologies}")
    else:
        converted_count += 1
        if converted_count <= 3:  # 只显示前3个已转换的
            conservative = ideology_dist.get(3, 0)
            liberal = ideology_dist.get(6, 0)
            print(f"\n✅ 已转换 #{i+1}: Conservative(3)={conservative:.2f}%, Liberal(6)={liberal:.2f}%")

print(f"\n总结 (前20个意识形态块):")
print(f"✅ 已转换: {converted_count}")
print(f"❌ 未转换: {not_converted_count}")
print(f"转换率: {converted_count/(converted_count+not_converted_count)*100:.1f}%")
