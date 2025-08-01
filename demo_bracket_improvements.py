#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
花括号结构改进功能完整测试和演示
展示根据游戏存档花括号对称特性改进后的修改功能
"""

import os
import sys
from victoria2_main_modifier import Victoria2Modifier

def demo_bracket_aware_improvements():
    """演示花括号结构感知的改进功能"""
    print("🎯 Victoria II 花括号结构改进功能演示")
    print("="*60)
    print("✨ 新特性：基于花括号对称结构的安全修改")
    print("🔍 智能识别：CHI国家定义 vs 外交关系块")
    print("🛡️ 结构保护：确保花括号完美对称")
    print("🎯 精准修改：只修改目标数据，保护其他内容")
    print("="*60)
    
    # 查找测试文件
    test_files = [f for f in os.listdir('.') if f.endswith('.v2') and 'China' in f][:3]
    if not test_files:
        print("❌ 未找到测试文件")
        return False
    
    print(f"📁 可用测试文件: {len(test_files)} 个")
    for i, f in enumerate(test_files, 1):
        print(f"  {i}. {f}")
    
    print(f"\n🧪 使用第一个文件进行演示: {test_files[0]}")
    
    try:
        # 创建修改器实例 - 使用新的初始化方式
        modifier = Victoria2Modifier(test_files[0])
        print(f"✅ 文件加载成功: {len(modifier.content):,} 字符")
        
        # 演示1: 花括号结构解析
        print(f"\n📊 花括号结构分析:")
        if modifier.structure:
            print(f"  ✅ 结构解析成功")
            print(f"  📏 总大小: {modifier.structure.end_pos - modifier.structure.start_pos:,} 字符")
            print(f"  🏗️ 根级块数: {len(modifier.structure.children)}")
            
            # 统计块类型
            block_types = {}
            for block in modifier.structure.children:
                block_type = block.content_type
                block_types[block_type] = block_types.get(block_type, 0) + 1
            
            print(f"  📋 块类型分布:")
            for block_type in sorted(block_types.keys()):
                count = block_types[block_type]
                print(f"    • {block_type}: {count} 个")
        
        # 演示2: 智能CHI块识别
        print(f"\n🇨🇳 智能CHI块识别演示:")
        chi_block = modifier.find_china_country_block()
        if chi_block:
            print(f"  ✅ 成功识别真正的CHI国家定义块")
            print(f"  📍 位置: {chi_block.start_pos:,} - {chi_block.end_pos:,}")
            print(f"  📏 大小: {len(chi_block.content):,} 字符")
            print(f"  🏗️ 子块数: {len(chi_block.children)}")
            
            # 检查包含的国家字段
            country_fields = ['primary_culture', 'badboy', 'capital', 'government', 'technology']
            found_fields = [field for field in country_fields if field in chi_block.content]
            print(f"  ✅ 包含国家字段: {', '.join(found_fields)}")
            
            # 查找文化配置
            culture_block = modifier.find_nested_block_safely(chi_block, "culture")
            if culture_block:
                print(f"  ✅ 找到culture子块: {len(culture_block.content)} 字符")
            else:
                print(f"  ℹ️ 未找到独立的culture子块")
        else:
            print(f"  ❌ 未能识别CHI块")
        
        # 演示3: 结构化省份查找
        print(f"\n🗺️ 结构化省份查找演示:")
        chinese_provinces = modifier.find_chinese_provinces_structured()
        if chinese_provinces:
            print(f"  ✅ 找到 {len(chinese_provinces)} 个中国省份")
            if len(chinese_provinces) > 0:
                sample = chinese_provinces[0]
                print(f"  📍 示例省份: 位置 {sample.start_pos:,} - {sample.end_pos:,}")
                print(f"  📏 示例大小: {len(sample.content):,} 字符")
        else:
            print(f"  ❌ 未找到中国省份")
        
        print(f"\n🎉 花括号结构改进功能演示完成!")
        print(f"✨ 所有新功能都基于Victoria II存档的花括号对称特性")
        print(f"🛡️ 确保修改安全性，避免破坏游戏存档结构")
        
        # 显示改进前后对比
        print(f"\n📈 改进效果对比:")
        print(f"  🔄 改进前: 使用正则表达式查找，可能误识别外交关系中的CHI")
        print(f"  ✅ 改进后: 基于花括号结构智能分析，精确识别国家定义块")
        print(f"  🔄 改进前: 逐行修改，可能破坏嵌套结构")
        print(f"  ✅ 改进后: 结构感知修改，保持花括号完美对称")
        print(f"  🔄 改进前: 简单字符串替换，风险较高")
        print(f"  ✅ 改进后: 智能块内修改，安全性大幅提升")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    demo_bracket_aware_improvements()
