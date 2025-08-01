#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查人口数据的完整性
"""

def main():
    files_to_check = [
        'China2281_01_01.v2',
        'China2281_01_01_safe_backup_20250728_215815.v2',
        'China2281_01_01_unified_backup_20250728_220040.v2'
    ]

    print("=== 多文件人口数据检查 ===")
    for filename in files_to_check:
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            size_count = content.count('size=')
            mahayana_count = content.count('religion=mahayana') 
            farmers_count = content.count('farmers=')
            
            print(f"\n{filename}:")
            print(f"  大小: {len(content):,} 字符")
            print(f"  size= 数量: {size_count:,}")
            print(f"  farmers= 数量: {farmers_count}")
            print(f"  mahayana 数量: {mahayana_count}")
            
            # 检查第一个农民组的内容
            import re
            farmer_match = re.search(r'farmers=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', content, re.DOTALL)
            if farmer_match:
                farmer_block = farmer_match.group(1)
                has_size = 'size=' in farmer_block
                has_religion = 'religion=' in farmer_block
                print(f"  第一个农民组: size={has_size}, religion={has_religion}")
                if has_size and has_religion:
                    print(f"  农民组内容片段: {farmer_block[:200]}...")
            else:
                print("  未找到农民组")
                
            # 检查省份1的详细信息
            province_match = re.search(r'^1=\s*\{(.{0,3000})', content, re.MULTILINE | re.DOTALL)
            if province_match:
                province_content = province_match.group(1)
                province_farmers = province_content.count('farmers=')
                province_size = province_content.count('size=')
                print(f"  省份1: farmers={province_farmers}, size={province_size}")
                
                # 如果有农民但没有size，说明人口数据被清空了
                if province_farmers > 0 and province_size == 0:
                    print("  ❌ 省份1的农民组没有size数据，人口被清空!")
                elif province_farmers > 0 and province_size > 0:
                    print("  ✅ 省份1的人口数据正常")
                    
        except Exception as e:
            print(f"{filename}: 读取失败 - {e}")

if __name__ == "__main__":
    main()
