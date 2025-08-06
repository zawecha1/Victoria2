#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复意识形态替换问题的脚本
"""

import re

def test_ideology_replacement():
    """测试意识形态替换问题"""
    
    # 模拟真实的人口块内容
    sample_pop_block = """aristocrats=
        {
                id=11972433
                size=244
                native_american_minor=mahayana
                money=14183.38818
                ideology=
                {
1=8.25323
2=4.54782
3=40.19861
4=18.91043
5=1.24637
6=25.59711
7=1.24637
                }
                issues=
                {
1=0.28305
2=5.46198
                }
        }"""
    
    print("🧪 测试意识形态替换问题")
    print("=" * 50)
    
    # 提取ideology块
    ideology_pattern = r'ideology=\s*\{[^}]*\}'
    ideology_match = re.search(ideology_pattern, sample_pop_block, re.DOTALL)
    
    if ideology_match:
        full_ideology_block = ideology_match.group(0)
        print("原始ideology块:")
        print(repr(full_ideology_block))
        print("显示内容:")
        print(full_ideology_block)
        
        # 提取内容
        inner_content_match = re.search(r'ideology=\s*\{([^}]*)\}', full_ideology_block, re.DOTALL)
        if inner_content_match:
            ideology_content = inner_content_match.group(1)
            print(f"\n内容部分:")
            print(repr(ideology_content))
            
            # 模拟转换后的新内容
            new_ideology_content = """1=0.00000
                        2=0.00000
                        3=68.60864
                        4=0.00000
                        5=0.00000
                        6=31.39130
                        7=0.00000"""
            
            print(f"\n新内容:")
            print(repr(new_ideology_content))
            
            # 测试原始的替换方法
            print(f"\n🔧 测试原始替换方法:")
            new_ideology_block = f'ideology=\n\t\t{{\n\t\t\t{new_ideology_content}\n\t\t}}'
            print("新构建的块:")
            print(repr(new_ideology_block))
            
            test_result = sample_pop_block.replace(full_ideology_block, new_ideology_block)
            if test_result == sample_pop_block:
                print("❌ 原始方法替换失败！")
            else:
                print("✅ 原始方法替换成功")
            
            # 测试改进的替换方法
            print(f"\n🔧 测试改进替换方法:")
            # 分析原始格式
            lines = full_ideology_block.split('\n')
            print(f"原始块行数: {len(lines)}")
            for i, line in enumerate(lines):
                print(f"行{i}: {repr(line)}")
            
            # 智能构建新块，保持原始格式
            if len(lines) >= 3:
                # 保持开头和结尾的格式
                start_line = lines[0]  # "ideology="
                end_line = lines[-1]   # "                }"
                
                # 构建新的ideology块，保持原始缩进
                new_ideology_block_smart = start_line + '\n                {\n' + new_ideology_content + '\n' + end_line
                
                print("智能构建的块:")
                print(repr(new_ideology_block_smart))
                
                test_result_smart = sample_pop_block.replace(full_ideology_block, new_ideology_block_smart)
                if test_result_smart == sample_pop_block:
                    print("❌ 智能方法也替换失败！")
                else:
                    print("✅ 智能方法替换成功")
                    print(f"成功替换，新内容长度: {len(test_result_smart)}")
            
            # 测试最安全的方法：直接替换内容部分
            print(f"\n🔧 测试最安全替换方法:")
            safe_result = sample_pop_block.replace(ideology_content, new_ideology_content)
            if safe_result == sample_pop_block:
                print("❌ 安全方法也替换失败！")
                print("可能是内容不完全匹配")
                
                # 更精确的内容匹配
                clean_original = re.sub(r'\s+', ' ', ideology_content.strip())
                print(f"清理后的原始内容: {repr(clean_original)}")
                
            else:
                print("✅ 安全方法替换成功")
                print(f"成功替换，新内容长度: {len(safe_result)}")

if __name__ == "__main__":
    test_ideology_replacement()
