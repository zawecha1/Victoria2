#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 存档花括号结构解析器
===================================
精确解析Victoria II存档文件的花括号结构，确保修改在正确的范围内进行
"""

import re
from typing import Dict, List, Tuple, Optional

class BracketBlock:
    """花括号块类"""
    def __init__(self, name: str, start_pos: int, end_pos: int, content: str, level: int = 0):
        self.name = name  # 块名称，如 "CHI", "ideology", "culture" 等
        self.start_pos = start_pos  # 块开始位置（包含开始的{）
        self.end_pos = end_pos  # 块结束位置（包含结束的}）
        self.content = content  # 块内容（不包含外层花括号）
        self.level = level  # 嵌套层级
        self.children: List['BracketBlock'] = []  # 子块列表
    
    def __repr__(self):
        return f"BracketBlock(name='{self.name}', pos={self.start_pos}-{self.end_pos}, level={self.level})"

class Victoria2BracketParser:
    """Victoria II 存档花括号解析器"""
    
    def __init__(self):
        self.content = ""
        self.blocks: List[BracketBlock] = []
    
    def load_content(self, content: str):
        """加载内容"""
        self.content = content
        self.blocks = []
    
    def find_matching_brace(self, start_pos: int) -> int:
        """找到与开始花括号匹配的结束花括号位置"""
        if start_pos >= len(self.content) or self.content[start_pos] != '{':
            return -1
        
        brace_count = 1
        pos = start_pos + 1
        
        while pos < len(self.content) and brace_count > 0:
            char = self.content[pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            pos += 1
        
        return pos - 1 if brace_count == 0 else -1
    
    def extract_block_name(self, block_start: int) -> str:
        """提取块名称"""
        # 向前查找块名称（可能是 name= 或 name 的形式）
        search_start = max(0, block_start - 100)
        prefix_content = self.content[search_start:block_start]
        
        # 查找最近的标识符=或标识符{模式
        patterns = [
            r'(\w+)\s*=\s*$',  # name=
            r'(\w+)\s*$'       # name (直接跟{)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prefix_content)
            if match:
                return match.group(1)
        
        # 如果找不到，尝试从当前位置后查找
        next_content = self.content[block_start:block_start + 50]
        if next_content.startswith('{'):
            # 可能是匿名块或数组元素
            return f"block_{block_start}"
        
        return f"unknown_{block_start}"
    
    def parse_block(self, start_pos: int, level: int = 0) -> Optional[BracketBlock]:
        """解析单个花括号块"""
        if start_pos >= len(self.content) or self.content[start_pos] != '{':
            return None
        
        end_pos = self.find_matching_brace(start_pos)
        if end_pos == -1:
            return None
        
        block_name = self.extract_block_name(start_pos)
        content = self.content[start_pos + 1:end_pos]
        
        block = BracketBlock(block_name, start_pos, end_pos, content, level)
        
        # 查找子块
        pos = 0
        while pos < len(content):
            if content[pos] == '{':
                # 找到子块的绝对位置
                abs_start = start_pos + 1 + pos
                child_block = self.parse_block(abs_start, level + 1)
                if child_block:
                    block.children.append(child_block)
                    # 跳过这个子块
                    pos = child_block.end_pos - start_pos
                else:
                    pos += 1
            else:
                pos += 1
        
        return block
    
    def parse_all_blocks(self) -> List[BracketBlock]:
        """解析所有顶级花括号块"""
        self.blocks = []
        pos = 0
        
        while pos < len(self.content):
            if self.content[pos] == '{':
                block = self.parse_block(pos)
                if block:
                    self.blocks.append(block)
                    pos = block.end_pos + 1
                else:
                    pos += 1
            else:
                pos += 1
        
        return self.blocks
    
    def find_blocks_by_name(self, name: str, case_sensitive: bool = True) -> List[BracketBlock]:
        """按名称查找块"""
        result = []
        
        def search_recursive(blocks: List[BracketBlock]):
            for block in blocks:
                if case_sensitive:
                    match = block.name == name
                else:
                    match = block.name.lower() == name.lower()
                
                if match:
                    result.append(block)
                
                # 递归搜索子块
                search_recursive(block.children)
        
        search_recursive(self.blocks)
        return result
    
    def find_block_containing_position(self, position: int) -> Optional[BracketBlock]:
        """找到包含指定位置的块"""
        def search_recursive(blocks: List[BracketBlock]) -> Optional[BracketBlock]:
            for block in blocks:
                if block.start_pos <= position <= block.end_pos:
                    # 检查是否有更深层的子块包含这个位置
                    child_result = search_recursive(block.children)
                    return child_result if child_result else block
            return None
        
        return search_recursive(self.blocks)
    
    def get_block_structure(self, block: BracketBlock, indent: int = 0) -> str:
        """获取块结构的文本表示"""
        indent_str = "  " * indent
        result = f"{indent_str}{block.name} ({block.start_pos}-{block.end_pos}, level={block.level})\n"
        
        for child in block.children:
            result += self.get_block_structure(child, indent + 1)
        
        return result
    
    def analyze_content_type(self, block: BracketBlock) -> str:
        """分析块内容类型"""
        content = block.content.strip()
        
        if not content:
            return "empty"
        
        # 检查是否为键值对列表
        if re.search(r'\w+\s*=\s*[^{}\n]+', content):
            return "key_value_pairs"
        
        # 检查是否为嵌套结构
        if '{' in content and '}' in content:
            return "nested_structure"
        
        # 检查是否为数组
        if re.search(r'^\s*"[^"]+"\s*$', content, re.MULTILINE):
            return "string_array"
        
        # 检查是否为数值数组
        if re.search(r'^\s*[\d.]+\s*$', content, re.MULTILINE):
            return "numeric_array"
        
        return "mixed_content"

def test_parser():
    """测试解析器"""
    # 简单测试内容
    test_content = """
    CHI={
        primary_culture="beifaren"
        culture={
            "nanfaren"
            "manchu"
        }
        badboy=0.000
        ideology={
            1=0.5
            3=0.3
            6=0.2
        }
    }
    """
    
    parser = Victoria2BracketParser()
    parser.load_content(test_content)
    blocks = parser.parse_all_blocks()
    
    print("解析结果:")
    for block in blocks:
        print(parser.get_block_structure(block))
        print(f"内容类型: {parser.analyze_content_type(block)}")

if __name__ == "__main__":
    test_parser()
