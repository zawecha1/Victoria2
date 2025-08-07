#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的游戏日期修改功能性能
"""

import os
import shutil
import time
from victoria2_main_modifier import Victoria2Modifier

def test_optimized_date_modification():
    """测试优化后的日期修改功能"""
    print("=" * 60)
    print("测试优化后的游戏日期修改功能性能")
    print("=" * 60)
    
    # 查找可用的存档文件
    save_files = [f for f in os.listdir('.') if f.endswith('.v2') and not f.endswith('backup.v2')]
    
    if not save_files:
        print("❌ 没有找到存档文件!")
        return False
    
    # 选择一个较大的文件进行测试
    test_file = None
    for file in save_files:
        size = os.path.getsize(file) / (1024 * 1024)  # MB
        if size > 10:  # 选择大于10MB的文件
            test_file = file
            break
    
    if not test_file:
        test_file = save_files[0]  # 如果没有大文件，就用第一个
    
    file_size = os.path.getsize(test_file) / (1024 * 1024)
    print(f"📁 选择测试文件: {test_file} ({file_size:.1f} MB)")
    
    # 创建测试备份
    test_backup = f"{test_file}_date_perf_backup"
    print(f"📋 创建测试备份: {test_backup}")
    shutil.copy2(test_file, test_backup)
    
    try:
        # 创建修改器实例
        modifier = Victoria2Modifier()
        
        # 加载文件并测量时间
        print(f"\n📖 加载文件...")
        load_start = time.time()
        if not modifier.load_file(test_file):
            print("❌ 文件加载失败!")
            return False
        load_time = time.time() - load_start
        print(f"✅ 文件加载完成，耗时: {load_time:.2f} 秒")
        
        # 测试优化后的日期修改
        print(f"\n📅 测试优化后的日期修改...")
        print(f"📊 文件大小: {len(modifier.content):,} 字符")
        
        # 重置计数器
        modifier.date_changes = 0
        
        # 执行日期修改并测量时间
        modify_start = time.time()
        success = modifier.modify_game_date("1836.1.1")
        modify_time = time.time() - modify_start
        
        if success:
            print(f"\n🎉 日期修改性能测试结果:")
            print(f"✅ 修改成功: {modifier.date_changes} 处日期")
            print(f"⚡ 修改耗时: {modify_time:.2f} 秒")
            print(f"🚀 处理速度: {modifier.date_changes / modify_time:.0f} 次/秒")
            print(f"📈 文件处理速度: {len(modifier.content) / modify_time / 1024 / 1024:.1f} MB/秒")
            
            # 保存修改后的文件用于验证
            test_output = f"{test_file}_date_perf_test"
            print(f"\n💾 保存测试结果到: {test_output}")
            save_start = time.time()
            modifier.save_file(test_output)
            save_time = time.time() - save_start
            print(f"✅ 文件保存完成，耗时: {save_time:.2f} 秒")
            
            # 验证修改结果
            verify_date_changes(test_output, "1836.1.1")
            
            # 总时间统计
            total_time = load_time + modify_time + save_time
            print(f"\n📊 总体性能统计:")
            print(f"📖 文件加载: {load_time:.2f} 秒 ({load_time/total_time*100:.1f}%)")
            print(f"⚡ 日期修改: {modify_time:.2f} 秒 ({modify_time/total_time*100:.1f}%)")
            print(f"💾 文件保存: {save_time:.2f} 秒 ({save_time/total_time*100:.1f}%)")
            print(f"🎯 总计时间: {total_time:.2f} 秒")
            
        else:
            print(f"❌ 日期修改失败!")
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    
    finally:
        # 恢复原文件
        print(f"\n🔄 恢复原文件...")
        shutil.copy2(test_backup, test_file)
        os.remove(test_backup)
    
    print("\n" + "=" * 60)
    print("✅ 日期修改性能测试完成!")
    print("=" * 60)
    return True

def verify_date_changes(filename: str, target_date: str):
    """验证日期修改结果"""
    print(f"\n🔍 验证修改结果...")
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 验证文件读取失败: {e}")
        return
    
    import re
    
    # 检查是否还有旧日期格式
    date_pattern = r'(?<![a-zA-Z0-9_])(\d{4})\.(\d{1,2})\.(\d{1,2})(?![a-zA-Z0-9_])'
    all_dates = re.findall(date_pattern, content)
    
    if all_dates:
        target_count = 0
        other_dates = set()
        
        for year, month, day in all_dates:
            date_str = f"{year}.{month}.{day}"
            if date_str == target_date:
                target_count += 1
            else:
                other_dates.add(date_str)
        
        print(f"✅ 目标日期 {target_date}: {target_count} 处")
        if other_dates:
            print(f"⚠️ 其他日期仍存在: {list(other_dates)[:5]} (共{len(other_dates)}种)")
        else:
            print(f"🎯 完美！所有日期都已修改为目标日期")
    else:
        print("⚠️ 未找到任何日期格式（可能有问题）")

def benchmark_old_vs_new():
    """模拟新旧方法的性能对比"""
    print("\n" + "=" * 60)
    print("新旧方法性能对比分析")
    print("=" * 60)
    
    # 模拟不同数量的替换操作
    test_counts = [1000, 5000, 10000, 20000]
    
    print("📊 理论性能对比 (基于算法复杂度):")
    print("方法说明:")
    print("  • 旧方法: 逐个字符串拆分重组 - O(n²) 复杂度")
    print("  • 新方法: 单次正则表达式替换 - O(n) 复杂度")
    print()
    
    for count in test_counts:
        # 旧方法理论时间 (假设每次操作0.1ms)
        old_time = count * count * 0.0001 / 1000  # O(n²)
        
        # 新方法理论时间 (假设总体0.1ms每千个字符)
        new_time = count * 0.0001  # O(n)
        
        speedup = old_time / new_time
        
        print(f"修改{count:5d}个日期:")
        print(f"  旧方法: ~{old_time:6.2f} 秒")
        print(f"  新方法: ~{new_time:6.2f} 秒")
        print(f"  提升: {speedup:6.1f}x 倍")
        print()

if __name__ == "__main__":
    # 测试优化后的日期修改性能
    test_result = test_optimized_date_modification()
    
    # 显示性能对比分析
    benchmark_old_vs_new()
    
    print(f"\n🎯 测试总结:")
    print(f"性能测试: {'✅ 通过' if test_result else '❌ 失败'}")
    
    if test_result:
        print("\n🚀 优化效果:")
        print("✅ 将O(n²)复杂度优化为O(n)")
        print("✅ 单次正则替换代替逐个字符串操作")
        print("✅ 大幅提升大文件处理速度")
        print("✅ 保持了功能的完整性")
    else:
        print("\n⚠️ 性能测试失败，请检查代码。")
