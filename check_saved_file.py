# 验证保存的修改文件
import re

print("验证保存的修改文件...")

try:
    with open('China1841_12_17_ideology_fixed.v2', 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    print(f"文件大小: {len(content):,} 字符")
    
    # 查找意识形态块
    ideology_matches = list(re.finditer(r'ideology=\s*\{([^}]*)\}', content, re.DOTALL))
    print(f"总共找到 {len(ideology_matches)} 个意识形态块")
    
    if len(ideology_matches) > 0:
        converted = 0
        for i, match in enumerate(ideology_matches[:20]):
            ideology_content = match.group(1).strip()
            ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
            ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
            old_ideologies = {id: val for id, val in ideology_dist.items() if id in [1, 2, 4, 5, 7] and val > 0}
            
            if not old_ideologies:
                converted += 1
                if converted <= 3:
                    conservative = ideology_dist.get(3, 0)
                    liberal = ideology_dist.get(6, 0)
                    print(f"✅ 已转换 #{i+1}: Conservative(3)={conservative:.2f}%, Liberal(6)={liberal:.2f}%")
            else:
                if len(ideology_matches[:20]) - converted <= 3:
                    print(f"❌ 未转换 #{i+1}: 仍有旧意识形态 {old_ideologies}")
        
        print(f"\n前20个中已转换: {converted}/20")
        print(f"转换率: {converted/20*100:.1f}%")
    else:
        print("❌ 没有找到意识形态块")
        
except FileNotFoundError:
    print("❌ 修改后的文件不存在")
except Exception as e:
    print(f"❌ 读取文件时出错: {e}")
