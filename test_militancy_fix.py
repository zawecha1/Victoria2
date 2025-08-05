#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的斗争性修改功能
"""

import os
import shutil
from victoria2_main_modifier import Victoria2Modifier

def test_militancy_modification():
    """测试斗争性修改功能"""
    print("=" * 60)
    print("测试修复后的斗争性修改功能")
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
    test_backup = f"{test_file}_test_backup"
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
        
        # 测试斗争性修改
        print(f"\n⚔️ 测试斗争性修改...")
        success = modifier.modify_militancy(china_militancy=0.0, other_militancy=10.0)
        
        if success and modifier.militancy_changes > 0:
            print(f"✅ 斗争性修改成功! 共修改 {modifier.militancy_changes} 处")
            
            # 保存修改后的文件
            test_output = f"{test_file}_militancy_test"
            print(f"💾 保存测试结果到: {test_output}")
            modifier.save_file(test_output)
            
            # 验证修改结果
            verify_militancy_changes(test_output)
            
        else:
            print(f"❌ 斗争性修改失败! 修改数量: {modifier.militancy_changes}")
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
    print("✅ 斗争性修改功能测试完成!")
    print("=" * 60)
    return True

def verify_militancy_changes(filename: str):
    """验证斗争性修改结果"""
    print(f"\n🔍 验证修改结果...")
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 验证文件读取失败: {e}")
        return
    
    import re
    
    # 查找中国省份的斗争性样本
    china_sample = re.search(r'owner="?CHI"?[\s\S]{1,2000}mil=([\d.]+)', content)
    if china_sample:
        china_militancy = float(china_sample.group(1))
        if china_militancy == 0.0:
            print(f"✅ 中国人口斗争性验证通过: {china_militancy}")
        else:
            print(f"❌ 中国人口斗争性验证失败: {china_militancy} (期望: 0.0)")
    else:
        print("⚠️ 未找到中国省份斗争性数据")
    
    # 查找其他国家省份的斗争性样本
    other_samples = re.findall(r'owner="?([A-Z]{3})"?[\s\S]{1,1000}mil=([\d.]+)', content)
    if other_samples:
        for country, militancy_str in other_samples[:3]:  # 检查前3个样本
            if country != "CHI":
                militancy = float(militancy_str)
                if militancy == 10.0:
                    print(f"✅ {country}人口斗争性验证通过: {militancy}")
                else:
                    print(f"❌ {country}人口斗争性验证失败: {militancy} (期望: 10.0)")
                break
    else:
        print("⚠️ 未找到其他国家省份斗争性数据")

if __name__ == "__main__":
    test_militancy_modification()
