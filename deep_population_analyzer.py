#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度检查人口删除结果 - 验证删除是否完全且正确
检查国家级别的人口数据和可能的引用
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

def extract_china_population_blocks(content):
    """提取中国国家级别的人口数据块"""
    print("提取中国国家级别的人口数据...")
    
    # 查找中国国家块
    china_pattern = re.compile(r'^CHI=\s*{', re.MULTILINE)
    china_match = china_pattern.search(content)
    
    if not china_match:
        print("错误: 未找到中国国家数据")
        return {}
    
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
    
    # 查找各种人口相关的数据块
    population_blocks = {}
    
    # 1. 查找 pops={ ... } 块
    pops_match = re.search(r'pops\s*=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', china_content, re.DOTALL)
    if pops_match:
        population_blocks['pops'] = pops_match.group(1)
    
    # 2. 查找 demographics={ ... } 块  
    demo_match = re.search(r'demographics\s*=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', china_content, re.DOTALL)
    if demo_match:
        population_blocks['demographics'] = demo_match.group(1)
    
    # 3. 查找 pop_types={ ... } 块
    pop_types_match = re.search(r'pop_types\s*=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', china_content, re.DOTALL)
    if pop_types_match:
        population_blocks['pop_types'] = pop_types_match.group(1)
    
    # 4. 查找 culture_pop_count={ ... } 块
    culture_pop_match = re.search(r'culture_pop_count\s*=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', china_content, re.DOTALL)
    if culture_pop_match:
        population_blocks['culture_pop_count'] = culture_pop_match.group(1)
    
    # 5. 查找任何包含人口ID的引用
    pop_id_refs = re.findall(r'id\s*=\s*(\d+)', china_content)
    if pop_id_refs:
        population_blocks['pop_id_references'] = pop_id_refs
    
    print(f"找到的人口数据块: {list(population_blocks.keys())}")
    return population_blocks

def analyze_province_population_references(content, china_provinces_sample=50):
    """分析省份中的人口引用和ID"""
    print(f"分析省份人口引用（采样前{china_provinces_sample}个中国省份）...")
    
    # 查找中国省份
    china_provinces = []
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    for i, match in enumerate(province_matches):
        if len(china_provinces) >= china_provinces_sample:
            break
            
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
        if 'owner="CHI"' in province_content or 'owner=CHI' in province_content:
            china_provinces.append({
                'id': province_id,
                'start': start_pos,
                'end': end_pos,
                'content': province_content
            })
    
    print(f"分析 {len(china_provinces)} 个中国省份的人口数据...")
    
    province_pop_data = {}
    all_pop_ids = set()
    culture_distribution = {}
    
    pop_types = ['aristocrats', 'artisans', 'bureaucrats', 'capitalists', 'clergymen', 
                 'clerks', 'craftsmen', 'farmers', 'labourers', 'officers', 'soldiers']
    
    for province in china_provinces:
        province_id = province['id']
        province_content = province['content']
        
        province_pops = []
        
        for pop_type in pop_types:
            # 查找人口块
            start_pattern = rf'\b{pop_type}\s*=\s*{{'
            start_matches = list(re.finditer(start_pattern, province_content))
            
            for start_match in start_matches:
                # 找到完整的人口块
                brace_start = start_match.end() - 1
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
                    continue
                
                pop_block = province_content[start_match.start():block_end]
                
                # 提取人口信息
                pop_info = {
                    'type': pop_type,
                    'block': pop_block
                }
                
                # 提取ID
                id_match = re.search(r'id\s*=\s*(\d+)', pop_block)
                if id_match:
                    pop_id = id_match.group(1)
                    pop_info['id'] = pop_id
                    all_pop_ids.add(pop_id)
                
                # 提取文化
                culture_pattern = r'\s+([a-z_]+)\s*=\s*([a-z_]+)'
                culture_matches = re.findall(culture_pattern, pop_block)
                system_fields = {'id', 'size', 'money', 'ideology', 'issues', 
                               'consciousness', 'militancy', 'type', 'rebel'}
                
                for potential_culture, religion in culture_matches:
                    if potential_culture not in system_fields:
                        if len(potential_culture) <= 15 and potential_culture.replace('_', '').isalpha():
                            pop_info['culture'] = potential_culture
                            
                            if potential_culture not in culture_distribution:
                                culture_distribution[potential_culture] = 0
                            culture_distribution[potential_culture] += 1
                            break
                
                # 提取size
                size_match = re.search(r'size\s*=\s*([0-9.]+)', pop_block)
                if size_match:
                    pop_info['size'] = float(size_match.group(1))
                
                province_pops.append(pop_info)
        
        if province_pops:
            province_pop_data[province_id] = province_pops
    
    return {
        'province_populations': province_pop_data,
        'all_pop_ids': all_pop_ids,
        'culture_distribution': culture_distribution,
        'total_provinces_analyzed': len(china_provinces)
    }

