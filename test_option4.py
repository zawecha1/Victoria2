#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试选项4 - 中国人口属性修改
"""

import sys
from victoria2_main_modifier import Victoria2Modifier

def test_option_4():
    """测试选项4的意识形态修改效果"""
    
    print("🧪 测试选项4 - 中国人口属性修改")
    print("=" * 50)
    
    filename = 'China1837_01_24.v2'
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=True)
    
    print("🔄 执行load_file...")
    if modifier.load_file(filename):
        print("✅ load_file成功")
        
        print("🔄 执行modify_chinese_population...")
        if modifier.modify_chinese_population():
            print(f"✅ modify_chinese_population成功")
            print(f"   宗教修改: {modifier.religion_changes}")
            print(f"   意识形态修改: {modifier.ideology_changes}")
            print(f"   总修改数: {modifier.population_count}")
            
            print("🔄 执行save_file...")
            if modifier.save_file(filename):
                print("✅ save_file成功")
                
                # 立即验证
                print("\n🔍 立即验证修改效果...")
                modifier.verify_ideology_modifications(filename)
                
            else:
                print("❌ save_file失败")
        else:
            print("❌ modify_chinese_population失败")
    else:
        print("❌ load_file失败")

if __name__ == "__main__":
    test_option_4()
