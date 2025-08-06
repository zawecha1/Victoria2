#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试全局意识形态修改功能
"""

from victoria2_main_modifier import Victoria2Modifier

def test_global_ideology_fix():
    """测试全局意识形态修改"""
    print("🧪 测试全局意识形态修改功能")
    print("=" * 50)
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=False)  # 关闭调试模式避免输出过多
    
    # 加载文件
    filename = 'autosave.v2'
    if not modifier.load_file(filename):
        print("❌ 文件加载失败")
        return False
    
    print(f"✅ 文件加载成功")
    
    # 创建备份
    backup_file = modifier.create_backup(filename, "global_ideology")
    print(f"✅ 备份创建: {backup_file}")
    
    # 执行全局意识形态修改
    print("\n🔄 开始全局意识形态修改...")
    success = modifier.modify_chinese_population(max_provinces=100)  # 先测试100个省份
    
    if success:
        print(f"✅ 全局意识形态修改完成")
        print(f"📊 修改统计:")
        print(f"  意识形态修改: {modifier.ideology_changes} 处")
        print(f"  总人口修改: {modifier.population_count} 个人口组")
        
        # 保存修改后的文件
        test_filename = filename.replace('.v2', '_ideology_test.v2')
        if modifier.save_file(test_filename):
            print(f"✅ 测试文件保存: {test_filename}")
            
            # 验证修改效果
            print("\n🔍 验证修改效果...")
            verify_ideology_fix(test_filename)
        else:
            print("❌ 文件保存失败")
    else:
        print("❌ 全局意识形态修改失败")

def verify_ideology_fix(filename):
    """验证意识形态修改效果"""
    import re
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 验证文件读取失败: {e}")
        return
    
    # 查找所有意识形态块
    ideology_pattern = r'ideology=\s*\{([^}]*)\}'
    ideology_matches = list(re.finditer(ideology_pattern, content, re.DOTALL))
    
    print(f"📊 验证结果: 找到 {len(ideology_matches)} 个意识形态块")
    
    # 检查前100个块的转换情况
    old_ideologies = [1, 2, 4, 5, 7]
    converted_count = 0
    unconverted_count = 0
    
    for i, match in enumerate(ideology_matches[:1000]):  # 只检查前1000个
        ideology_content = match.group(1)
        
        # 解析意识形态数据
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
        ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
        
        # 检查是否有旧意识形态
        has_old = any(ideology_dist.get(old_id, 0) > 0 for old_id in old_ideologies)
        
        if has_old:
            unconverted_count += 1
        else:
            converted_count += 1
    
    print(f"📋 前1000个意识形态块检查结果:")
    print(f"  已转换: {converted_count}")
    print(f"  未转换: {unconverted_count}")
    
    if unconverted_count == 0:
        print("✅ 验证通过：前1000个意识形态块都已正确转换!")
    else:
        print(f"⚠️ 发现 {unconverted_count} 个未转换的意识形态块")

if __name__ == "__main__":
    test_global_ideology_fix()
