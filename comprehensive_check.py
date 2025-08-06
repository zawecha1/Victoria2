# 全面检查修改效果
import re

print("全面检查修改效果...")

with open('China1841_12_17_ideology_fixed.v2', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# 查找意识形态块
ideology_matches = list(re.finditer(r'ideology=\s*\{([^}]*)\}', content, re.DOTALL))
print(f"总共找到 {len(ideology_matches)} 个意识形态块")

converted = 0
not_converted = 0

# 检查所有意识形态块
for i, match in enumerate(ideology_matches):
    ideology_content = match.group(1).strip()
    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
    ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
    
    # 检查是否有旧意识形态
    old_ideologies = {id: val for id, val in ideology_dist.items() if id in [1, 2, 4, 5, 7] and val > 0}
    
    if not old_ideologies:
        converted += 1
        if converted <= 5:  # 显示前5个已转换的
            conservative = ideology_dist.get(3, 0)
            liberal = ideology_dist.get(6, 0)
            print(f"✅ 已转换 #{i+1}: Conservative(3)={conservative:.2f}%, Liberal(6)={liberal:.2f}%")
    else:
        not_converted += 1

print(f"\n全面统计:")
print(f"✅ 已转换: {converted}")
print(f"❌ 未转换: {not_converted}")
print(f"总计: {converted + not_converted}")
print(f"转换率: {converted/(converted+not_converted)*100:.1f}%")

# 检查是否有宗教修改
mahayana_count = len(re.findall(r'=mahayana', content))
print(f"\n宗教修改统计:")
print(f"mahayana出现次数: {mahayana_count}")

# 查找前几个修改的迹象
print(f"\n查找修改的迹象...")
sample_conversions = re.findall(r'ideology=\s*\{\s*1=0\.00000\s*2=0\.00000\s*3=[\d.]+\s*4=0\.00000\s*5=0\.00000\s*6=[\d.]+\s*7=0\.00000\s*\}', content, re.DOTALL)
print(f"完全转换的意识形态块数量: {len(sample_conversions)}")

if len(sample_conversions) > 0:
    print("✅ 找到完全转换的意识形态块!")
    print(f"示例: {sample_conversions[0][:100]}...")
else:
    print("❌ 没有找到完全转换的意识形态块")
