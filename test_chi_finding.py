#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修正后的CHI块查找功能
"""

import re

def test_chi_block_finding():
    try:
        with open('China2281_01_01.v2', 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        print("=== 测试CHI块查找 ===")
        
        # 方法1: 使用\b词边界
        pattern1 = r'\bCHI=\s*\{'
        match1 = re.search(pattern1, content, re.MULTILINE)
        
        # 方法2: 使用^行首
        pattern2 = r'^CHI=\s*\{'
        match2 = re.search(pattern2, content, re.MULTILINE)
        
        # 方法3: 使用前后空白字符
        pattern3 = r'(?:^|\s)CHI=\s*\{'
        match3 = re.search(pattern3, content, re.MULTILINE)
        
        print(f"方法1 (\\b词边界): {'找到' if match1 else '未找到'}")
        if match1:
            print(f"  位置: {match1.start()}")
            print(f"  匹配内容: {repr(content[match1.start():match1.end()+20])}")
        
        print(f"方法2 (^行首): {'找到' if match2 else '未找到'}")
        if match2:
            print(f"  位置: {match2.start()}")
            print(f"  匹配内容: {repr(content[match2.start():match2.end()+20])}")
        
        print(f"方法3 (空白边界): {'找到' if match3 else '未找到'}")
        if match3:
            print(f"  位置: {match3.start()}")
            print(f"  匹配内容: {repr(content[match3.start():match3.end()+20])}")
        
        # 使用最可靠的方法查找CHI块
        best_match = match2 or match1 or match3
        if best_match:
            start_pos = best_match.start()
            
            # 找到CHI块的结束位置
            next_country_pattern = r'\n[A-Z]{3}=\s*\{'
            next_country_match = re.search(next_country_pattern, content[start_pos + 100:])
            
            if next_country_match:
                end_pos = start_pos + 100 + next_country_match.start()
            else:
                end_pos = len(content)
            
            chi_block = content[start_pos:end_pos]
            
            print(f"\n=== CHI块信息 ===")
            print(f"CHI块大小: {len(chi_block):,} 字符")
            print(f"CHI块位置: {start_pos}-{end_pos}")
            
            # 查找主文化
            primary_match = re.search(r'primary_culture="([^"]+)"', chi_block)
            if primary_match:
                print(f"当前主文化: {primary_match.group(1)}")
            else:
                print("当前主文化: 未找到")
            
            # 查找接受文化
            accepted_pattern = r'accepted_culture=\s*\{\s*([^}]+)\s*\}'
            accepted_match = re.search(accepted_pattern, chi_block, re.DOTALL)
            if accepted_match:
                cultures = re.findall(r'"([^"]+)"', accepted_match.group(1))
                print(f"当前接受文化: {cultures}")
            else:
                print("当前接受文化: 未找到")
            
            # 查找恶名度
            badboy_match = re.search(r'badboy=([\d.]+)', chi_block)
            if badboy_match:
                print(f"当前恶名度: {badboy_match.group(1)}")
            else:
                print("当前恶名度: 未找到")
            
            # 显示CHI块的开头部分
            print(f"\nCHI块开头100字符:")
            print(repr(chi_block[:100]))
            
        else:
            print("❌ 所有方法都未找到CHI块")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chi_block_finding()
