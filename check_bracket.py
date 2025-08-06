#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查BracketBlock解析结果
"""

import re
from victoria2_main_modifier import Victoria2Modifier

def check_bracket_parsing():
    """检查BracketBlock解析结果"""
    
    print("🔍 检查BracketBlock解析结果")
    print("=" * 50)
    
    filename = 'China1837_01_24.v2'
    
    # 创建修改器实例
    modifier = Victoria2Modifier(debug_mode=False)  # 关闭调试模式减少输出
    
    # 只读取文件，不做完整解析
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        modifier.content = content
        print(f"✅ 文件读取成功，大小: {len(content):,}")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 查找省份1的位置
    province_pattern = r'^1=\s*{'
    province_match = re.search(province_pattern, content, re.MULTILINE)
    
    if not province_match:
        print("❌ 未找到省份1")
        return
    
    print("✅ 找到省份1")
    
    # 提取省份1的开始位置
    province_start = province_match.start()
    
    # 找到省份1的完整内容
    start_pos = province_match.end()
    brace_count = 1
    current_pos = start_pos
    while current_pos < len(content) and brace_count > 0:
        char = content[current_pos]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        current_pos += 1
    
    province_end = current_pos
    province_content = content[province_start:province_end]
    
    print(f"省份1内容长度: {len(province_content):,}")
    
    # 使用修改器的解析器解析省份1
    from bracket_parser import Victoria2BracketParser
    
    # 创建解析器
    parser = Victoria2BracketParser()
    parser.load_content(province_content)
    
    # 解析省份1的结构
    print("🔄 解析省份1的括号结构...")
    try:
        province_structure = parser.parse_block(0)  # 从位置0开始解析
        print(f"✅ 解析成功")
        print(f"子块数量: {len(province_structure.children)}")
        
        # 人口类型列表
        pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                    'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                    'bureaucrats', 'intellectuals']
        
        # 检查前10个子块
        for i, child_block in enumerate(province_structure.children[:10]):
            print(f"\n子块 {i}:")
            print(f"  位置: {child_block.start_pos} - {child_block.end_pos}")
            print(f"  长度: {len(child_block.content)}")
            
            # 显示内容的前200个字符
            content_preview = child_block.content[:200]
            print(f"  内容预览: {repr(content_preview)}")
            
            # 检查是否包含人口类型
            found_pops = [pop for pop in pop_types if pop in child_block.content]
            if found_pops:
                print(f"  ✅ 发现人口类型: {found_pops}")
            
            # 检查是否包含ideology
            if 'ideology=' in child_block.content:
                print(f"  🎭 包含ideology")
    
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_bracket_parsing()
