#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试执行模式的安全验证脚本
"""

import subprocess
import sys
import os

def test_execution_mode():
    """测试执行模式但不实际确认"""
    print("测试执行模式...")
    
    # 使用 'n' 作为输入来取消执行
    process = subprocess.Popen(
        [sys.executable, 'final_safe_redistributor.py', 'execute'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 发送 'n' 来取消执行
    stdout, stderr = process.communicate(input='n\n')
    
    print("STDOUT:")
    print(stdout)
    if stderr:
        print("STDERR:")
        print(stderr)
    
    return process.returncode

if __name__ == "__main__":
    test_execution_mode()
