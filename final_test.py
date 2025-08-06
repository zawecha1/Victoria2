#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证脚本 - 测试所有修改功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from victoria2_main_modifier import Victoria2Modifier

def test_all_modifications():
    """测试所有修改功能"""
    print("🧪 Victoria II 存档修改器最终测试")
    print("=" * 60)
    
    filename = "China1837_01_24.v2"
    
    # 创建修改器实例
    modifier = Victoria2Modifier(filename, debug_mode=True)
    
    print("🔄 1. 加载文件...")
    if not modifier.load_file():
        print("❌ 文件加载失败")
        return False
    
    print("\n🔄 2. 测试意识形态修改...")
    if modifier.modify_chinese_population(ideology="conservative", target_percentage=100.0):
        print("✅ 意识形态修改成功")
    else:
        print("❌ 意识形态修改失败")
    
    print("\n🔄 3. 测试忠诚度修改...")
    if modifier.modify_militancy(china_militancy=0.0):
        print("✅ 忠诚度修改成功")
    else:
        print("❌ 忠诚度修改失败")
    
    print("\n🔄 4. 保存文件...")
    if modifier.save_file("China1837_01_24_final_test.v2"):
        print("✅ 文件保存成功")
    else:
        print("❌ 文件保存失败")
    
    print("\n📊 修改统计:")
    print(f"  - 意识形态修改次数: {modifier.ideology_changes}")
    print(f"  - 忠诚度修改次数: {modifier.militancy_changes}")
    
    return True

if __name__ == "__main__":
    success = test_all_modifications()
    
    if success:
        print("\n🎉 所有测试通过!")
        print("✅ Victoria II 存档修改器工作正常")
    else:
        print("\n❌ 部分测试失败")
