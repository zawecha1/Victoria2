#!/usr/bin/env python3
"""
测试新的块类型识别功能
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from victoria2_main_modifier import Victoria2Modifier

def test_block_identification():
    """测试块类型识别功能"""
    print("🧪 测试新的块类型识别功能")
    print("="*50)
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=True)
    
    # 测试文件
    test_file = "autosave.v2"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    print(f"📁 加载测试文件: {test_file}")
    
    # 加载文件
    if not modifier.load_file(test_file):
        print("❌ 文件加载失败")
        return False
    
    print("✅ 文件加载成功")
    
    # 测试各种功能类型的块查找
    function_types = [
        'militancy',   # 人口斗争性修改
        'culture',     # 中国文化修改  
        'infamy',      # 中国恶名度修改
        'population',  # 人口属性修改
        'date',        # 游戏日期修改
        'money'        # 人口金钱修改
    ]
    
    print(f"\n🔍 测试各功能类型的块查找:")
    print("-" * 50)
    
    results = {}
    
    for func_type in function_types:
        print(f"\n📊 测试功能类型: {func_type}")
        blocks = modifier.find_blocks_by_function_type(func_type)
        results[func_type] = len(blocks)
        
        if blocks:
            print(f"✅ 成功找到 {len(blocks)} 个相关块")
            
            # 显示前3个块的详细信息
            for i, block in enumerate(blocks[:3]):
                block_type = modifier._classify_block_type(block)
                print(f"   块 {i+1}: 类型={block_type}, 层级={block.level}, 大小={len(block.content)}")
        else:
            print(f"❌ 未找到相关块")
    
    # 显示总结
    print(f"\n📈 测试结果总结:")
    print("-" * 50)
    for func_type, count in results.items():
        status = "✅" if count > 0 else "❌"
        print(f"{status} {func_type:12} : {count:>5} 个块")
    
    # 检查是否所有功能都找到了相关块
    success_count = sum(1 for count in results.values() if count > 0)
    total_count = len(results)
    
    print(f"\n🎯 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 所有功能类型都成功找到相关块!")
        return True
    else:
        print("⚠️ 部分功能类型未找到相关块，请检查查找逻辑")
        return False

if __name__ == "__main__":
    test_block_identification()
