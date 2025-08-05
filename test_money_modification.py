#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中国人口金钱修改功能
"""

import os
import shutil
from victoria2_main_modifier import Victoria2Modifier

def test_chinese_money_modification():
    """测试中国人口金钱修改功能"""
    print("=" * 60)
    print("测试中国人口金钱修改功能")
    print("=" * 60)
    
    # 查找可用的存档文件
    save_files = [f for f in os.listdir('.') if f.endswith('.v2') and not f.endswith('backup.v2')]
    
    if not save_files:
        print("❌ 没有找到存档文件!")
        return False
    
    print(f"找到 {len(save_files)} 个存档文件:")
    for i, file in enumerate(save_files, 1):
        size = os.path.getsize(file) / (1024 * 1024)  # MB
        print(f"  {i}. {file} ({size:.1f} MB)")
    
    # 选择第一个文件进行测试
    test_file = save_files[0]
    print(f"\n📁 选择测试文件: {test_file}")
    
    # 创建测试备份
    test_backup = f"{test_file}_money_test_backup"
    print(f"📋 创建测试备份: {test_backup}")
    shutil.copy2(test_file, test_backup)
    
    try:
        # 创建修改器实例
        modifier = Victoria2Modifier()
        
        # 加载文件
        print(f"\n📖 加载文件...")
        if not modifier.load_file(test_file):
            print("❌ 文件加载失败!")
            return False
        
        # 测试金钱修改
        print(f"\n💰 测试中国人口金钱修改...")
        success = modifier.modify_chinese_population_money(9999999.0)
        
        if success and modifier.money_changes > 0:
            print(f"✅ 金钱修改成功! 共修改 {modifier.money_changes} 处")
            
            # 保存修改后的文件
            test_output = f"{test_file}_money_test"
            print(f"💾 保存测试结果到: {test_output}")
            modifier.save_file(test_output)
            
            # 验证修改结果
            verify_money_changes(test_output)
            
        else:
            print(f"❌ 金钱修改失败! 修改数量: {modifier.money_changes}")
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
    print("✅ 中国人口金钱修改功能测试完成!")
    print("=" * 60)
    return True

def verify_money_changes(filename: str):
    """验证金钱修改结果"""
    print(f"\n🔍 验证修改结果...")
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 验证文件读取失败: {e}")
        return
    
    import re
    
    # 查找中国省份的金钱样本
    china_samples = re.findall(r'owner="?CHI"?[\s\S]{1,2000}money=([\d.]+)', content)
    if china_samples:
        # 检查前几个样本
        for i, money_str in enumerate(china_samples[:5]):  # 检查前5个样本
            money = float(money_str)
            if abs(money - 9999999.0) < 0.1:  # 允许小的浮点精度误差
                print(f"✅ 中国人口金钱验证通过 (样本{i+1}): {money:,.0f}")
            else:
                print(f"❌ 中国人口金钱验证失败 (样本{i+1}): {money:,.0f} (期望: 9,999,999)")
        
        print(f"📊 总共找到 {len(china_samples)} 个中国人口金钱记录")
    else:
        print("⚠️ 未找到中国省份金钱数据")
    
    # 检查其他国家的金钱是否未被误修改
    other_samples = re.findall(r'owner="?([A-Z]{3})"?[\s\S]{1,1000}money=([\d.]+)', content)
    other_count = 0
    for country, money_str in other_samples[:10]:  # 检查前10个样本
        if country != "CHI":
            money = float(money_str)
            if abs(money - 9999999.0) < 0.1:  # 如果其他国家也被修改了
                print(f"⚠️ 警告: {country}人口金钱也被修改为: {money:,.0f}")
            else:
                other_count += 1
    
    if other_count > 0:
        print(f"✅ 确认其他国家人口金钱未被误修改 (检查了{other_count}个样本)")

def test_selective_money_modification():
    """测试选择性修改中的金钱功能"""
    print("\n" + "=" * 60)
    print("测试选择性修改 - 仅金钱功能")
    print("=" * 60)
    
    # 查找可用的存档文件
    save_files = [f for f in os.listdir('.') if f.endswith('.v2') and not f.endswith('backup.v2')]
    
    if not save_files:
        print("❌ 没有找到存档文件!")
        return False
    
    test_file = save_files[0]
    print(f"📁 选择测试文件: {test_file}")
    
    # 创建测试备份
    test_backup = f"{test_file}_selective_money_backup"
    print(f"📋 创建测试备份: {test_backup}")
    shutil.copy2(test_file, test_backup)
    
    try:
        # 创建修改器实例
        modifier = Victoria2Modifier()
        
        # 测试选择性修改 - 仅金钱
        options = {
            'militancy': False,
            'culture': False,
            'infamy': False,
            'population': False,
            'date': False,
            'money': True  # 仅选择金钱修改
        }
        
        print(f"\n💰 测试选择性修改 - 仅金钱功能...")
        success = modifier.execute_selective_modifications(test_file, options)
        
        if success:
            print(f"✅ 选择性金钱修改成功!")
            
            # 验证修改结果
            verify_money_changes(test_file)
            
        else:
            print(f"❌ 选择性金钱修改失败!")
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
    print("✅ 选择性金钱修改功能测试完成!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    # 测试基本金钱修改功能
    test1_result = test_chinese_money_modification()
    
    # 测试选择性修改中的金钱功能
    test2_result = test_selective_money_modification()
    
    print(f"\n🎯 总测试结果:")
    print(f"基本金钱修改功能: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"选择性金钱修改功能: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过! 中国人口金钱修改功能正常工作!")
    else:
        print("\n⚠️ 部分测试失败，请检查代码。")
