#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比当前文件和备份文件的差异
"""

def main():
    try:
        # 读取两个文件
        with open('China2281_01_01.v2', 'r', encoding='utf-8-sig') as f:
            current = f.read()
        
        with open('China2281_01_01_selective_backup_20250728_213116.v2', 'r', encoding='utf-8-sig') as f:
            backup = f.read()
        
        print("=== 文件对比报告 ===")
        print(f"当前文件大小: {len(current):,} 字符")
        print(f"备份文件大小: {len(backup):,} 字符")
        
        print("\n人口组数量对比:")
        current_size = current.count('size=')
        backup_size = backup.count('size=')
        print(f"当前文件 size= 数量: {current_size:,}")
        print(f"备份文件 size= 数量: {backup_size:,}")
        print(f"差异: {current_size - backup_size:,}")
        
        print("\n宗教数量对比:")
        current_mahayana = current.count('religion=mahayana')
        backup_mahayana = backup.count('religion=mahayana')
        print(f"当前文件 mahayana 数量: {current_mahayana}")
        print(f"备份文件 mahayana 数量: {backup_mahayana}")
        
        print("\n其他关键数据:")
        print(f"当前文件 farmers= 数量: {current.count('farmers=')}")
        print(f"备份文件 farmers= 数量: {backup.count('farmers=')}")
        
        print(f"当前文件 money= 数量: {current.count('money=')}")
        print(f"备份文件 money= 数量: {backup.count('money=')}")
        
        # 检查第一个省份的内容
        import re
        province_pattern = r'^1=\s*\{(.{0,5000})\}'
        current_match = re.search(province_pattern, current, re.MULTILINE | re.DOTALL)
        backup_match = re.search(province_pattern, backup, re.MULTILINE | re.DOTALL)
        
        if current_match and backup_match:
            current_province = current_match.group(1)
            backup_province = backup_match.group(1)
            
            print(f"\n省份1详细对比:")
            print(f"当前文件省份1长度: {len(current_province)} 字符")
            print(f"备份文件省份1长度: {len(backup_province)} 字符")
            print(f"当前文件省份1 size= 数量: {current_province.count('size=')}")
            print(f"备份文件省份1 size= 数量: {backup_province.count('size=')}")
            
            # 显示省份1的前500字符进行对比
            print(f"\n省份1前500字符对比:")
            print("当前文件:")
            print(repr(current_province[:500]))
            print("\n备份文件:")
            print(repr(backup_province[:500]))
        
    except Exception as e:
        print(f"对比失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
