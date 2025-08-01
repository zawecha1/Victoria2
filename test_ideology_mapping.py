#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
非交互式测试意识形态映射 - 测试Liberal=ID 5
"""

import sys
import os
from chinese_pop_modifier import ChinesePopulationModifier

def test_ideology_mapping(source_file, test_file):
    """测试意识形态映射的非交互式版本"""
    
    print("🧪 意识形态映射测试 (Liberal = ID 5)")
    print("="*50)
    
    # 复制源文件到测试文件
    print(f"复制 {source_file} 到 {test_file}")
    import shutil
    shutil.copy2(source_file, test_file)
    
    # 创建修改器实例
    modifier = ChinesePopulationModifier()
    
    print(f"\n目标文件: {test_file}")
    print("修改内容:")
    print("- 所有中国人口宗教 → mahayana")
    print("- 意识形态调整 (测试Liberal=ID 5):")
    print("  • Reactionary(1) + Socialist(4) + Communist(7) → Conservative(3)")
    print("  • Fascist(2) + Anarcho-Liberal(6) → Liberal(5)")
    print("="*50)
    
    # 执行修改
    success = modifier.modify_chinese_populations(test_file)
    
    if success:
        print("\n✅ 测试修改成功!")
        print("📁 备份文件已创建")
        
        # 显示统计信息
        print(f"\n📊 修改统计:")
        print(f"宗教修改: {modifier.religion_changes} 处")
        print(f"意识形态修改: {modifier.ideology_changes} 处")
        print(f"总修改数: {modifier.modifications_count} 个人口组")
        
        return True
    else:
        print("\n❌ 测试修改失败!")
        return False

def main():
    """主函数"""
    
    if len(sys.argv) < 2:
        print("用法: python test_ideology_mapping.py <源文件> [测试文件名]")
        print("示例: python test_ideology_mapping.py China2245_04_06.v2 test_liberal_id5.v2")
        return
    
    source_file = sys.argv[1]
    test_file = sys.argv[2] if len(sys.argv) > 2 else "test_liberal_id5.v2"
    
    # 检查源文件是否存在
    if not os.path.exists(source_file):
        print(f"❌ 源文件不存在: {source_file}")
        return
    
    # 执行测试
    success = test_ideology_mapping(source_file, test_file)
    
    if success:
        print(f"\n🎯 测试完成！请检查文件: {test_file}")
        print("💡 可以用以下命令检查结果:")
        print(f"   python check_single_file.py {test_file} 3")
    else:
        print("\n❌ 测试失败!")

if __name__ == "__main__":
    main()
