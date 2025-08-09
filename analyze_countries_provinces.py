#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国家省份分析工具 (analyze_countries_provinces.py)
==================================================
分析Victoria II存档中每个国家拥有的省份数量和详细信息

功能:
1. 统计每个国家的省份数量
2. 记录每个省份的详细信息（ID、名称、控制者、核心声明等）
3. 保存分析结果到JSON文件
4. 显示统计摘要

使用方法:
    python analyze_countries_provinces.py
    
输出:
    countries_provinces_analysis_YYYYMMDD_HHMMSS.json
"""

from victoria2_main_modifier import Victoria2Modifier
import os
import sys

def main():
    """主函数：执行国家省份分析"""
    print("🌍 Victoria II 国家省份分析工具")
    print("=" * 50)
    
    # 查找存档文件
    available_files = []
    for file in os.listdir('.'):
        if file.endswith('.v2'):
            available_files.append(file)
    
    if not available_files:
        print("❌ 未找到.v2存档文件")
        return
    
    print(f"📁 找到 {len(available_files)} 个存档文件:")
    for i, file in enumerate(available_files, 1):
        size_mb = os.path.getsize(file) / (1024 * 1024)
        print(f"   {i}. {file} ({size_mb:.1f} MB)")
    
    # 选择文件
    if len(available_files) == 1:
        selected_file = available_files[0]
        print(f"\n📂 自动选择: {selected_file}")
    else:
        try:
            choice = input(f"\n请选择文件 (1-{len(available_files)}): ").strip()
            if not choice:
                selected_file = available_files[0]
                print(f"📂 使用默认: {selected_file}")
            else:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(available_files):
                    selected_file = available_files[choice_idx]
                else:
                    print("❌ 无效选择，使用第一个文件")
                    selected_file = available_files[0]
        except ValueError:
            print("❌ 无效输入，使用第一个文件")
            selected_file = available_files[0]
    
    print(f"\n🔍 开始分析: {selected_file}")
    
    try:
        # 初始化修改器
        modifier = Victoria2Modifier(selected_file, debug_mode=True)
        
        # 执行分析并保存
        result_file = modifier.save_countries_provinces_analysis()
        
        if result_file:
            print(f"\n✅ 分析完成！结果已保存到: {result_file}")
            
            # 询问是否打开结果文件
            open_file = input("\n是否要打开结果文件? (y/N): ").strip().lower()
            if open_file in ['y', 'yes', '是']:
                try:
                    os.system(f'notepad "{result_file}"')
                except:
                    print(f"请手动打开文件: {result_file}")
        else:
            print("❌ 分析失败")
            
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        import traceback
        traceback.print_exc()

def test_with_autosave():
    """使用autosave.v2进行快速测试"""
    print("🧪 快速测试模式：使用 autosave.v2")
    print("=" * 40)
    
    if not os.path.exists('autosave.v2'):
        print("❌ 未找到 autosave.v2 文件")
        return
    
    try:
        modifier = Victoria2Modifier('autosave.v2', debug_mode=True)
        result_file = modifier.save_countries_provinces_analysis("test_provinces_analysis.json")
        
        if result_file:
            print(f"✅ 测试完成！结果保存到: {result_file}")
        else:
            print("❌ 测试失败")
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")

if __name__ == "__main__":
    print("选择运行模式:")
    print("1. 交互式分析 (默认)")
    print("2. 快速测试 (使用autosave.v2)")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "2":
        test_with_autosave()
    else:
        main()
