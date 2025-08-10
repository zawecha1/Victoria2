#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 中国人口清理工具 - 快速测试脚本
"""

import os
import shutil
from datetime import datetime

def create_test_copy(source_file):
    """创建测试用的存档副本"""
    if not os.path.exists(source_file):
        print(f"错误: 源文件不存在 {source_file}")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    test_file = f"test_population_clean_{timestamp}.v2"
    
    try:
        shutil.copy2(source_file, test_file)
        print(f"测试副本已创建: {test_file}")
        return test_file
    except Exception as e:
        print(f"创建测试副本失败: {e}")
        return None

def run_population_cleaner_test():
    """运行人口清理工具测试"""
    print("=" * 60)
    print("Victoria II 中国人口清理工具 - 安全测试")
    print("=" * 60)
    
    # 列出可用的存档文件
    v2_files = [f for f in os.listdir('.') if f.endswith('.v2')]
    
    if not v2_files:
        print("当前目录下没有找到.v2存档文件")
        return
    
    print("找到的存档文件:")
    for i, f in enumerate(v2_files, 1):
        size = os.path.getsize(f) / (1024 * 1024)
        print(f"  {i}. {f} ({size:.1f} MB)")
    
    # 选择文件
    while True:
        try:
            choice = input(f"\n选择要测试的文件 (1-{len(v2_files)}): ").strip()
            if not choice:
                print("操作取消")
                return
            
            index = int(choice) - 1
            if 0 <= index < len(v2_files):
                source_file = v2_files[index]
                break
            else:
                print(f"请输入1到{len(v2_files)}之间的数字")
        except ValueError:
            print("请输入有效的数字")
    
    print(f"\n选择的文件: {source_file}")
    
    # 创建测试副本
    test_file = create_test_copy(source_file)
    if not test_file:
        return
    
    # 运行预览
    print("\n步骤1: 运行预览分析...")
    os.system(f'python china_population_cleaner.py "{test_file}" preview')
    
    # 询问是否继续测试执行
    print("\n" + "-" * 40)
    print("预览完成！现在可以选择:")
    print("1. 继续测试实际执行 (在测试副本上)")
    print("2. 停止测试")
    
    choice = input("继续测试执行吗? (y/n): ").strip().lower()
    
    if choice in ['y', 'yes', '是']:
        print(f"\n步骤2: 在测试副本 {test_file} 上执行清理...")
        os.system(f'python china_population_cleaner.py "{test_file}" execute')
        
        print(f"\n测试完成!")
        print(f"原文件: {source_file} (未修改)")
        print(f"测试文件: {test_file} (已修改)")
        print(f"备份文件: {test_file}.backup_* (自动创建)")
        
        # 询问是否删除测试文件
        cleanup = input("\n删除测试文件吗? (y/n): ").strip().lower()
        if cleanup in ['y', 'yes', '是']:
            try:
                # 删除测试文件和相关备份
                for f in os.listdir('.'):
                    if f.startswith(test_file.replace('.v2', '')):
                        os.remove(f)
                        print(f"已删除: {f}")
            except Exception as e:
                print(f"清理文件时出错: {e}")
    else:
        print("测试停止")
        # 删除测试副本
        try:
            os.remove(test_file)
            print(f"已删除测试副本: {test_file}")
        except:
            print(f"请手动删除测试副本: {test_file}")

if __name__ == "__main__":
    run_population_cleaner_test()
