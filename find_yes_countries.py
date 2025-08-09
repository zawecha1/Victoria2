#!/usr/bin/env python3
"""
找出哪个国家还是civilized="yes"状态
"""

import re
import os

def find_yes_countries(filename):
    """找出所有civilized="yes"的国家"""
    print(f"\n🔍 查找 {filename} 中的 civilized=\"yes\" 国家")
    
    if not os.path.exists(filename):
        print(f"❌ 文件不存在: {filename}")
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        # 更精确的模式：找到国家块中的civilized字段
        # 模式1: 查找 国家代码={}块中包含civilized="yes"的
        pattern1 = r'([A-Z]{2,3})\s*=\s*\{[^{}]*?civilized\s*=\s*"?yes"?[^{}]*?\}'
        matches1 = re.findall(pattern1, content, re.IGNORECASE | re.DOTALL)
        
        print(f"模式1找到的yes国家: {matches1}")
        
        # 模式2: 更宽松的搜索，查找civilized="yes"前后的内容
        pattern2 = r'([A-Z]{2,3})\s*=\s*\{[^{}]*?civilized\s*=\s*"?yes"?'
        matches2 = re.findall(pattern2, content, re.IGNORECASE | re.DOTALL)
        
        print(f"模式2找到的yes国家: {matches2}")
        
        # 模式3: 查找所有civilized="yes"并显示上下文
        pattern3 = r'.{0,50}civilized\s*=\s*"?yes"?.{0,50}'
        contexts = re.findall(pattern3, content, re.IGNORECASE | re.DOTALL)
        
        print(f"\n📋 所有 civilized=\"yes\" 的上下文:")
        for i, context in enumerate(contexts, 1):
            clean_context = ' '.join(context.split())  # 清理空白字符
            print(f"  {i}. {clean_context}")
        
        return matches1 if matches1 else matches2
        
    except Exception as e:
        print(f"❌ 分析文件时出错: {e}")
        return []

def main():
    """主函数"""
    print("🔍 查找civilized=\"yes\"的国家")
    print("="*60)
    
    # 检查autosave.v2中的yes国家
    yes_countries_autosave = find_yes_countries("autosave.v2")
    
    # 检查测试文件中的yes国家
    yes_countries_test = find_yes_countries("test_civilized_simple_143915.v2")
    
    print(f"\n" + "="*60)
    print("📊 总结:")
    print(f"autosave.v2 中的 yes 国家: {yes_countries_autosave}")
    print(f"测试文件中的 yes 国家: {yes_countries_test}")
    
    if yes_countries_autosave:
        print(f"\n⚠️ 问题分析:")
        print(f"autosave.v2 中还有 {len(yes_countries_autosave)} 个国家是 civilized=\"yes\"")
        for country in yes_countries_autosave:
            if country == 'CHI':
                print(f"  🇨🇳 {country}: 这是中国，应该保持yes状态 ✅")
            else:
                print(f"  🌍 {country}: 这个国家应该被改为no，但没有被修改 ❌")
    else:
        print(f"✅ autosave.v2 中没有找到 civilized=\"yes\" 的国家")

if __name__ == "__main__":
    main()
