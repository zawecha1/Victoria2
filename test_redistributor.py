#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试最终重分配工具的各种功能
"""

import subprocess
import sys

def test_preview_mode():
    """测试预览模式"""
    print("测试预览模式...")
    try:
        # 模拟选择预览模式 (选项1)
        process = subprocess.Popen(
            [sys.executable, 'final_safe_redistributor.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input='1\n', timeout=30)
        
        if '首都保护重分配方案' in stdout:
            print("✅ 预览模式测试通过")
            return True
        else:
            print("❌ 预览模式测试失败")
            print("STDOUT:", stdout[-500:])  # 显示最后500字符
            return False
            
    except Exception as e:
        print(f"❌ 预览模式测试出错: {e}")
        return False

def test_menu_display():
    """测试菜单显示"""
    print("测试菜单显示...")
    try:
        process = subprocess.Popen(
            [sys.executable, 'final_safe_redistributor.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 给程序一点时间显示菜单，然后发送退出命令
        stdout, stderr = process.communicate(input='3\n', timeout=10)
        
        if 'Victoria II 首都保护省份重分配工具' in stdout:
            print("✅ 菜单显示测试通过")
            return True
        else:
            print("❌ 菜单显示测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 菜单显示测试出错: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试最终重分配工具")
    print("=" * 40)
    
    tests = [
        test_menu_display,
        test_preview_mode
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过! 工具可以安全使用。")
    else:
        print("⚠️ 部分测试失败，请检查代码。")

if __name__ == "__main__":
    main()
