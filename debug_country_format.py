#!/usr/bin/env python3
"""
调试国家块格式
"""

import re
from victoria2_main_modifier import Victoria2Modifier

def debug_country_blocks():
    """调试国家块格式"""
    print("🔍 调试国家块格式")
    print("="*60)
    
    filename = "autosave.v2"
    modifier = Victoria2Modifier(debug_mode=False)
    
    if modifier.load_file(filename):
        print("📂 文件加载成功")
        
        # 查找国家块
        country_blocks = modifier.find_blocks_by_function_type('countries')
        print(f"📊 找到 {len(country_blocks)} 个国家块")
        
        if country_blocks:
            print("\n🔍 分析前3个国家块的内容格式:")
            for i, block in enumerate(country_blocks[:3], 1):
                print(f"\n--- 国家块 {i} ---")
                print(f"块名称: '{block.name}'")
                print(f"块级别: {block.level}")
                
                # 显示前200字符内容
                content_sample = block.content[:200]
                print(f"内容开头200字符:")
                print(repr(content_sample))
                
                # 尝试各种国家标识符模式
                patterns = [
                    r'^([A-Z]{3})\s*=\s*{',  # 原模式
                    r'([A-Z]{3})\s*=\s*{',   # 不要求开头
                    r'^(\w+)\s*=\s*{',       # 任意标识符开头
                    r'(\w+)\s*=\s*{'         # 任意标识符
                ]
                
                print("尝试的模式匹配结果:")
                for j, pattern in enumerate(patterns, 1):
                    match = re.search(pattern, block.content.strip())
                    if match:
                        print(f"  模式{j}: ✅ 匹配到 '{match.group(1)}'")
                    else:
                        print(f"  模式{j}: ❌ 无匹配")
                
                # 查找civilized字段
                civilized_match = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', block.content)
                if civilized_match:
                    print(f"文明化状态: {civilized_match.group(1)}")
                else:
                    print("文明化状态: 未找到")
        
        return True
    else:
        print("❌ 文件加载失败")
        return False

if __name__ == "__main__":
    debug_country_blocks()
