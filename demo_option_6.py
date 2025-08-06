#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('.')

from victoria2_main_modifier import Victoria2Modifier, perform_selective_modification, show_modification_menu

def run_option_6_demo():
    """演示如何使用选项6 - 中国人口金钱修改"""
    
    print("🎮 维多利亚2修改器 - 选项6演示")
    print("="*60)
    
    # 显示菜单
    show_modification_menu()
    
    # 模拟用户选择选项6
    print("\n🎯 选择选项6: 中国人口金钱修改 (设为9,999,999)")
    
    # 设置修改选项 - 只选择金钱修改
    options = {
        'militancy': False,
        'culture': False,
        'infamy': False,
        'population': False,
        'date': False,
        'money': True,  # 选择金钱修改
    }
    
    # 使用默认存档文件
    filename = 'China1836_02_20.v2'
    
    print(f"📁 使用存档文件: {filename}")
    print("💰 开始执行中国人口金钱修改...")
    
    # 执行选择性修改
    try:
        success = perform_selective_modification(filename, options)
        if success:
            print("\n🎉 选项6执行成功!")
            print("✅ 中国人口的money和bank字段已设置为9,999,999")
        else:
            print("❌ 修改失败")
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {e}")
    
    print("\n📋 选项6功能说明:")
    print("- 修改所有中国省份中的人口金钱")
    print("- 同时修改 money 和 bank 字段")
    print("- 目标金额: 9,999,999")
    print("- 自动备份原始文件")

if __name__ == "__main__":
    run_option_6_demo()
