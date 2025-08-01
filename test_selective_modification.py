#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试选择性修改功能 - 只修改人口属性
"""

import sys
import os
sys.path.append(r"c:\Users\zhangwc6\Documents\Paradox Interactive\Victoria II\save games")

from victoria2_main_modifier import Victoria2Modifier

def test_selective_modification():
    """测试选择性修改"""
    print("测试选择性修改功能")
    print("="*40)
    
    # 选择只修改人口属性
    options = {
        'militancy': False,
        'culture': False,
        'infamy': False,
        'population': True  # 只选择人口属性修改
    }
    
    filename = "China1885_03_04.v2"
    
    print(f"目标文件: {filename}")
    print("选择的修改项目: 只修改中国人口属性")
    print("- 宗教 → mahayana")
    print("- 意识形态调整")
    
    # 创建修改器
    modifier = Victoria2Modifier()
    
    # 执行选择性修改
    print("\n开始执行选择性修改...")
    result = modifier.execute_selective_modifications(filename, options)
    
    if result:
        print("✅ 选择性修改测试成功!")
    else:
        print("❌ 选择性修改测试失败!")

if __name__ == "__main__":
    test_selective_modification()
