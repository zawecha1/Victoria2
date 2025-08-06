#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查人口块识别问题
"""

import re
import sys
from victoria2_main_modifier import Victoria2Modifier

def check_population_detection():
    """检查人口块识别问题"""
    
    print("🔍 检查人口块识别问题")
    print("=" * 50)
    
    filename = 'China1837_01_24.v2'
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=True)
    
    # 加载文件
    if not modifier.load_file(filename):
        print("❌ 无法加载文件")
        return
    
    print("✅ 文件加载成功")
    
    # 查找中国省份
    chinese_provinces = modifier.find_chinese_provinces_structured()
    if not chinese_provinces:
        print("❌ 未找到中国省份")
        return
    
    print(f"✅ 找到 {len(chinese_provinces)} 个中国省份")
    
    # 分析第一个省份
    first_province = chinese_provinces[0]
    print(f"\n🎯 分析第一个省份:")
    print(f"子块数量: {len(first_province.children)}")
    print(f"省份内容长度: {len(first_province.content)}")
    
    # 人口类型列表
    pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                'bureaucrats', 'intellectuals']
    
    # 检查子块
    population_blocks = []
    for i, child_block in enumerate(first_province.children):
        print(f"\n子块 {i}:")
        print(f"  长度: {len(child_block.content)}")
        print(f"  开始: {child_block.start_pos}")
        print(f"  结束: {child_block.end_pos}")
        
        # 显示内容的前100个字符
        content_preview = child_block.content[:100] + "..." if len(child_block.content) > 100 else child_block.content
        print(f"  内容预览: {repr(content_preview)}")
        
        # 检查是否包含人口类型
        found_pop_types = [pop_type for pop_type in pop_types if pop_type in child_block.content]
        if found_pop_types:
            print(f"  ✅ 发现人口类型: {found_pop_types}")
            population_blocks.append(child_block)
        else:
            print(f"  ❌ 未发现人口类型")
    
    print(f"\n📊 总结:")
    print(f"找到 {len(population_blocks)} 个人口块")
    
    if not population_blocks:
        print("❌ 没有找到任何人口块")
        print("🔍 让我们用更宽松的方法搜索...")
        
        # 在完整的省份内容中搜索人口类型
        province_content = first_province.content
        for pop_type in pop_types:
            pattern = f'{pop_type}='
            if pattern in province_content:
                print(f"  ✅ 在省份内容中找到: {pattern}")
                
                # 找到具体位置
                pos = province_content.find(pattern)
                print(f"    位置: {pos}")
                
                # 显示周围的内容
                start = max(0, pos - 50)
                end = min(len(province_content), pos + 200)
                context = province_content[start:end]
                print(f"    上下文: {repr(context)}")
                break
    else:
        print("✅ 成功找到人口块")
        
        # 测试第一个人口块的修改
        first_pop = population_blocks[0]
        print(f"\n🧪 测试第一个人口块的修改:")
        
        original_content = first_pop.content
        modified_content = modifier._modify_single_population_structured(original_content)
        
        if modified_content != original_content:
            print("✅ 修改成功")
            print(f"  长度变化: {len(original_content)} → {len(modified_content)}")
        else:
            print("❌ 修改失败，内容未改变")

if __name__ == "__main__":
    check_population_detection()
