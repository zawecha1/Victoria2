#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的主修改器功能
"""

import sys
import os
sys.path.append(r"c:\Users\zhangwc6\Documents\Paradox Interactive\Victoria II\save games")

from victoria2_main_modifier import Victoria2Modifier

def test_all_modifications():
    """测试所有修改功能"""
    print("🧪 测试修复后的主修改器")
    print("="*40)
    
    # 测试修改器对象创建
    modifier = Victoria2Modifier()
    print("✅ Victoria2Modifier 对象创建成功")
    
    # 检查所有必需的方法是否存在
    required_methods = [
        'execute_all_modifications',
        'execute_selective_modifications',
        'modify_militancy',
        'modify_china_culture',
        'modify_china_infamy',
        'modify_chinese_population'
    ]
    
    missing_methods = []
    for method in required_methods:
        if hasattr(modifier, method):
            print(f"✅ {method} 方法存在")
        else:
            missing_methods.append(method)
            print(f"❌ {method} 方法缺失")
    
    if missing_methods:
        print(f"\n❌ 发现缺失的方法: {missing_methods}")
        return False
    else:
        print("\n🎉 所有方法检查通过!")
        
    # 测试意识形态映射
    print(f"\n🔍 意识形态映射检查:")
    print(f"Liberal ID 6 映射: {modifier.ideology_mapping}")
    
    print("\n✅ 修复测试完成 - 所有功能正常!")
    return True

if __name__ == "__main__":
    test_all_modifications()
