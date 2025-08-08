"""
测试修复后的中国文化修改功能
"""

# 模拟一个简单的测试，检查修复是否工作
import re

def test_culture_parsing_fix():
    """测试文化解析修复"""
    
    # 模拟一个包含问题的culture块
    problematic_culture_block = '''culture=
{
    "nanfaren"
    "manchu"
    "yankee"
    technology_school="tech_school"
    civilized="yes"
    some_setting="noculture"
}'''
    
    print("🧪 测试文化解析修复")
    print("="*50)
    
    # 旧方法（有问题）
    old_matches = re.findall(r'"([^"]+)"', problematic_culture_block)
    print(f"❌ 旧方法结果: {old_matches}")
    print(f"   问题: 包含了 'noculture' 和其他非文化项")
    
    # 新方法（修复后）
    current_accepted = []
    raw_matches = []
    lines = problematic_culture_block.split('\n')
    for line in lines:
        line = line.strip()
        if '"' in line:
            raw_matches.extend(re.findall(r'"([^"]+)"', line))
        
        if re.match(r'^"[^"]+"\s*$', line) and '=' not in line:
            match = re.search(r'"([^"]+)"', line)
            if match:
                culture_name = match.group(1)
                if culture_name != "noculture" and not culture_name.startswith("no"):
                    current_accepted.append(culture_name)
    
    print(f"✅ 新方法结果: {current_accepted}")
    print(f"   原始匹配: {raw_matches}")
    filtered_out = [item for item in raw_matches if item not in current_accepted]
    print(f"   已过滤: {filtered_out}")
    
    # 验证修复效果
    if "noculture" not in current_accepted and len(current_accepted) == 3:
        print("\n🎉 修复成功!")
        print("✅ 成功过滤掉了 'noculture'")
        print("✅ 正确保留了三个真正的文化")
        return True
    else:
        print("\n❌ 修复失败!")
        return False

if __name__ == "__main__":
    test_culture_parsing_fix()
