#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试花括号结构改进
"""

import sys
sys.path.append('.')

def simple_test():
    try:
        print("🧪 开始简单测试...")
        
        # 测试导入
        from victoria2_main_modifier import Victoria2Modifier
        print("✅ 模块导入成功")
        
        # 测试创建实例
        modifier = Victoria2Modifier()
        print("✅ 创建实例成功")
        
        # 测试花括号解析器
        from bracket_parser import Victoria2BracketParser
        parser = Victoria2BracketParser()
        print("✅ 花括号解析器创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    simple_test()
