#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理loyalty_value中的重复值问题
"""

import re

def fix_duplicate_loyalty_values(filename):
    """修复loyalty_value中的重复数字问题"""
    print("🔧 清理loyalty_value中的重复值...")
    
    # 读取文件
    with open(filename, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    print(f"📁 原始文件大小: {len(content):,} 字符")
    
    # 查找所有有问题的loyalty_value
    problem_pattern = r'loyalty_value=(\d+\.\d+)(\.\d+)+'
    problem_matches = list(re.finditer(problem_pattern, content))
    
    print(f"🔍 找到 {len(problem_matches)} 个有问题的loyalty_value")
    
    if problem_matches:
        print("📝 示例问题值:")
        for i, match in enumerate(problem_matches[:5]):  # 显示前5个
            print(f"  {i+1}. {match.group(0)}")
        if len(problem_matches) > 5:
            print(f"  ... 还有 {len(problem_matches) - 5} 个")
    
    # 修复：将重复的数字替换为单一值
    def fix_loyalty_value(match):
        full_match = match.group(0)
        first_value = match.group(1)
        
        # 判断应该是什么值
        if "10.00000" in full_match:
            return "loyalty_value=10.00000"
        elif "0.00000" in full_match:
            return "loyalty_value=0.00000"
        else:
            # 使用第一个值
            return f"loyalty_value={first_value}"
    
    # 执行替换
    new_content = re.sub(problem_pattern, fix_loyalty_value, content)
    
    # 检查是否有其他异常模式
    extreme_pattern = r'loyalty_value=[\d.]{20,}'  # 超长数字
    extreme_matches = list(re.finditer(extreme_pattern, new_content))
    
    if extreme_matches:
        print(f"⚠️ 发现 {len(extreme_matches)} 个异常长的loyalty_value")
        # 简单替换为10.0
        new_content = re.sub(extreme_pattern, 'loyalty_value=10.00000', new_content)
    
    # 保存文件
    with open(filename, 'w', encoding='utf-8-sig') as f:
        f.write(new_content)
    
    print(f"📁 修复后文件大小: {len(new_content):,} 字符")
    print(f"💾 文件已保存: {filename}")
    
    return len(problem_matches) + len(extreme_matches)

if __name__ == "__main__":
    filename = "China1837_01_24.v2"
    
    print("🔧 开始清理loyalty_value重复值问题...")
    fixed_count = fix_duplicate_loyalty_values(filename)
    
    if fixed_count > 0:
        print(f"\n✅ 清理完成! 修复了 {fixed_count} 个问题值")
    else:
        print(f"\n✅ 没有发现问题值")
