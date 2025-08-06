#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整修改所有省份的意识形态
"""

from victoria2_main_modifier import Victoria2Modifier

def fix_all_ideology():
    """修改所有省份的意识形态"""
    print("🌍 开始完整的全局意识形态修改")
    print("=" * 50)
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=False)
    
    # 加载文件
    filename = 'autosave.v2'
    if not modifier.load_file(filename):
        print("❌ 文件加载失败")
        return False
    
    print(f"✅ 文件加载成功")
    
    # 创建备份
    backup_file = modifier.create_backup(filename, "complete_ideology")
    print(f"✅ 备份创建: {backup_file}")
    
    # 执行完整的全局意识形态修改（不限制省份数量）
    print("\n🔄 开始完整的全局意识形态修改...")
    success = modifier.modify_chinese_population()  # 处理所有省份
    
    if success:
        print(f"✅ 完整意识形态修改完成")
        print(f"📊 修改统计:")
        print(f"  意识形态修改: {modifier.ideology_changes} 处")
        print(f"  总人口修改: {modifier.population_count} 个人口组")
        
        # 保存修改后的文件
        fixed_filename = filename.replace('.v2', '_ideology_fixed.v2')
        if modifier.save_file(fixed_filename):
            print(f"✅ 修复文件保存: {fixed_filename}")
            
            # 快速验证修改效果
            print("\n🔍 快速验证修改效果...")
            quick_verify(fixed_filename)
        else:
            print("❌ 文件保存失败")
    else:
        print("❌ 完整意识形态修改失败")

def quick_verify(filename):
    """快速验证修改效果"""
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
    
    # 快速检查前500个块
    old_ideologies = [1, 2, 4, 5, 7]
    sample_size = min(500, len(ideology_matches))
    unconverted_count = 0
    
    for i, match in enumerate(ideology_matches[:sample_size]):
        ideology_content = match.group(1)
        
        # 解析意识形态数据
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
        ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
        
        # 检查是否有旧意识形态
        has_old = any(ideology_dist.get(old_id, 0) > 0 for old_id in old_ideologies)
        
        if has_old:
            unconverted_count += 1
    
    print(f"📋 前{sample_size}个意识形态块快速检查:")
    print(f"  已转换: {sample_size - unconverted_count}")
    print(f"  未转换: {unconverted_count}")
    
    if unconverted_count == 0:
        print("✅ 快速验证通过：采样检查显示意识形态都已正确转换!")
    else:
        print(f"⚠️ 快速验证：采样中发现 {unconverted_count} 个未转换的意识形态块")
        print("建议：如果需要更完整的修改，请运行全局检查程序")

if __name__ == "__main__":
    fix_all_ideology()
