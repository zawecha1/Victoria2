#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的CHI块查找算法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from victoria2_main_modifier import Victoria2Modifier

def test_chi_finding():
    """测试CHI块查找"""
    print("=" * 60)
    print("测试修复后的CHI块查找算法")
    print("=" * 60)
    
    modifier = Victoria2Modifier()
    filename = "China2281_01_01.v2"
    
    if not modifier.load_file(filename):
        print("❌ 文件加载失败")
        return
    
    print(f"文件大小: {len(modifier.content):,} 字符")
    
    # 测试文化修改功能
    print("\n🧪 测试文化修改算法...")
    try:
        # 只测试查找，不实际修改
        import re
        
        # 查找真正的CHI国家定义块
        china_pattern = r'\nCHI=\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*(?:primary_culture|capital|technology|ruling_party|upper_house|consciousness|nonstate_consciousness|schools|political_reform_want|social_reform_want|government|plurality|revanchism|war_policy|economic_policy|trade_policy|religious_policy|citizenship_policy|war_exhaustion|badboy|mobilized|created_from|ai)'
        china_matches = list(re.finditer(china_pattern, modifier.content, re.DOTALL))
        
        print(f"找到包含国家字段的CHI块: {len(china_matches)} 个")
        
        if not china_matches:
            # 备选：查找所有CHI块并选择最大的
            print("查找所有CHI块...")
            all_chi_patterns = list(re.finditer(r'\nCHI=\s*\{', modifier.content))
            print(f"总共找到CHI块: {len(all_chi_patterns)} 个")
            
            # 分析每个CHI块的大小
            for i, match in enumerate(all_chi_patterns[:10]):  # 只显示前10个
                start_pos = match.start()
                next_country_pattern = r'\n[A-Z]{3}=\s*{'
                next_country_match = re.search(next_country_pattern, modifier.content[start_pos + 100:])
                
                if next_country_match:
                    end_pos = start_pos + 100 + next_country_match.start()
                else:
                    end_pos = len(modifier.content)
                
                chi_size = end_pos - start_pos
                context = modifier.content[max(0, start_pos-50):start_pos+150]
                
                print(f"CHI块 {i+1}: 位置 {start_pos}-{end_pos}, 大小 {chi_size:,} 字符")
                print(f"  上下文: {repr(context[:100])}...")
        else:
            for i, match in enumerate(china_matches):
                start_pos = match.start()
                context = modifier.content[max(0, start_pos-50):start_pos+200]
                print(f"包含国家字段的CHI块 {i+1}: 位置 {start_pos}")
                print(f"  上下文: {repr(context[:150])}...")
        
        print("\n✅ CHI块查找测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chi_finding()