def compare_population_data(original_file, modified_file):
    """比较两个文件的人口数据"""
    print("=" * 70)
    print("深度人口数据比较分析")
    print("=" * 70)
    
    # 加载文件
    original_content = load_file_simple(original_file)
    modified_content = load_file_simple(modified_file)
    
    if not original_content or not modified_content:
        print("文件加载失败")
        return
    
    print(f"\n原始文件 ({original_file}):")
    print(f"  文件大小: {len(original_content):,} 字符")
    
    print(f"\n修改文件 ({modified_file}):")
    print(f"  文件大小: {len(modified_content):,} 字符")
    print(f"  大小差异: {len(original_content) - len(modified_content):,} 字符")
    
    # 1. 提取国家级人口数据块
    print("\n" + "=" * 50)
    print("1. 国家级人口数据块比较")
    print("=" * 50)
    
    original_blocks = extract_china_population_blocks(original_content)
    modified_blocks = extract_china_population_blocks(modified_content)
    
    for block_type in ['pops', 'demographics', 'culture_pop_count', 'pop_types']:
        if block_type in original_blocks and block_type in modified_blocks:
            orig_size = len(original_blocks[block_type])
            mod_size = len(modified_blocks[block_type])
            print(f"{block_type:20}: 原始={orig_size:6}, 修改={mod_size:6}, 差异={orig_size-mod_size:6}")
        elif block_type in original_blocks:
            print(f"{block_type:20}: 原始={len(original_blocks[block_type]):6}, 修改=  缺失")
        elif block_type in modified_blocks:
            print(f"{block_type:20}: 原始=  缺失, 修改={len(modified_blocks[block_type]):6}")
    
    # 2. 分析省份级人口数据
    print("\n" + "=" * 50)
    print("2. 省份级人口数据分析")
    print("=" * 50)
    
    original_prov_data = analyze_province_population_references(original_content)
    modified_prov_data = analyze_province_population_references(modified_content)
    
    print(f"\n原始文件省份人口统计:")
    print(f"  分析省份数: {original_prov_data['total_provinces_analyzed']}")
    print(f"  人口ID数量: {len(original_prov_data['all_pop_ids'])}")
    print(f"  文化种类数: {len(original_prov_data['culture_distribution'])}")
    
    print(f"\n修改文件省份人口统计:")
    print(f"  分析省份数: {modified_prov_data['total_provinces_analyzed']}")
    print(f"  人口ID数量: {len(modified_prov_data['all_pop_ids'])}")
    print(f"  文化种类数: {len(modified_prov_data['culture_distribution'])}")
    
    # 3. 文化分布比较
    print(f"\n文化分布比较 (前15个):")
    print(f"{'文化':<15} {'原始':<8} {'修改':<8} {'差异':<8}")
    print("-" * 45)
    
    all_cultures = set(original_prov_data['culture_distribution'].keys()) | \
                   set(modified_prov_data['culture_distribution'].keys())
    
    culture_diffs = []
    for culture in all_cultures:
        orig_count = original_prov_data['culture_distribution'].get(culture, 0)
        mod_count = modified_prov_data['culture_distribution'].get(culture, 0)
        diff = orig_count - mod_count
        culture_diffs.append((culture, orig_count, mod_count, diff))
    
    # 按差异排序，显示前15个
    culture_diffs.sort(key=lambda x: abs(x[3]), reverse=True)
    for culture, orig, mod, diff in culture_diffs[:15]:
        print(f"{culture:<15} {orig:<8} {mod:<8} {diff:<8}")
    
    # 4. 人口ID引用检查
    print(f"\n" + "=" * 50)
    print("3. 人口ID引用完整性检查")
    print("=" * 50)
    
    original_ids = original_prov_data['all_pop_ids']
    modified_ids = modified_prov_data['all_pop_ids']
    
    lost_ids = original_ids - modified_ids
    new_ids = modified_ids - original_ids
    
    print(f"人口ID变化:")
    print(f"  原始ID数量: {len(original_ids)}")
    print(f"  修改ID数量: {len(modified_ids)}")
    print(f"  丢失ID数量: {len(lost_ids)}")
    print(f"  新增ID数量: {len(new_ids)}")
    
    if lost_ids:
        print(f"\n丢失的人口ID (前20个): {sorted(list(lost_ids))[:20]}")
    
    # 5. 检查国家级数据中的ID引用
    print(f"\n" + "=" * 50)
    print("4. 国家级数据中的人口ID引用检查")
    print("=" * 50)
    
    if 'pop_id_references' in original_blocks:
        orig_country_ids = set(original_blocks['pop_id_references'])
        print(f"原始文件国家级引用ID数量: {len(orig_country_ids)}")
    else:
        orig_country_ids = set()
        print("原始文件未找到国家级人口ID引用")
    
    if 'pop_id_references' in modified_blocks:
        mod_country_ids = set(modified_blocks['pop_id_references'])
        print(f"修改文件国家级引用ID数量: {len(mod_country_ids)}")
    else:
        mod_country_ids = set()
        print("修改文件未找到国家级人口ID引用")
    
    # 检查是否有孤立的引用
    orphaned_refs_orig = orig_country_ids - original_ids
    orphaned_refs_mod = mod_country_ids - modified_ids
    
    if orphaned_refs_orig:
        print(f"原始文件中孤立的引用 (国家级引用但省份中不存在): {len(orphaned_refs_orig)} 个")
    
    if orphaned_refs_mod:
        print(f"修改文件中孤立的引用 (国家级引用但省份中不存在): {len(orphaned_refs_mod)} 个")
        print(f"孤立引用示例: {sorted(list(orphaned_refs_mod))[:10]}")
    
    # 6. 保存详细报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"deep_population_analysis_{timestamp}.json"
    
    analysis_report = {
        'timestamp': timestamp,
        'files': {
            'original': original_file,
            'modified': modified_file
        },
        'file_sizes': {
            'original': len(original_content),
            'modified': len(modified_content),
            'difference': len(original_content) - len(modified_content)
        },
        'culture_analysis': {
            'original_distribution': original_prov_data['culture_distribution'],
            'modified_distribution': modified_prov_data['culture_distribution'],
            'culture_differences': {culture: {'original': orig, 'modified': mod, 'difference': diff} 
                                  for culture, orig, mod, diff in culture_diffs}
        },
        'pop_id_analysis': {
            'original_ids_count': len(original_ids),
            'modified_ids_count': len(modified_ids),
            'lost_ids_count': len(lost_ids),
            'lost_ids_sample': sorted(list(lost_ids))[:50],
            'orphaned_references': {
                'original': list(orphaned_refs_orig),
                'modified': list(orphaned_refs_mod)
            }
        },
        'country_level_blocks': {
            'original': {k: len(v) if isinstance(v, str) else len(v) for k, v in original_blocks.items()},
            'modified': {k: len(v) if isinstance(v, str) else len(v) for k, v in modified_blocks.items()}
        }
    }
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细分析报告已保存: {report_filename}")
    
    # 7. 总结问题
    print(f"\n" + "=" * 70)
    print("问题总结")
    print("=" * 70)
    
    issues_found = []
    
    if len(lost_ids) > 0:
        issues_found.append(f"丢失了 {len(lost_ids)} 个人口ID")
    
    if orphaned_refs_mod:
        issues_found.append(f"存在 {len(orphaned_refs_mod)} 个孤立的人口ID引用")
    
    major_culture_losses = [(culture, diff) for culture, orig, mod, diff in culture_diffs 
                           if diff > 100]  # 文化人口减少超过100个
    
    if major_culture_losses:
        issues_found.append(f"主要文化人口大量减少: {len(major_culture_losses)} 种文化")
    
    if issues_found:
        print("发现的问题:")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
        
        print(f"\n可能的原因:")
        print("1. 删除人口时存在引用完整性问题")
        print("2. 国家级统计数据没有同步更新")
        print("3. 人口ID在其他地方被引用但未删除")
        
    else:
        print("未发现明显的数据完整性问题")

if __name__ == "__main__":
    # 比较处理后的文件和正确的备份
    compare_population_data('China1844_09_16.v2', 'autosave.v2')
