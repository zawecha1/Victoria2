#!/usr/bin/env python3
"""
检查中国文明化状态
"""

import re

def check_china_status():
    """检查中国的文明化状态"""
    files = [
        'autosave.v2',
        'autosave_china_civilized_160040.v2'
    ]
    
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            print(f"\n📄 {filename}:")
            
            # 查找中国块
            chi_pattern = r'CHI\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
            chi_match = re.search(chi_pattern, content, re.DOTALL)
            
            if chi_match:
                chi_content = chi_match.group(1)
                
                # 查找civilized字段
                civilized_match = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', chi_content)
                if civilized_match:
                    status = civilized_match.group(1)
                    print(f"  🇨🇳 civilized={status}")
                else:
                    print(f"  ❌ 未找到civilized字段")
            else:
                print(f"  ❌ 未找到中国块")
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")

if __name__ == "__main__":
    check_china_status()
