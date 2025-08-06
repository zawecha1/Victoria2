#!/usr/bin/env python3
"""
测试修改功能中的块类型识别
"""

import sys
import os

# 添加当前目录到路径  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_modification_with_block_analysis():
    """测试修改功能中的块类型识别"""
    print("🧪 测试修改功能中的块类型识别")
    print("="*50)
    
    # 创建测试内容
    test_content = """
date=1841.12.17
CHI={
    tag=CHI
    primary_culture=beifaren
    badboy=5.5
    culture={
        nanfaren=yes
        manchu=yes
    }
    technology={
        army_professionalism=1
    }
}
1760={
    owner=CHI
    controller=CHI
    farmers={
        culture=beifaren
        religion=buddhist
        militancy=3.5
        consciousness=2.1
        money=500.0
        bank=200.0
        ideology={
            conservative=0.7
            liberal=0.3
        }
    }
    artisans={
        culture=beifaren
        religion=mahayana
        militancy=2.0
        money=800.0
    }
}
"""
    
    # 写入临时测试文件
    test_file = "temp_modify_test.v2"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        from victoria2_main_modifier import Victoria2Modifier
        
        # 创建修改器实例
        modifier = Victoria2Modifier(debug_mode=True)
        
        print(f"📁 加载测试文件: {test_file}")
        
        # 加载文件
        if not modifier.load_file(test_file):
            print("❌ 文件加载失败")
            return False
        
        print("✅ 文件加载成功")
        
        # 测试恶名度修改功能（使用块识别）
        print(f"\n🧪 测试恶名度修改功能 (包含块识别):")
        print("-" * 50)
        
        try:
            success = modifier.modify_china_infamy(0.0)
            if success:
                print("✅ 恶名度修改成功")
            else:
                print("❌ 恶名度修改失败")
        except Exception as e:
            print(f"❌ 恶名度修改出错: {e}")
        
        # 测试文化修改功能（使用块识别）
        print(f"\n🧪 测试文化修改功能 (包含块识别):")
        print("-" * 50)
        
        try:
            success = modifier.modify_china_culture("beifaren", ["nanfaren", "manchu"])
            if success:
                print("✅ 文化修改成功")
            else:
                print("❌ 文化修改失败")
        except Exception as e:
            print(f"❌ 文化修改出错: {e}")
        
        return True
        
    finally:
        # 清理临时文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 清理临时文件: {test_file}")

if __name__ == "__main__":
    test_modification_with_block_analysis()
