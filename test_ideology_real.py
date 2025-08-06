#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试意识形态修改的简单脚本
"""

import re
from victoria2_main_modifier import Victoria2Modifier

def test_ideology_modification_on_real_file():
    """在真实文件上测试意识形态修改"""
    
    print("开始测试选项4：中国人口属性修改（仅前2个省份）")
    print("=" * 60)
    
    # 创建修改器实例，启用调试模式
    modifier = Victoria2Modifier(debug_mode=True)
    
    # 加载文件
    filename = 'China1837_01_24.v2'
    print(f"🔄 加载文件: {filename}")
    
    if not modifier.load_file(filename):
        print("❌ 文件加载失败")
        return False
    
    print("✅ 文件加载成功")
    
    # 创建备份
    backup_filename = modifier.create_backup(filename, "ideology_test")
    print(f"📁 备份文件: {backup_filename}")
    
    # 查找中国省份
    chinese_provinces = modifier.find_chinese_provinces()
    print(f"🏛️ 找到 {len(chinese_provinces)} 个中国省份")
    
    if len(chinese_provinces) == 0:
        print("❌ 未找到中国省份")
        return False
    
    # 只处理前2个省份进行测试
    test_provinces = chinese_provinces[:2]
    print(f"🎯 测试省份: {test_provinces}")
    
    print("\n开始执行意识形态修改...")
    
    # 重置计数器
    modifier.religion_changes = 0
    modifier.ideology_changes = 0
    modifier.population_count = 0
    
    # 执行修改（只修改前2个省份）
    result = modifier.modify_chinese_population(max_provinces=2)
    
    if result:
        print("\n✅ 修改完成！")
        print(f"📊 统计结果:")
        print(f"  宗教修改: {modifier.religion_changes} 处")
        print(f"  意识形态修改: {modifier.ideology_changes} 处")
        print(f"  总人口组: {modifier.population_count} 个")
        
        # 保存文件
        test_filename = filename.replace('.v2', '_ideology_test.v2')
        if modifier.save_file(test_filename):
            print(f"✅ 测试文件已保存: {test_filename}")
            
            # 验证修改
            print("\n🔍 验证修改结果...")
            if modifier.verify_ideology_modifications(test_filename):
                print("🎉 意识形态修改验证成功！")
                return True
            else:
                print("⚠️ 意识形态修改验证失败")
                return False
        else:
            print("❌ 测试文件保存失败")
            return False
    else:
        print("❌ 修改失败")
        return False

if __name__ == "__main__":
    success = test_ideology_modification_on_real_file()
    if success:
        print("\n🎉 测试成功完成！")
    else:
        print("\n❌ 测试失败！")
