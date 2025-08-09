#!/usr/bin/env python3
"""
测试菜单显示
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from victoria2_main_modifier import show_modification_menu

def test_menu():
    """测试菜单显示"""
    print("🧪 测试菜单显示")
    print("="*50)
    
    show_modification_menu()
    
    print("\n✅ 菜单显示测试完成")

if __name__ == "__main__":
    test_menu()
