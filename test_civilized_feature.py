#!/usr/bin/env python3
"""
测试文明化状态修改功能
"""

import sys
import os
from victoria2_main_modifier import Victoria2Modifier

def test_civilized_modification():
    """测试文明化状态修改功能"""
    print("🧪 测试文明化状态修改功能")
    print("="*60)
    
    # 使用现有的存档文件
    filename = "autosave.v2"
    
    if not os.path.exists(filename):
        print(f"❌ 测试文件 {filename} 不存在")
        return False
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=True)
    
    # 加载文件
    print("📂 正在加载文件...")
    if not modifier.load_file(filename):
        print("❌ 文件加载失败")
        return False
    
    print("✅ 文件加载成功")
    
    # 测试单独的文明化修改功能
    print("\n🏛️ 测试单独的文明化修改功能...")
    
    # 创建备份
    backup_name = modifier.create_backup(filename, "civilized_test")
    print(f"📁 创建备份: {backup_name}")
    
    # 执行文明化修改
    try:
        result = modifier.modify_all_countries_civilized("no")
        print(f"\n📊 修改结果: {'成功' if result else '失败'}")
        print(f"📈 修改统计: {modifier.civilized_changes} 个国家")
        
        if result:
            # 保存文件
            test_filename = "test_civilized_output.v2"
            if modifier.save_file(test_filename):
                print(f"💾 测试结果已保存到: {test_filename}")
                
                # 简单验证
                print("\n🔍 简单验证...")
                with open(test_filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                    content = f.read()
                
                # 统计 civilized="no" 的数量
                import re
                no_count = len(re.findall(r'civilized\s*=\s*"no"', content))
                yes_count = len(re.findall(r'civilized\s*=\s*"yes"', content))
                
                print(f"   civilized=\"no\": {no_count} 个")
                print(f"   civilized=\"yes\": {yes_count} 个")
                
                if no_count > yes_count:
                    print("✅ 验证成功: 大部分国家已设为非文明化")
                else:
                    print("⚠️ 验证警告: 非文明化国家数量较少")
                
                return True
            else:
                print("❌ 测试文件保存失败")
                return False
        else:
            print("❌ 文明化修改失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_find_countries_blocks():
    """测试查找国家块功能"""
    print("\n🔍 测试查找国家块功能")
    print("="*60)
    
    filename = "autosave.v2"
    modifier = Victoria2Modifier(debug_mode=False)
    
    if modifier.load_file(filename):
        print("📂 文件加载成功")
        
        # 测试查找国家块
        country_blocks = modifier.find_blocks_by_function_type('countries')
        print(f"📊 找到 {len(country_blocks)} 个国家块")
        
        if country_blocks:
            print("\n🌍 前5个国家块示例:")
            for i, block in enumerate(country_blocks[:5], 1):
                # 查找国家标识符
                import re
                tag_match = re.search(r'^([A-Z]{3})\s*=\s*{', block.content.strip())
                tag = tag_match.group(1) if tag_match else "未知"
                
                # 查找文明化状态
                civilized_match = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', block.content)
                civilized = civilized_match.group(1) if civilized_match else "未设置"
                
                print(f"   {i}. {tag}: civilized={civilized}")
            
            return True
        else:
            print("❌ 未找到国家块")
            return False
    else:
        print("❌ 文件加载失败")
        return False

if __name__ == "__main__":
    print("🧪 文明化状态修改功能测试")
    print("="*80)
    
    # 测试1: 查找国家块
    success1 = test_find_countries_blocks()
    
    # 测试2: 文明化修改
    success2 = test_civilized_modification()
    
    print("\n" + "="*80)
    print("🏁 测试完成总结:")
    print(f"   查找国家块: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   文明化修改: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("🎉 所有测试通过!")
    else:
        print("⚠️ 部分测试失败")
