#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 主修改器演示脚本
展示新功能：默认路径和选择性修改
"""

import sys
import os
sys.path.append(r"c:\Users\zhangwc6\Documents\Paradox Interactive\Victoria II\save games")

from victoria2_main_modifier import Victoria2Modifier, get_save_files_list, show_modification_menu

def demo_new_features():
    """演示新功能"""
    print("Victoria II 主修改器 v2.1 - 新功能演示")
    print("="*50)
    
    # 1. 演示默认路径功能
    print("\n1. 📁 默认路径功能:")
    save_files = get_save_files_list()
    if save_files:
        print(f"   找到 {len(save_files)} 个存档文件")
        print(f"   最新的5个文件:")
        for i, file in enumerate(save_files[:5], 1):
            print(f"   {i}. {file}")
    else:
        print("   未找到存档文件")
    
    # 2. 演示修改选项菜单
    print("\n2. 🎮 选择性修改菜单:")
    show_modification_menu()
    
    # 3. 演示修改器功能
    print("\n3. ⚙️ 修改器功能说明:")
    print("   ✓ 支持命令行模式：python victoria2_main_modifier.py <文件名>")
    print("   ✓ 支持交互式模式：python victoria2_main_modifier.py")
    print("   ✓ 自动文件列表：显示最近的存档文件")
    print("   ✓ 选择性修改：可以只修改特定项目")
    print("   ✓ 全部修改：一键执行所有修改")
    
    # 4. 使用示例
    print("\n4. 📖 使用示例:")
    print("   # 命令行模式（全部修改）")
    print("   python victoria2_main_modifier.py China1885_03_04.v2")
    print("")
    print("   # 交互式模式")
    print("   python victoria2_main_modifier.py")
    print("   -> 选择文件编号: 1")
    print("   -> 选择修改项目: 4 (只修改人口属性)")
    print("   -> 或选择: 5 (全部修改)")
    print("   -> 或选择: 1,3,4 (多选：斗争性+恶名度+人口)")
    
    print("\n✅ 新功能集成完成！")
    print("🎯 现在支持更灵活的使用方式")

if __name__ == "__main__":
    demo_new_features()
