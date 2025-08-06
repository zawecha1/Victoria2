#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import sys

# 强制重新加载模块
if 'victoria2_main_modifier' in sys.modules:
    importlib.reload(sys.modules['victoria2_main_modifier'])

from victoria2_main_modifier import Victoria2Modifier

def test_real_ideology_modification():
    """在真实存档文件上测试意识形态修改"""
    
    print("🎮 测试真实存档的意识形态修改")
    print("="*60)
    
    # 创建修改器实例
    modifier = Victoria2Modifier()
    modifier.debug_mode = True
    
    # 加载存档文件
    filename = 'China1836_02_20.v2'
    print(f"📁 加载存档文件: {filename}")
    modifier.load_file(filename)
    
    # 执行意识形态修改 (选项4)
    print("\n🎭 开始执行中国人口意识形态修改...")
    result = modifier.modify_chinese_population(max_provinces=10)  # 只处理前10个省份进行测试
    
    if result:
        print(f"\n✅ 意识形态修改成功!")
        print(f"📊 修改统计:")
        print(f"   - 意识形态修改: {modifier.ideology_changes} 个")
        
        # 保存测试文件
        output_filename = 'China1836_02_20_ideology_test.v2'
        modifier.save_file(output_filename)
        print(f"💾 已保存测试文件: {output_filename}")
        
        # 运行验证
        print(f"\n🔍 验证意识形态修改结果...")
        modifier.verify_ideology_modifications(output_filename)
        
    else:
        print("ℹ️ 未进行任何修改 (可能意识形态已经是目标状态)")
    
    print("\n🎉 测试完成!")

if __name__ == "__main__":
    test_real_ideology_modification()
