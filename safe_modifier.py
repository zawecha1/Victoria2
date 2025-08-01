#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全的Victoria II修改器
执行安全的、分步骤的修改
"""
from victoria2_main_modifier import Victoria2Modifier
import sys

def main():
    print("🛡️ Victoria II 安全修改器")
    print("="*50)
    
    filename = sys.argv[1] if len(sys.argv) > 1 else input("请输入文件名: ")
    
    modifier = Victoria2Modifier()
    if not modifier.load_file(filename):
        return
    
    # 创建备份
    backup = modifier.create_backup(filename, "safe")
    
    print("\n请选择修改项目:")
    print("1. 文化修改 (安全)")
    print("2. 恶名度修改 (安全)")
    print("3. 人口属性修改 (谨慎)")
    print("4. 全部修改")
    
    choice = input("选择 (1-4): ").strip()
    
    if choice in ['1', '4']:
        print("\n执行文化修改...")
        modifier.modify_china_culture()
    
    if choice in ['2', '4']:
        print("\n执行恶名度修改...")
        modifier.modify_china_infamy()
    
    if choice in ['3', '4']:
        print("\n⚠️ 人口属性修改有风险，建议分批处理")
        batch_size = input("输入要处理的省份数量 (推荐50-100，回车=全部): ").strip()
        
        if batch_size.isdigit():
            batch_size = int(batch_size)
        else:
            batch_size = None
            
        print(f"\n执行人口属性修改...")
        modifier.modify_chinese_population(batch_size)
    
    modifier.save_file(filename)
    print(f"\n✅ 修改完成！备份文件: {backup}")

if __name__ == "__main__":
    main()
