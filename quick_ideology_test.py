#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试意识形态修改修复效果
"""

import sys
import os
import shutil
from datetime import datetime
from victoria2_main_modifier import Victoria2Modifier

def quick_test():
    """快速测试意识形态修改"""
    
    print("🧪 快速测试意识形态修改修复效果")
    print("=" * 50)
    
    filename = 'China1837_01_24.v2'
    
    # 创建测试副本
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_filename = f'test_ideology_fix_{timestamp}.v2'
    shutil.copy2(filename, test_filename)
    print(f"📁 创建测试文件: {test_filename}")
    
    # 启用调试模式的修改器
    modifier = Victoria2Modifier(debug_mode=True)
    
    if not modifier.load_file(test_filename):
        print("❌ 文件加载失败")
        return False
    
    print("✅ 文件加载成功")
    print(f"📊 文件大小: {len(modifier.content):,} 字符")
    
    # 只测试前2个中国省份
    print("\n🎯 开始修改（限制前2个省份测试）...")
    result = modifier.modify_chinese_population(max_provinces=2)
    
    if not result:
        print("❌ 修改失败")
        return False
    
    print(f"\n📈 修改统计:")
    print(f"  宗教修改: {modifier.religion_changes} 处")
    print(f"  意识形态修改: {modifier.ideology_changes} 处")
    print(f"  人口组总数: {modifier.population_count} 个")
    
    # 保存文件
    if not modifier.save_file(test_filename):
        print("❌ 文件保存失败")
        return False
    
    print("✅ 文件保存成功")
    
    # 验证修改结果
    print("\n🔍 验证修改结果...")
    if modifier.verify_ideology_modifications(test_filename):
        print("🎉 意识形态修改验证成功！")
        return True
    else:
        print("❌ 意识形态修改验证失败")
        return False

if __name__ == "__main__":
    success = quick_test()
    
    if success:
        print("\n🎉 测试成功！意识形态修改问题已修复！")
    else:
        print("\n❌ 测试失败，需要进一步调试。")
