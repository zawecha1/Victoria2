#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度诊断文件修改流程
"""

import re
import sys
from victoria2_main_modifier import Victoria2Modifier

def deep_diagnose_file_modification():
    """深度诊断文件修改流程"""
    
    print("🔬 深度诊断文件修改流程")
    print("=" * 50)
    
    filename = 'China1837_01_24.v2'
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=True)
    
    # 读取原始文件
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            original_content = f.read()
        print(f"✅ 原始文件读取成功，大小: {len(original_content):,} 字符")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 执行修改过程
    print("\n🔄 开始执行修改过程...")
    
    try:
        # 模拟完整的调用流程
        print("🔄 执行load_file...")
        if modifier.load_file(filename):
            print("✅ load_file成功")
            
            print("🔄 执行modify_chinese_population...")
            if modifier.modify_chinese_population():
                print(f"✅ modify_chinese_population成功 - 宗教修改: {modifier.religion_changes}, 意识形态修改: {modifier.ideology_changes}")
                
                print("🔄 执行save_file...")
                if modifier.save_file(filename):
                    print("✅ save_file成功")
                else:
                    print("❌ save_file失败")
            else:
                print("❌ modify_chinese_population失败")
        else:
            print("❌ load_file失败")
        
        print("✅ 修改函数执行完成")
        
    except Exception as e:
        print(f"❌ 修改过程失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 读取修改后的文件
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            modified_content = f.read()
        print(f"✅ 修改后文件读取成功，大小: {len(modified_content):,} 字符")
    except Exception as e:
        print(f"❌ 修改后文件读取失败: {e}")
        return
    
    # 比较文件内容
    if original_content == modified_content:
        print("❌ 文件内容完全相同，修改未生效！")
        
        # 进一步分析
        print("\n🔍 分析原因...")
        
        # 检查省份1的第一个意识形态块
        province_pattern = r'^1=\s*\{'
        province_match = re.search(province_pattern, original_content, re.MULTILINE)
        
        if province_match:
            # 提取省份内容
            start_pos = province_match.end()
            brace_count = 1
            current_pos = start_pos
            while current_pos < len(original_content) and brace_count > 0:
                char = original_content[current_pos]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                current_pos += 1
            
            province_content = original_content[start_pos:current_pos-1]
            
            # 查找意识形态块
            ideology_pattern = r'ideology=\s*\{([^}]*)\}'
            ideology_matches = list(re.finditer(ideology_pattern, province_content, re.DOTALL))
            
            if ideology_matches:
                first_match = ideology_matches[0]
                ideology_content = first_match.group(1)
                
                # 解析意识形态数据
                ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
                ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
                
                # 检查是否有旧意识形态
                old_ideologies = [1, 2, 4, 5, 7]
                old_values = {id_val: ideology_dist.get(id_val, 0) for id_val in old_ideologies}
                
                print(f"🎯 省份1第一个意识形态块的旧值: {old_values}")
                
                if any(val > 0 for val in old_values.values()):
                    print("❌ 发现旧意识形态仍有非零值，修改确实未生效")
                else:
                    print("✅ 旧意识形态已清零，修改似乎已生效")
    else:
        print("✅ 文件内容已改变，修改已生效！")
        
        # 计算差异大小
        diff_chars = sum(1 for a, b in zip(original_content, modified_content) if a != b)
        print(f"📊 差异字符数: {diff_chars:,}")
    
    print("\n📝 执行验证...")
    
    # 执行验证
    modifier.verify_ideology_modifications(filename)

if __name__ == "__main__":
    deep_diagnose_file_modification()
