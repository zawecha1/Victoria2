#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断人口删除问题 - 分析autosave.v2和China1844_09_16.v2的差异
"""

import re
import json
from datetime import datetime

def load_file_simple(filename):
    """加载文件"""
    try:
        with open(filename, 'r', encoding='latin1') as f:
            content = f.read()
        print(f"文件加载成功: {filename}, 大小: {len(content):,} 字符")
        return content
    except Exception as e:
        print(f"加载失败: {e}")
        return None

def analyze_population_differences(content1, content2, filename1, filename2):
    """分析人口差异"""
    print(f"\n分析 {filename1} 和 {filename2} 的人口差异...")
    
    # 人口类型
    pop_types = ['aristocrats', 'artisans', 'bureaucrats', 'capitalists', 'clergymen', 
                 'clerks', 'craftsmen', 'farmers', 'labourers', 'officers', 'soldiers']
    
    results = {
        'file1': filename1,
        'file2': filename2,
        'pop_counts': {},
        'province_analysis': [],
        'structure_issues': []
    }
    
    for pop_type in pop_types:
        # 统计每种人口类型的数量
        pattern = rf'\b{pop_type}\s*=\s*{{'
        count1 = len(re.findall(pattern, content1))
        count2 = len(re.findall(pattern, content2))
        
        results['pop_counts'][pop_type] = {
            'file1': count1,
            'file2': count2,
            'difference': count1 - count2
        }
        
        print(f"{pop_type:12}: {filename1}={count1:4}, {filename2}={count2:4}, 差异={count1-count2:4}")
    
    return results

def analyze_province_structure(content, filename):
    """分析省份结构"""
    print(f"\n分析 {filename} 的省份结构...")
    
    # 查找所有省份
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    province_info = []
    structure_issues = []
    
    for i, match in enumerate(province_matches[:50]):  # 只检查前50个省份避免太慢
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
        
        # 检查花括号平衡
        open_braces = province_content.count('{')
        close_braces = province_content.count('}')
        
        # 检查人口数量
        pop_count = 0
        pop_types = ['aristocrats', 'artisans', 'bureaucrats', 'capitalists', 'clergymen', 
                     'clerks', 'craftsmen', 'farmers', 'labourers', 'officers', 'soldiers']
        
        for pop_type in pop_types:
            pattern = rf'\b{pop_type}\s*=\s*{{'
            pop_count += len(re.findall(pattern, province_content))
        
        # 检查是否属于中国
        is_china = 'owner="CHI"' in province_content or 'owner=CHI' in province_content
        
        province_data = {
            'id': province_id,
            'is_china': is_china,
            'pop_count': pop_count,
            'open_braces': open_braces,
            'close_braces': close_braces,
            'brace_balance': open_braces - close_braces,
            'content_length': len(province_content)
        }
        
        province_info.append(province_data)
        
        # 检查结构问题
        if abs(open_braces - close_braces) > 1:  # Victoria II允许-1的差异
            structure_issues.append({
                'province_id': province_id,
                'issue': 'brace_imbalance',
                'open_braces': open_braces,
                'close_braces': close_braces,
                'difference': open_braces - close_braces
            })
    
    return province_info, structure_issues

def check_population_deletion_pattern(content1, content2):
    """检查人口删除模式"""
    print("\n检查人口删除模式...")
    
    # 查找中国省份
    china_provinces1 = []
    china_provinces2 = []
    
    # 在两个文件中查找中国省份
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    
    for match in province_pattern.finditer(content1):
        province_id = int(match.group(1))
        start_pos = match.end()
        
        # 简单地取省份开头的一部分来检查
        province_snippet = content1[start_pos:start_pos+500]
        if 'owner="CHI"' in province_snippet or 'owner=CHI' in province_snippet:
            china_provinces1.append(province_id)
    
    for match in province_pattern.finditer(content2):
        province_id = int(match.group(1))
        start_pos = match.end()
        
        province_snippet = content2[start_pos:start_pos+500]
        if 'owner="CHI"' in province_snippet or 'owner=CHI' in province_snippet:
            china_provinces2.append(province_id)
    
    print(f"文件1中国省份数量: {len(china_provinces1)}")
    print(f"文件2中国省份数量: {len(china_provinces2)}")
    
    # 检查是否有省份丢失
    lost_provinces = set(china_provinces2) - set(china_provinces1)
    if lost_provinces:
        print(f"丢失的中国省份: {sorted(lost_provinces)}")
    
    return {
        'china_provinces_file1': len(china_provinces1),
        'china_provinces_file2': len(china_provinces2),
        'lost_provinces': list(lost_provinces)
    }

def find_malformed_structures(content, filename):
    """查找格式错误的结构"""
    print(f"\n检查 {filename} 中的格式错误...")
    
    issues = []
    
    # 检查连续的花括号
    consecutive_open = re.findall(r'{{+', content)
    consecutive_close = re.findall(r'}}+', content)
    
    if consecutive_open:
        issues.append(f"发现连续开括号: {len(consecutive_open)} 处")
    
    if consecutive_close:
        issues.append(f"发现连续闭括号: {len(consecutive_close)} 处")
    
    # 检查空的人口块
    empty_pop_pattern = r'\b(aristocrats|artisans|bureaucrats|capitalists|clergymen|clerks|craftsmen|farmers|labourers|officers|soldiers)\s*=\s*{\s*}'
    empty_pops = re.findall(empty_pop_pattern, content)
    
    if empty_pops:
        issues.append(f"发现空人口块: {len(empty_pops)} 个")
    
    # 检查不完整的人口块
    incomplete_pattern = r'\b(aristocrats|artisans|bureaucrats|capitalists|clergymen|clerks|craftsmen|farmers|labourers|officers|soldiers)\s*=\s*{[^}]*$'
    incomplete_matches = re.findall(incomplete_pattern, content, re.MULTILINE)
    
    if incomplete_matches:
        issues.append(f"发现不完整的人口块: {len(incomplete_matches)} 个")
    
    return issues

def main():
    """主函数"""
    print("=" * 60)
    print("人口删除问题诊断工具")
    print("=" * 60)
    
    # 加载文件
    content1 = load_file_simple('autosave.v2')
    content2 = load_file_simple('China1844_09_16.v2')
    
    if not content1 or not content2:
        print("文件加载失败")
        return
    
    # 基本统计
    print(f"\n基本统计:")
    print(f"autosave.v2 大小: {len(content1):,} 字符")
    print(f"China1844_09_16.v2 大小: {len(content2):,} 字符")
    print(f"差异: {len(content1) - len(content2):,} 字符")
    
    # 花括号统计
    open1, close1 = content1.count('{'), content1.count('}')
    open2, close2 = content2.count('{'), content2.count('}')
    
    print(f"\n花括号统计:")
    print(f"autosave.v2: 开={open1}, 闭={close1}, 差异={open1-close1}")
    print(f"China1844_09_16.v2: 开={open2}, 闭={close2}, 差异={open2-close2}")
    
    # 分析人口差异
    pop_analysis = analyze_population_differences(content1, content2, 'autosave.v2', 'China1844_09_16.v2')
    
    # 检查人口删除模式
    deletion_pattern = check_population_deletion_pattern(content1, content2)
    
    # 查找格式错误
    issues1 = find_malformed_structures(content1, 'autosave.v2')
    issues2 = find_malformed_structures(content2, 'China1844_09_16.v2')
    
    print(f"\nautosave.v2 格式问题:")
    for issue in issues1:
        print(f"  - {issue}")
    if not issues1:
        print("  - 无明显格式问题")
    
    print(f"\nChina1844_09_16.v2 格式问题:")
    for issue in issues2:
        print(f"  - {issue}")
    if not issues2:
        print("  - 无明显格式问题")
    
    # 保存诊断报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"population_deletion_diagnosis_{timestamp}.json"
    
    diagnosis_report = {
        'timestamp': timestamp,
        'file_sizes': {
            'autosave.v2': len(content1),
            'China1844_09_16.v2': len(content2),
            'difference': len(content1) - len(content2)
        },
        'brace_counts': {
            'autosave.v2': {'open': open1, 'close': close1, 'diff': open1-close1},
            'China1844_09_16.v2': {'open': open2, 'close': close2, 'diff': open2-close2}
        },
        'population_analysis': pop_analysis,
        'deletion_pattern': deletion_pattern,
        'format_issues': {
            'autosave.v2': issues1,
            'China1844_09_16.v2': issues2
        }
    }
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(diagnosis_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n诊断报告已保存: {report_filename}")
    
    # 总结问题
    print(f"\n" + "=" * 60)
    print("问题总结")
    print("=" * 60)
    
    total_pop_lost = sum(data['difference'] for data in pop_analysis['pop_counts'].values())
    print(f"总计丢失人口单位: {-total_pop_lost} 个")
    
    if deletion_pattern['lost_provinces']:
        print(f"丢失省份: {len(deletion_pattern['lost_provinces'])} 个")
    
    if issues1:
        print(f"autosave.v2 有 {len(issues1)} 种格式问题")
    
    print("\n可能的原因:")
    print("1. 删除人口时破坏了省份结构")
    print("2. 花括号不匹配导致省份块损坏") 
    print("3. 删除范围过大，删除了非人口数据")

if __name__ == "__main__":
    main()
