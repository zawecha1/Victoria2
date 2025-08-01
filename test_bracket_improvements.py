#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试花括号结构改进后的Victoria2Modifier功能
"""

import os
import sys
from victoria2_main_modifier import Victoria2Modifier

def test_bracket_structure_improvements():
    """测试花括号结构改进"""
    print("🧪 花括号结构改进测试")
    print("=" * 50)
    
    # 查找测试文件
    test_files = [f for f in os.listdir('.') if f.endswith('.v2') and 'China' in f]
    if not test_files:
        print("❌ 未找到测试文件")
        return False
    
    test_file = test_files[0]
    print(f"📁 使用测试文件: {test_file}")
    
    try:
        # 创建修改器实例
        modifier = Victoria2Modifier(test_file)
        print(f"✅ 文件加载成功")
        print(f"📊 文件大小: {len(modifier.content):,} 字符")
        
        # 测试花括号结构解析
        if modifier.structure:
            print(f"✅ 花括号结构解析成功")
            print(f"🏗️ 根级块数量: {len(modifier.structure.children)}")
            print(f"📏 结构总大小: {modifier.structure.end_pos - modifier.structure.start_pos:,} 字符")
            
            # 分析主要块类型
            block_types = {}
            for block in modifier.structure.children:
                block_type = block.content_type
                block_types[block_type] = block_types.get(block_type, 0) + 1
            
            print("\n📋 块类型统计:")
            for block_type, count in sorted(block_types.items()):
                print(f"  • {block_type}: {count} 个")
        else:
            print("❌ 花括号结构解析失败")
            return False
        
        # 测试CHI国家块查找
        print("\n🇨🇳 测试CHI国家块查找:")
        chi_block = modifier.find_china_country_block()
        if chi_block:
            print(f"✅ CHI块找到成功")
            print(f"📍 位置: {chi_block.start_pos:,}-{chi_block.end_pos:,}")
            print(f"📏 大小: {len(chi_block.content):,} 字符")
            print(f"🏗️ 子块数量: {len(chi_block.children)}")
            
            # 分析CHI块内容
            if "primary_culture" in chi_block.content:
                print("✅ 包含主文化字段")
            if "badboy" in chi_block.content:
                print("✅ 包含恶名度字段")
            if "culture=" in chi_block.content:
                print("✅ 包含接受文化字段")
        else:
            print("❌ CHI块未找到")
            return False
        
        # 测试中国省份查找（结构化方法）
        print("\n🗺️ 测试中国省份查找 (结构化方法):")
        chinese_provinces = modifier.find_chinese_provinces_structured()
        print(f"✅ 找到 {len(chinese_provinces)} 个中国省份")
        if chinese_provinces:
            sample_province = chinese_provinces[0]
            print(f"📍 示例省份位置: {sample_province.start_pos:,}-{sample_province.end_pos:,}")
            print(f"📏 示例省份大小: {len(sample_province.content):,} 字符")
        
        # 测试安全修改功能
        print("\n🔧 测试安全修改功能:")
        print("（此测试不会实际修改文件，只验证结构分析）")
        
        # 测试文化块查找
        culture_block = modifier.find_nested_block_safely(chi_block, "culture")
        if culture_block:
            print(f"✅ 文化块找到: {len(culture_block.content)} 字符")
        else:
            print("ℹ️ 文化块未找到或格式不同")
        
        print("\n🎉 所有测试完成！花括号结构改进功能正常")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_bracket_structure_improvements()
