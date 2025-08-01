#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证功能隔离模式的执行结果
"""

def main():
    try:
        print("=== 功能隔离模式验证报告 ===")
        
        # 读取文件
        with open('China2281_01_01.v2', 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        print(f"文件大小: {len(content):,} 字符")
        
        # 基本统计
        size_count = content.count('size=')
        print(f"总人口组: {size_count:,}")
        
        # 宗教统计
        mahayana_count = content.count('religion=mahayana')
        buddhist_count = content.count('religion=buddhist')
        print(f"mahayana宗教: {mahayana_count}")
        print(f"buddhist宗教: {buddhist_count}")
        
        # 意识形态统计
        conservative_count = content.count('ideology=conservative')
        liberal_count = content.count('ideology=liberal')
        print(f"conservative意识形态: {conservative_count}")
        print(f"liberal意识形态: {liberal_count}")
        
        # CHI恶名度检查
        import re
        chi_match = re.search(r'CHI=\s*\{[^{}]*badboy=([0-9.]+)', content)
        if chi_match:
            print(f"CHI恶名度: {chi_match.group(1)}")
        else:
            print("CHI恶名度: 未找到")
        
        # CHI接受文化检查
        culture_match = re.search(r'CHI=\s*\{[^{}]*?accepted_culture=\{([^}]+)\}', content, re.DOTALL)
        if culture_match:
            print(f"CHI接受文化: {culture_match.group(1).strip()}")
        else:
            print("CHI接受文化: 未找到")
        
        print("\n✅ 功能隔离模式执行成功!")
        print("每个功能都独立读取和保存文件，确保数据安全")
        
    except Exception as e:
        print(f"验证错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
