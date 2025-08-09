#!/usr/bin/env python3
"""
获取civilized=yes周围更大范围的上下文
"""

import re
import os

def get_large_context():
    """获取更大范围的上下文"""
    print("🔍 获取 civilized=\"yes\" 周围更大范围的上下文")
    print("="*80)
    
    filename = "autosave.v2"
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        # 查找civilized="yes"的位置
        pattern = r'civilized\s*=\s*"?yes"?'
        match = re.search(pattern, content, re.IGNORECASE)
        
        if match:
            start = match.start()
            
            # 获取前后2000字符的上下文
            context_start = max(0, start - 2000)
            context_end = min(len(content), start + 2000)
            context = content[context_start:context_end]
            
            print(f"📍 找到位置: {start}")
            print(f"📖 上下文 (前后2000字符):")
            print("="*80)
            
            # 将匹配的部分高亮显示
            highlighted = context.replace(match.group(), f">>>{match.group()}<<<")
            print(highlighted)
            print("="*80)
            
            # 在更大范围内寻找国家标识符
            # 向前查找最近的国家块开始
            before_context = content[max(0, start - 5000):start]
            after_context = content[start:min(len(content), start + 1000)]
            
            # 查找国家块模式
            country_patterns = [
                r'([A-Z]{2,3})\s*=\s*\{[^{}]*$',  # 在before_context的末尾
                r'^[^{}]*([A-Z]{2,3})\s*=\s*\{',  # 在after_context的开始
                r'([A-Z]{2,3})\s*=\s*\{',         # 任何位置
            ]
            
            print(f"\n🔍 在更大范围内查找国家标识符:")
            
            # 在前面的内容中查找
            print(f"📄 前5000字符中的国家块:")
            country_matches = re.findall(r'([A-Z]{2,3})\s*=\s*\{', before_context)
            if country_matches:
                print(f"  找到的国家: {country_matches[-5:]}")  # 显示最后5个
                likely_country = country_matches[-1]  # 最接近的国家
                print(f"  🎯 最可能的国家: {likely_country}")
                if likely_country == 'CHI':
                    print(f"    🇨🇳 这是中国！保持 civilized=\"yes\" 是正确的 ✅")
                else:
                    print(f"    ⚠️ 这不是中国，可能有问题")
            else:
                print(f"  ❌ 未找到国家标识符")
            
            # 搜索特定的中国相关关键词
            print(f"\n🔍 查找中国相关关键词:")
            china_keywords = ['CHI', 'beifaren', 'nanfaren', 'manchu', 'beijing', 'chinese']
            found_keywords = []
            
            full_context = content[max(0, start - 3000):min(len(content), start + 1000)]
            for keyword in china_keywords:
                if keyword in full_context.lower():
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"  找到中国相关关键词: {found_keywords}")
                print(f"  🇨🇳 这很可能是中国的国家块 ✅")
            else:
                print(f"  ❌ 未找到中国相关关键词")
                
        else:
            print(f"❌ 未找到 civilized=\"yes\"")
            
    except Exception as e:
        print(f"❌ 查找过程中出错: {e}")

if __name__ == "__main__":
    get_large_context()
