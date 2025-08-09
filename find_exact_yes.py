#!/usr/bin/env python3
"""
直接找出civilized="yes"的确切位置
"""

import re
import os

def find_exact_yes_location():
    """找出确切的civilized="yes"位置"""
    print("🔍 直接查找 civilized=\"yes\" 的确切位置")
    print("="*60)
    
    filename = "autosave.v2"
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        # 查找所有civilized="yes"的位置
        pattern = r'civilized\s*=\s*"?yes"?'
        matches = []
        
        for match in re.finditer(pattern, content, re.IGNORECASE):
            start = match.start()
            end = match.end()
            
            # 获取前后500字符的上下文
            context_start = max(0, start - 500)
            context_end = min(len(content), end + 500)
            context = content[context_start:context_end]
            
            matches.append({
                'position': start,
                'matched_text': match.group(),
                'context': context
            })
        
        print(f"📊 找到 {len(matches)} 个 civilized=\"yes\"")
        
        for i, match in enumerate(matches, 1):
            print(f"\n🎯 匹配 {i}:")
            print(f"  位置: {match['position']}")
            print(f"  匹配文本: '{match['matched_text']}'")
            print(f"  上下文 (前后500字符):")
            
            # 清理上下文以便阅读
            clean_context = ' '.join(match['context'].split())
            
            # 在匹配的词周围添加标记
            highlighted = clean_context.replace(
                match['matched_text'], 
                f">>>{match['matched_text']}<<<", 
                1
            )
            
            print(f"  {highlighted[:1000]}...")  # 只显示前1000字符
            
            # 尝试从上下文中找出国家标识符
            country_patterns = [
                r'([A-Z]{3})\s*=\s*\{[^{}]*civilized',
                r'([A-Z]{2,3})\s*=\s*\{[^{}]*civilized',
                r'tag\s*=\s*([A-Z]{3})',
                r'tag\s*=\s*"([A-Z]{3})"'
            ]
            
            found_country = None
            for pattern in country_patterns:
                country_match = re.search(pattern, match['context'], re.IGNORECASE)
                if country_match:
                    found_country = country_match.group(1)
                    break
            
            if found_country:
                print(f"  🌍 可能的国家: {found_country}")
                if found_country == 'CHI':
                    print(f"    🇨🇳 这是中国！应该保持civilized=\"yes\" ✅")
                else:
                    print(f"    ⚠️ 这不是中国，可能需要修改为\"no\"")
            else:
                print(f"  ❓ 无法确定国家标识符")
        
        return matches
        
    except Exception as e:
        print(f"❌ 查找过程中出错: {e}")
        return []

if __name__ == "__main__":
    find_exact_yes_location()
