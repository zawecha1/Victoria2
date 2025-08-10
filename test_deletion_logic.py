#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试修复的删除逻辑
"""

import re

def test_population_block_parsing():
    """测试人口块解析逻辑"""
    
    # 模拟一个省份的人口数据
    test_province_content = '''
	owner="CHI"
	controller="CHI"
	aristocrats={
		id=2000001
		size=102.600
		beifaren=orthodox
		money=12.500
		ideology={
			reactionary=10.000
		}
		issues={
			vote_franschise=landed_voting
		}
		consciousness=0.000
		militancy=0.000
	}
	craftsmen={
		id=2000002
		size=1250.850
		irish=protestant
		money=8.900
		ideology={
			liberal=15.000
		}
		issues={
			economic_policy=interventionism
		}
		consciousness=2.100
		militancy=1.200
	}
	farmers={
		id=2000003
		size=5020.100
		beifaren=buddhist
		money=4.200
		consciousness=0.500
		militancy=0.000
	}
'''
    
    print("测试人口块解析...")
    
    pop_types = ['aristocrats', 'craftsmen', 'farmers']
    primary_culture = 'beifaren'
    accepted_cultures = ['nanfaren', 'manchu', 'yankee']
    
    for pop_type in pop_types:
        # 查找人口块开始位置
        start_pattern = rf'\b{pop_type}\s*=\s*{{'
        start_matches = list(re.finditer(start_pattern, test_province_content))
        
        for start_match in start_matches:
            print(f"\n找到 {pop_type} 块:")
            print(f"  开始位置: {start_match.start()}")
            
            # 找到完整的人口块
            brace_start = start_match.end() - 1  # '{' 的位置
            brace_count = 0
            block_end = None
            
            for i in range(brace_start, len(test_province_content)):
                char = test_province_content[i]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        block_end = i + 1
                        break
            
            if block_end is None:
                print(f"  错误: 未找到块结束")
                continue
            
            print(f"  结束位置: {block_end}")
            
            # 提取完整的人口块内容
            pop_block_content = test_province_content[start_match.start():block_end]
            
            print(f"  块长度: {len(pop_block_content)}")
            
            # 分析文化
            culture = extract_culture_from_pop_block(pop_block_content)
            print(f"  文化: {culture}")
            
            # 判断是否删除
            should_delete = culture and culture not in [primary_culture] + accepted_cultures
            print(f"  应删除: {should_delete}")
            
            # 查找完整行范围
            line_start = start_match.start()
            while line_start > 0 and test_province_content[line_start - 1] not in ['\n', '\r']:
                line_start -= 1
            
            line_end = block_end
            while line_end < len(test_province_content) and test_province_content[line_end] not in ['\n', '\r']:
                line_end += 1
            if line_end < len(test_province_content):
                line_end += 1  # 包含换行符
            
            print(f"  删除范围: {line_start} - {line_end}")
            print(f"  删除内容预览: {repr(test_province_content[line_start:min(line_start+50, line_end)])}")

def extract_culture_from_pop_block(pop_content):
    """从人口块中提取文化信息"""
    # 查找 文化名=宗教名 格式
    culture_pattern = r'\s+([a-z_]+)\s*=\s*([a-z_]+)'
    culture_matches = re.findall(culture_pattern, pop_content)
    
    # 系统字段列表
    system_fields = {
        'id', 'size', 'money', 'ideology', 'issues', 
        'consciousness', 'militancy', 'type', 'rebel'
    }
    
    for potential_culture, religion in culture_matches:
        if potential_culture not in system_fields:
            if len(potential_culture) <= 15 and potential_culture.replace('_', '').isalpha():
                return potential_culture
    
    return None

def test_deletion_logic():
    """测试删除逻辑"""
    
    test_content = '''province_start
	aristocrats={
		id=1
		size=100
		irish=catholic
		money=10
	}
	craftsmen={
		id=2
		size=200
		beifaren=buddhist
		money=20
	}
	farmers={
		id=3
		size=300
		yankee=protestant
		money=15
	}
province_end'''
    
    print("\n" + "=" * 50)
    print("测试删除逻辑")
    print("=" * 50)
    
    print("原始内容:")
    print(test_content)
    print(f"原始长度: {len(test_content)}")
    
    # 查找要删除的irish人口
    pop_pattern = r'\baristocrats\s*=\s*{'
    match = re.search(pop_pattern, test_content)
    
    if match:
        # 找到完整块
        brace_start = match.end() - 1
        brace_count = 0
        block_end = None
        
        for i in range(brace_start, len(test_content)):
            char = test_content[i]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    block_end = i + 1
                    break
        
        if block_end:
            # 查找行边界
            line_start = match.start()
            while line_start > 0 and test_content[line_start - 1] not in ['\n', '\r']:
                line_start -= 1
            
            line_end = block_end
            while line_end < len(test_content) and test_content[line_end] not in ['\n', '\r']:
                line_end += 1
            if line_end < len(test_content):
                line_end += 1
            
            print(f"\n删除范围: {line_start} - {line_end}")
            print(f"删除内容: {repr(test_content[line_start:line_end])}")
            
            # 执行删除
            modified_content = test_content[:line_start] + test_content[line_end:]
            
            print(f"\n修改后内容:")
            print(modified_content)
            print(f"修改后长度: {len(modified_content)}")
            print(f"删除了 {len(test_content) - len(modified_content)} 个字符")

if __name__ == "__main__":
    test_population_block_parsing()
    test_deletion_logic()
