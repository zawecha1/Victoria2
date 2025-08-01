#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析中国文化宗教分布
"""

def main():
    with open('China2281_01_01.v2', 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # 检查各种中国文化的宗教情况
    chinese_cultures = ['beifaren', 'nanfaren', 'manchu', 'han', 'cantonese', 'min', 'hakka']

    print("=== 中国文化宗教统计 ===")
    total_mahayana = 0
    total_chinese_pop = 0
    
    for culture in chinese_cultures:
        # 查找该文化的所有宗教
        import re
        pattern = f'{culture}=([a-zA-Z_]+)'
        matches = re.findall(pattern, content)
        
        if matches:
            from collections import Counter
            religion_counts = Counter(matches)
            print(f"\n{culture} 文化:")
            for religion, count in religion_counts.most_common():
                print(f"  {religion}: {count}")
                if religion == 'mahayana':
                    total_mahayana += count
                total_chinese_pop += count
        else:
            print(f"\n{culture} 文化: 未找到")

    print(f"\n=== 总计 ===")
    print(f"中国文化人口组总数: {total_chinese_pop}")
    print(f"已转换为mahayana: {total_mahayana}")
    print(f"转换比例: {total_mahayana/total_chinese_pop*100:.1f}%" if total_chinese_pop > 0 else "无数据")
    
    # 检查所有=mahayana的情况
    all_mahayana = content.count('=mahayana')
    print(f"文件中所有=mahayana: {all_mahayana}")

if __name__ == "__main__":
    main()
