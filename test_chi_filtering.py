#!/usr/bin/env python3
"""
测试修复后的CHI块查找逻辑 - 确保只找到真正的国家定义块
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chi_block_filtering():
    """测试CHI块过滤逻辑"""
    print("🧪 测试修复后的CHI块查找逻辑")
    print("="*50)
    
    # 创建包含多种CHI引用的测试内容
    test_content = """
date=1841.12.17
CHI={
    tag=CHI
    primary_culture=beifaren
    badboy=5.5
    capital=1616
    technology={
        army_professionalism=1
    }
    government=absolute_monarchy
    plurality=0.0
    culture={
        nanfaren=yes
        manchu=yes
    }
}
diplomacy={
    relation={
        tag=CHI
        value=100
    }
    alliance={
        first=ENG
        second=CHI
        start_date=1840.1.1
    }
}
trade={
    CHI=50.0
}
war={
    name="Opium War"
    participants={
        CHI={
            exhaustion=0.5
        }
        ENG={
            exhaustion=0.1
        }
    }
}
"""
    
    # 写入临时测试文件
    test_file = "temp_chi_filter_test.v2"
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
        
        # 测试文化修改的CHI块查找
        print(f"\n🔍 测试文化修改的CHI块查找:")
        print("-" * 50)
        
        try:
            blocks = modifier.find_blocks_by_function_type('culture')
            print(f"✅ 找到 {len(blocks)} 个CHI国家定义块")
            
            if blocks:
                for i, block in enumerate(blocks):
                    print(f"  块 {i+1}: 大小={len(block.content)} 字符, 层级={block.level}")
                    print(f"       名称='{block.name}', 位置={block.start_pos}-{block.end_pos}")
                    
                    # 检查国家指标
                    country_indicators = [
                        'primary_culture', 'capital', 'technology', 'ruling_party',
                        'government', 'plurality', 'badboy', 'tag=CHI'
                    ]
                    indicator_count = sum(1 for indicator in country_indicators 
                                        if indicator in block.content)
                    print(f"       国家指标: {indicator_count}/8")
            
            # 预期结果：应该只找到1个真正的国家定义块
            if len(blocks) == 1:
                print("✅ 过滤逻辑正确：只找到真正的国家定义块")
                return True
            elif len(blocks) == 0:
                print("❌ 过滤过于严格：未找到国家定义块")
                return False
            else:
                print(f"⚠️ 可能仍有问题：找到了 {len(blocks)} 个块")
                return False
                
        except Exception as e:
            print(f"❌ CHI块查找出错: {e}")
            return False
        
    finally:
        # 清理临时文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 清理临时文件: {test_file}")

if __name__ == "__main__":
    success = test_chi_block_filtering()
    if success:
        print("\n🎉 CHI块过滤逻辑测试通过！")
    else:
        print("\n❌ CHI块过滤逻辑需要进一步调整")
