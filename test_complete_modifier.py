#!/usr/bin/env python3
"""
测试完整的主修改器功能，包括新的文明化状态修改
"""

from victoria2_main_modifier import Victoria2Modifier
import os

def test_complete_modifier():
    """测试完整的主修改器功能"""
    print("🧪 测试完整的Victoria II主修改器功能")
    print("="*80)
    
    filename = "autosave.v2"
    
    if not os.path.exists(filename):
        print(f"❌ 文件 {filename} 不存在")
        return False
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=False)
    
    print("📋 可用的修改功能:")
    print("1. modify_militancy() - 人口斗争性修改")
    print("2. modify_china_culture() - 中国文化修改") 
    print("3. modify_china_infamy() - 中国恶名度修改")
    print("4. modify_chinese_population() - 中国人口属性修改")
    print("5. modify_game_date() - 游戏日期修改")
    print("6. modify_chinese_population_money() - 人口金钱修改")
    print("7. modify_all_countries_civilized() - 🆕 所有国家文明化状态修改")
    print("8. execute_all_modifications() - 执行所有修改")
    
    print("\n🔧 测试单独的文明化状态修改功能...")
    
    # 加载文件
    if not modifier.load_file(filename):
        print("❌ 文件加载失败")
        return False
    
    print("✅ 文件加载成功")
    
    # 创建备份
    backup_name = modifier.create_backup(filename, "complete_test")
    print(f"📁 创建备份: {backup_name}")
    
    # 测试新的文明化修改功能
    print("\n🏛️ 测试文明化状态修改...")
    result = modifier.modify_all_countries_civilized("no")
    
    if result:
        print(f"✅ 文明化修改成功! 修改了 {modifier.civilized_changes} 个国家")
        
        # 保存测试结果
        test_output = "test_complete_modifier_output.v2"
        if modifier.save_file(test_output):
            print(f"💾 测试结果保存到: {test_output}")
            
            # 验证结果
            print("\n🔍 验证修改结果...")
            import re
            with open(test_output, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
            
            civilized_yes = len(re.findall(r'civilized\s*=\s*"?yes"?', content, re.IGNORECASE))
            civilized_no = len(re.findall(r'civilized\s*=\s*"?no"?', content, re.IGNORECASE))
            
            print(f"  验证结果:")
            print(f"    civilized=\"yes\": {civilized_yes}")
            print(f"    civilized=\"no\": {civilized_no}")
            
            if civilized_no > civilized_yes:
                print("✅ 验证成功: 大部分国家已设为非文明化状态")
                return True
            else:
                print("⚠️ 验证警告: 结果可能不完全正确")
                return False
        else:
            print("❌ 测试结果保存失败")
            return False
    else:
        print("❌ 文明化修改失败")
        return False

def show_usage_example():
    """显示使用示例"""
    print("\n" + "="*80)
    print("📖 使用示例:")
    print("="*80)
    
    example_code = '''
# 创建修改器实例
modifier = Victoria2Modifier(debug_mode=True)

# 加载存档文件
modifier.load_file("your_save_file.v2")

# 执行所有修改 (包括新的文明化状态修改)
modifier.execute_all_modifications("your_save_file.v2")

# 或者单独执行文明化状态修改
modifier.modify_all_countries_civilized("no")  # 设为非文明化
modifier.modify_all_countries_civilized("yes") # 设为文明化

# 保存修改结果
modifier.save_file("modified_save_file.v2")
'''
    
    print(example_code)
    print("="*80)

if __name__ == "__main__":
    # 运行完整测试
    success = test_complete_modifier()
    
    # 显示使用示例
    show_usage_example()
    
    print(f"\n🏁 测试结果: {'✅ 成功' if success else '❌ 失败'}")
    if success:
        print("🎉 所有功能测试通过! 新的文明化状态修改功能已成功集成到主修改器中!")
    else:
        print("⚠️ 测试未完全通过，请检查输出信息")
