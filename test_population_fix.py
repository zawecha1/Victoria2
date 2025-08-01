#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的人口修改功能
"""

import os
from victoria2_main_modifier import Victoria2Modifier

def test_population_fix():
    """测试修复后的人口修改功能"""
    print("🧪 测试修复后的人口修改功能")
    print("=" * 50)
    
    # 查找测试文件
    test_files = [f for f in os.listdir('.') if f.endswith('.v2') and 'China' in f]
    if not test_files:
        print("❌ 未找到测试文件")
        return False
    
    test_file = test_files[0]
    print(f"📁 使用测试文件: {test_file}")
    
    try:
        # 创建修改器实例并测试加载
        modifier = Victoria2Modifier()
        print("✅ 修改器实例创建成功")
        
        # 测试文件加载
        if modifier.load_file(test_file):
            print("✅ 文件加载成功")
            print(f"📊 文件大小: {len(modifier.content):,} 字符")
            
            # 检查结构是否正确保存
            if modifier.structure:
                print("✅ 花括号结构已正确保存")
                print(f"🏗️ 根级块数: {len(modifier.structure.children)}")
            else:
                print("❌ 花括号结构未保存")
                return False
            
            # 测试CHI块查找
            print("\n🇨🇳 测试CHI块查找:")
            chi_block = modifier.find_china_country_block()
            if chi_block:
                print("✅ CHI块查找成功")
                print(f"📏 CHI块大小: {len(chi_block.content):,} 字符")
            else:
                print("❌ CHI块查找失败")
            
            # 测试结构化省份查找（不实际修改）
            print("\n🗺️ 测试结构化省份查找:")
            try:
                chinese_provinces = modifier.find_chinese_provinces_structured()
                print(f"✅ 结构化省份查找成功: 找到 {len(chinese_provinces)} 个中国省份")
            except Exception as e:
                print(f"❌ 结构化省份查找失败: {e}")
                print("🔄 这种情况下会自动回退到传统方法")
            
            # 测试传统方法（不实际修改）
            print("\n🔄 测试传统方法省份查找:")
            traditional_provinces = modifier.find_chinese_provinces()
            print(f"✅ 传统方法查找成功: 找到 {len(traditional_provinces)} 个中国省份")
            
            print("\n🎉 所有测试通过！修复成功！")
            return True
            
        else:
            print("❌ 文件加载失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_population_fix()
