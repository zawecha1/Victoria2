#!/usr/bin/env python3
"""
直接使用正则表达式查找国家块
"""

import re

def find_countries_with_regex():
    """使用正则表达式直接查找国家块"""
    print("🔍 使用正则表达式查找国家块")
    print("="*60)
    
    filename = "autosave.v2"
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        print(f"📂 文件读取成功，大小: {len(content):,} 字符")
        
        # 查找国家块的几种模式
        patterns = [
            # 模式1: 三字母国家代码后跟等号和花括号
            r'([A-Z]{3})\s*=\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*civilized\s*=[^}]*\}',
            # 模式2: 更宽松的国家代码匹配
            r'(\w{2,3})\s*=\s*\{[^{}]*civilized\s*=[^}]*\}',
        ]
        
        for i, pattern in enumerate(patterns, 1):
            print(f"\n🔍 尝试模式 {i}...")
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            print(f"  找到 {len(matches)} 个潜在国家")
            if matches:
                print(f"  前10个: {matches[:10]}")
        
        # 更简单的方法：直接查找 civilized 字段
        print(f"\n📊 统计 civilized 字段:")
        civilized_yes = len(re.findall(r'civilized\s*=\s*"?yes"?', content, re.IGNORECASE))
        civilized_no = len(re.findall(r'civilized\s*=\s*"?no"?', content, re.IGNORECASE))
        
        print(f"  civilized=yes: {civilized_yes}")
        print(f"  civilized=no: {civilized_no}")
        print(f"  总计: {civilized_yes + civilized_no}")
        
        # 查找国家块的更准确模式
        print(f"\n🌍 查找完整国家块:")
        # 这个模式查找包含关键国家字段的块
        country_pattern = r'([A-Z]{2,3})\s*=\s*\{[^{}]*(?:primary_culture|capital|government|civilized)[^{}]*\}'
        countries = re.findall(country_pattern, content, re.IGNORECASE | re.DOTALL)
        print(f"  找到 {len(countries)} 个国家块")
        if countries:
            print(f"  国家列表: {countries[:20]}...")  # 显示前20个
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    find_countries_with_regex()
