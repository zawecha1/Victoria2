#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版中国人口清理工具 - 正确删除非主流文化人口
"""

import os
import re
import json
from datetime import datetime

def load_file_simple(filename):
    """简单文件加载"""
    encodings = ['latin1', 'utf-8', 'utf-8-sig']
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"文件加载成功 (编码: {encoding}), 大小: {len(content):,} 字符")
            return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"加载失败: {e}")
            return None
    return None

def analyze_china_culture_settings(content):
    """分析中国的文化设置"""
    print("分析中国的文化设置...")
    
    # 查找中国国家块
    china_pattern = re.compile(r'^CHI=\s*{', re.MULTILINE)
    china_match = china_pattern.search(content)
    
    if not china_match:
        print("错误: 未找到中国国家数据")
        return None, None
    
    start_pos = china_match.end()
    
    # 找到中国块的结束位置
    next_country = re.search(r'\n[A-Z]{2,3}=\s*{', content[start_pos:start_pos+500000])
    if next_country:
        end_pos = start_pos + next_country.start()
    else:
        next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+500000])
        if next_section:
            end_pos = start_pos + next_section.start()
        else:
            end_pos = start_pos + 400000
    
    china_content = content[start_pos:end_pos]
    
    # 提取主流文化
    primary_culture = None
    primary_culture_match = re.search(r'primary_culture\s*=\s*"([a-z_]+)"', china_content)
    if primary_culture_match:
        primary_culture = primary_culture_match.group(1)
    
    # 提取可接受文化
    accepted_cultures = []
    culture_block_match = re.search(r'culture\s*=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', china_content, re.DOTALL)
    if culture_block_match:
        culture_block_content = culture_block_match.group(1)
        culture_names = re.findall(r'"([a-z_]+)"', culture_block_content)
        
        for culture in culture_names:
            if culture != "noculture" and culture != primary_culture:
                accepted_cultures.append(culture)
    
    if not primary_culture:
        print("警告: 未找到主流文化，使用默认值 'beifaren'")
        primary_culture = 'beifaren'
    
    print(f"中国主流文化: {primary_culture}")
    print(f"中国可接受文化: {accepted_cultures}")
    
    return primary_culture, accepted_cultures

def find_china_provinces(content):
    """找到中国拥有的所有省份"""
    print("查找中国拥有的省份...")
    
    china_provinces = []
    
    # 查找所有省份
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    print(f"扫描 {len(province_matches)} 个省份...")
    
    for i, match in enumerate(province_matches):
        province_id = int(match.group(1))
        start_pos = match.end()
        
        # 确定省份块结束位置
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+20000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 10000
        
        province_content = content[start_pos:end_pos]
        
        # 检查是否属于中国
        owner_match = re.search(r'owner="?CHI"?', province_content)
        if owner_match:
            name_match = re.search(r'name="([^"]+)"', province_content)
            province_name = name_match.group(1) if name_match else f"Province_{province_id}"
            china_provinces.append({
                'id': province_id,
                'name': province_name,
                'start': start_pos,
                'end': end_pos,
                'global_start': match.start(),  # 记录全局开始位置
                'global_end': end_pos
            })
        
        if (i + 1) % 500 == 0:
            print(f"  进度: {i + 1}/{len(province_matches)}")
    
    print(f"找到中国省份: {len(china_provinces)} 个")
    return china_provinces

def find_population_blocks_to_remove(province_content, primary_culture, accepted_cultures):
    """查找省份中需要删除的人口块 - 改进版"""
    population_data = {
        'total_pops': 0,
        'kept_pops': 0,
        'removed_pops': 0,
        'removed_blocks': []  # 存储完整的删除信息
    }
    
    pop_types = ['aristocrats', 'artisans', 'bureaucrats', 'capitalists', 'clergymen', 
                 'clerks', 'craftsmen', 'farmers', 'labourers', 'officers', 'soldiers']
    
    for pop_type in pop_types:
        # 查找人口块开始位置
        start_pattern = rf'\b{pop_type}\s*=\s*{{'
        start_matches = list(re.finditer(start_pattern, province_content))
        
        for start_match in start_matches:
            # 找到完整的人口块
            brace_start = start_match.end() - 1  # '{' 的位置
            brace_count = 0
            block_end = None
            
            for i in range(brace_start, len(province_content)):
                char = province_content[i]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        block_end = i + 1
                        break
            
            if block_end is None:
                continue  # 跳过不完整的块
            
            # 提取完整的人口块内容
            pop_block_content = province_content[start_match.start():block_end]
            population_data['total_pops'] += 1
            
            # 分析文化
            culture = extract_culture_from_pop_block(pop_block_content)
            
            if culture and (culture == primary_culture or culture in accepted_cultures):
                population_data['kept_pops'] += 1
            else:
                population_data['removed_pops'] += 1
                
                # 记录详细的删除信息
                size_match = re.search(r'\bsize\s*=\s*([0-9.]+)', pop_block_content)
                size = float(size_match.group(1)) if size_match else 0
                
                # 查找完整行的开始和结束
                line_start = start_match.start()
                while line_start > 0 and province_content[line_start - 1] not in ['\n', '\r']:
                    line_start -= 1
                
                # 查找下一行的开始
                line_end = block_end
                while line_end < len(province_content) and province_content[line_end] not in ['\n', '\r']:
                    line_end += 1
                if line_end < len(province_content):
                    line_end += 1  # 包含换行符
                
                population_data['removed_blocks'].append({
                    'type': pop_type,
                    'culture': culture or 'unknown',
                    'size': size,
                    'line_start': line_start,
                    'line_end': line_end,
                    'block_start': start_match.start(),
                    'block_end': block_end,
                    'content': pop_block_content
                })
    
    return population_data

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

def plan_population_cleanup_improved(content, china_provinces, primary_culture, accepted_cultures):
    """改进的人口清理规划"""
    print("规划人口清理方案（改进版）...")
    
    cleanup_plan = {
        'provinces_affected': 0,
        'total_pops_removed': 0,
        'total_population_size_removed': 0,
        'province_modifications': [],
        'summary': {
            'by_culture': {},
            'by_pop_type': {}
        }
    }
    
    for province in china_provinces:
        province_id = province['id']
        province_name = province['name']
        province_start = province['start']
        province_end = province['end']
        global_province_start = province['global_start']
        
        province_content = content[province_start:province_end]
        
        # 分析省份人口
        pop_data = find_population_blocks_to_remove(province_content, primary_culture, accepted_cultures)
        
        if pop_data['removed_pops'] > 0:
            cleanup_plan['provinces_affected'] += 1
            cleanup_plan['total_pops_removed'] += pop_data['removed_pops']
            
            # 转换为全局位置
            global_removals = []
            for block in pop_data['removed_blocks']:
                cleanup_plan['total_population_size_removed'] += block['size']
                
                # 统计
                culture = block['culture']
                if culture not in cleanup_plan['summary']['by_culture']:
                    cleanup_plan['summary']['by_culture'][culture] = 0
                cleanup_plan['summary']['by_culture'][culture] += 1
                
                pop_type = block['type']
                if pop_type not in cleanup_plan['summary']['by_pop_type']:
                    cleanup_plan['summary']['by_pop_type'][pop_type] = 0
                cleanup_plan['summary']['by_pop_type'][pop_type] += 1
                
                global_removals.append({
                    'pop_type': pop_type,
                    'culture': culture,
                    'size': block['size'],
                    'global_line_start': global_province_start + block['line_start'],
                    'global_line_end': global_province_start + block['line_end'],
                    'content': block['content']
                })
            
            cleanup_plan['province_modifications'].append({
                'province_id': province_id,
                'province_name': province_name,
                'removals': global_removals
            })
    
    print(f"规划完成: {cleanup_plan['provinces_affected']} 个省份需要清理")
    print(f"将删除 {cleanup_plan['total_pops_removed']} 个人口单位")
    return cleanup_plan

def execute_population_cleanup_improved(content, cleanup_plan):
    """改进的人口清理执行"""
    print("\n开始执行人口清理（改进版）...")
    
    # 收集所有删除操作并按位置排序
    all_removals = []
    for province_mod in cleanup_plan['province_modifications']:
        all_removals.extend(province_mod['removals'])
    
    # 按全局位置从后往前排序，避免位置偏移
    all_removals.sort(key=lambda x: x['global_line_start'], reverse=True)
    
    print(f"准备删除 {len(all_removals)} 个人口单位...")
    
    modified_content = content
    total_removed = 0
    
    for i, removal in enumerate(all_removals):
        start_pos = removal['global_line_start']
        end_pos = removal['global_line_end']
        
        # 验证删除内容
        to_delete = modified_content[start_pos:end_pos]
        expected_type = removal['pop_type']
        
        if expected_type not in to_delete:
            print(f"警告: 删除位置不匹配 {expected_type} at {start_pos}-{end_pos}")
            continue
        
        # 执行删除
        modified_content = modified_content[:start_pos] + modified_content[end_pos:]
        total_removed += 1
        
        if (i + 1) % 100 == 0:
            print(f"  进度: {i + 1}/{len(all_removals)}")
    
    print(f"完成! 删除了 {total_removed} 个人口单位")
    return modified_content

def check_bracket_balance(content):
    """检查花括号平衡"""
    open_count = content.count('{')
    close_count = content.count('}')
    difference = open_count - close_count
    
    print(f"花括号检查: 开={open_count}, 闭={close_count}, 差异={difference}")
    return difference == -1

def save_modified_file(filename, content, cleanup_plan):
    """保存修改后的文件"""
    # 检查花括号平衡
    if not check_bracket_balance(content):
        print("错误: 花括号不平衡，拒绝保存!")
        return False
    
    # 创建备份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"{filename}.backup_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(filename, backup_filename)
        print(f"备份创建成功: {backup_filename}")
    except Exception as e:
        print(f"备份创建失败: {e}")
        return False
    
    try:
        # 保存修改后的文件
        with open(filename, 'w', encoding='latin1') as f:
            f.write(content)
        
        print(f"文件保存成功: {filename}")
        return True
        
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def test_on_backup_file():
    """在备份文件上测试新的删除逻辑"""
    print("=" * 60)
    print("测试改进的人口删除逻辑")
    print("=" * 60)
    
    # 使用正确的备份文件
    filename = 'China1844_09_16.v2'
    
    if not os.path.exists(filename):
        print(f"错误: 未找到文件 {filename}")
        return
    
    # 加载文件
    print(f"加载文件: {filename}")
    content = load_file_simple(filename)
    if not content:
        print("文件加载失败")
        return
    
    # 分析中国文化设置
    primary_culture, accepted_cultures = analyze_china_culture_settings(content)
    if not primary_culture:
        print("无法分析中国文化设置，退出程序")
        return
    
    # 查找中国省份
    china_provinces = find_china_provinces(content)
    if not china_provinces:
        print("未找到中国省份，退出程序")
        return
    
    # 规划清理方案
    cleanup_plan = plan_population_cleanup_improved(content, china_provinces, primary_culture, accepted_cultures)
    
    # 显示方案概述
    print(f"\n清理方案概述:")
    print(f"受影响省份: {cleanup_plan['provinces_affected']} 个")
    print(f"删除人口单位: {cleanup_plan['total_pops_removed']} 个")
    print(f"删除人口总数: {cleanup_plan['total_population_size_removed']:.0f}")
    
    # 询问是否测试执行
    confirm = input("\n是否在测试文件上执行删除？(yes/no): ").strip().lower()
    if confirm in ['yes', 'y']:
        # 创建测试文件
        test_filename = f"test_fixed_population_{datetime.now().strftime('%Y%m%d_%H%M%S')}.v2"
        
        print(f"\n执行人口清理...")
        modified_content = execute_population_cleanup_improved(content, cleanup_plan)
        
        # 保存测试文件
        try:
            with open(test_filename, 'w', encoding='latin1') as f:
                f.write(modified_content)
            print(f"测试文件已保存: {test_filename}")
            
            # 检查结果
            print(f"\n结果检查:")
            print(f"原始文件大小: {len(content):,} 字符")
            print(f"修改后大小: {len(modified_content):,} 字符")
            print(f"差异: {len(content) - len(modified_content):,} 字符")
            
            # 检查花括号
            orig_open = content.count('{')
            orig_close = content.count('}')
            new_open = modified_content.count('{')
            new_close = modified_content.count('}')
            
            print(f"原始花括号: 开={orig_open}, 闭={orig_close}, 差异={orig_open-orig_close}")
            print(f"修改后花括号: 开={new_open}, 闭={new_close}, 差异={new_open-new_close}")
            
            print(f"\n测试完成！请在游戏中测试加载 {test_filename}")
            
        except Exception as e:
            print(f"保存测试文件失败: {e}")
    else:
        print("测试取消")

if __name__ == "__main__":
    test_on_backup_file()
