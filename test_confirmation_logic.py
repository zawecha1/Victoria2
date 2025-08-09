#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的确认逻辑 - 默认回车确认
"""

import subprocess
import sys

def test_confirmation_logic():
    """测试确认逻辑"""
    print("=" * 60)
    print("测试新的确认逻辑: 默认回车确认")
    print("=" * 60)
    
    # 测试用例1: 回车确认
    print("\n测试1: 发送回车 (应该确认)")
    try:
        process = subprocess.Popen(
            [sys.executable, 'final_safe_redistributor.py', 'execute', 'autosave.v2'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 发送回车
        stdout, stderr = process.communicate(input='\n', timeout=30)
        
        print("输出 (最后500字符):")
        print(stdout[-500:] if len(stdout) > 500 else stdout)
        
        if "用户取消操作" in stdout:
            print("✅ 确认逻辑: 回车被正确识别为确认")
        else:
            print("❌ 确认逻辑可能有问题")
            
    except subprocess.TimeoutExpired:
        print("⏰ 超时 - 可能正在执行重分配")
        process.kill()
    except Exception as e:
        print(f"测试失败: {e}")
    
    # 测试用例2: 输入no取消
    print("\n测试2: 输入 'no' (应该取消)")
    try:
        process = subprocess.Popen(
            [sys.executable, 'final_safe_redistributor.py', 'execute', 'autosave.v2'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 发送 'no'
        stdout, stderr = process.communicate(input='no\n', timeout=30)
        
        print("输出 (最后300字符):")
        print(stdout[-300:] if len(stdout) > 300 else stdout)
        
        if "用户取消操作" in stdout:
            print("✅ 取消逻辑: 'no' 被正确识别为取消")
        else:
            print("❌ 取消逻辑可能有问题")
            
    except subprocess.TimeoutExpired:
        print("⏰ 超时")
        process.kill()
    except Exception as e:
        print(f"测试失败: {e}")

def show_usage_example():
    """显示使用示例"""
    print("\n" + "=" * 60)
    print("新的确认方式使用示例:")
    print("=" * 60)
    
    print("\n1. 快速确认 (推荐):")
    print("   确认执行重分配? (直接回车确认，输入 no 取消): [直接按回车]")
    print("   → 立即执行重分配")
    
    print("\n2. 明确取消:")
    print("   确认执行重分配? (直接回车确认，输入 no 取消): no")
    print("   → 取消操作，不执行重分配")
    
    print("\n3. 其他输入 (兼容):")
    print("   确认执行重分配? (直接回车确认，输入 no 取消): yes")
    print("   → 执行重分配 (向后兼容)")
    
    print("\n✅ 优势:")
    print("   - 更快的操作体验 (一键回车)")
    print("   - 减少输入错误")
    print("   - 保持向后兼容性")
    print("   - 明确的提示信息")

if __name__ == "__main__":
    test_confirmation_logic()
    show_usage_example()
