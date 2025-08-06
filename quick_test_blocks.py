#!/usr/bin/env python3
"""
快速测试新的块类型识别功能 - 使用简化测试
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_with_small_file():
    """使用较小的测试文件快速测试"""
    print("🧪 快速测试新的块类型识别功能")
    print("="*50)
    
    # 创建一个简单的测试内容
    test_content = """
date=1836.1.1
version=1.3
CHI={
    tag=CHI
    primary_culture=beifaren
    badboy=0.0
    culture={
        nanfaren=yes
        manchu=yes
    }
}
1={
    owner=CHI
    controller=CHI
    farmers={
        culture=beifaren
        religion=mahayana
        militancy=0.0
        money=1000.0
    }
}
2={
    owner=ENG
    controller=ENG
    farmers={
        culture=english
        religion=protestant
        militancy=5.0
    }
}
"""
    
    # 写入临时测试文件
    test_file = "temp_test.v2"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        from victoria2_main_modifier import Victoria2Modifier
        
        # 创建修改器实例
        modifier = Victoria2Modifier(debug_mode=False)
        
        print(f"📁 加载测试文件: {test_file}")
        
        # 加载文件
        if not modifier.load_file(test_file):
            print("❌ 文件加载失败")
            return False
        
        print("✅ 文件加载成功")
        
        # 测试各种功能类型的块查找
        function_types = ['militancy', 'culture', 'infamy', 'population', 'date', 'money']
        
        print(f"\n🔍 测试各功能类型的块查找:")
        print("-" * 50)
        
        results = {}
        
        for func_type in function_types:
            print(f"\n📊 测试功能类型: {func_type}")
            try:
                blocks = modifier.find_blocks_by_function_type(func_type)
                results[func_type] = len(blocks)
                
                if blocks:
                    print(f"✅ 成功找到 {len(blocks)} 个相关块")
                else:
                    print(f"❌ 未找到相关块")
            except Exception as e:
                print(f"❌ 查找出错: {e}")
                results[func_type] = 0
        
        # 显示总结
        print(f"\n📈 测试结果总结:")
        print("-" * 50)
        for func_type, count in results.items():
            status = "✅" if count > 0 else "❌"
            print(f"{status} {func_type:12} : {count:>5} 个块")
        
        # 测试分析功能
        print(f"\n📊 测试完整的括号分析功能:")
        print("-" * 50)
        try:
            modifier.analyze_bracket_types()
            print("✅ 分析功能正常工作")
        except Exception as e:
            print(f"❌ 分析功能出错: {e}")
        
        return True
        
    finally:
        # 清理临时文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 清理临时文件: {test_file}")

if __name__ == "__main__":
    test_with_small_file()
