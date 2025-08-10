#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国人口清理工具 - 安全删除非主流文化人口
删除中国境内所有非主流文化和非可接受文化的人口
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
    
    # 找到中国块的结束位置 - 使用更大的搜索范围
    next_country = re.search(r'\n[A-Z]{2,3}=\s*{', content[start_pos:start_pos+500000])
    if next_country:
        end_pos = start_pos + next_country.start()
    else:
        next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+500000])
        if next_section:
            end_pos = start_pos + next_section.start()
        else:
            end_pos = start_pos + 400000  # 扩大搜索范围
    
    china_content = content[start_pos:end_pos]
    
    # 提取主流文化
    primary_culture = None
    primary_culture_match = re.search(r'primary_culture\s*=\s*"([a-z_]+)"', china_content)
    if primary_culture_match:
        primary_culture = primary_culture_match.group(1)
    
    # 提取可接受文化 - 查找culture块
    accepted_cultures = []
    
    # 查找 culture={ ... } 块
    culture_block_match = re.search(r'culture\s*=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', china_content, re.DOTALL)
    if culture_block_match:
        culture_block_content = culture_block_match.group(1)
        # 在culture块中查找引号包围的文化名
        culture_names = re.findall(r'"([a-z_]+)"', culture_block_content)
        
        for culture in culture_names:
            # 跳过"noculture"和主流文化
            if culture != "noculture" and culture != primary_culture:
                accepted_cultures.append(culture)
    
    # 如果仍然没有主流文化，使用默认值
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
                'end': end_pos
            })
        
        if (i + 1) % 500 == 0:
            print(f"  进度: {i + 1}/{len(province_matches)}")
    
    print(f"找到中国省份: {len(china_provinces)} 个")
    return china_provinces

def analyze_population_in_province(province_content, primary_culture, accepted_cultures, referenced_pop_ids):
    """分析省份中的人口 - 修复版，检查引用"""
    population_data = {
        'total_pops': 0,
        'kept_pops': 0,
        'removed_pops': 0,
        'protected_pops': 0,  # 被引用保护的人口
        'removed_details': []
    }
    
    # 已知的人口类型
    pop_types = ['aristocrats', 'artisans', 'bureaucrats', 'capitalists', 'clergymen', 
                 'clerks', 'craftsmen', 'farmers', 'labourers', 'officers', 'soldiers']
    
    for pop_type in pop_types:
        # 查找人口块：pop_type = { ... }
        start_pattern = rf'\b{pop_type}\s*=\s*{{'
        start_matches = list(re.finditer(start_pattern, province_content))
        
        for start_match in start_matches:
            # 找到完整的人口块 - 严格的花括号匹配
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
            pop_block_start = start_match.start()
            pop_content = province_content[pop_block_start:block_end]
            population_data['total_pops'] += 1
            
            # 从人口块中提取文化信息和人口ID
            culture = extract_culture_from_pop_block(pop_content)
            pop_id = extract_pop_id_from_block(pop_content)
            
            # 查找size信息
            size_match = re.search(r'\bsize\s*=\s*([0-9.]+)', pop_content)
            size = float(size_match.group(1)) if size_match else 0
            
            if culture:
                # 检查是否为保留文化
                if culture == primary_culture or culture in accepted_cultures:
                    population_data['kept_pops'] += 1
                else:
                    # 检查是否被引用
                    if pop_id and pop_id in referenced_pop_ids:
                        population_data['protected_pops'] += 1
                        print(f"    保护被引用人口: {pop_type}, 文化={culture}, ID={pop_id}")
                    else:
                        population_data['removed_pops'] += 1
                        
                        # 查找完整行范围用于删除
                        line_start = pop_block_start
                        while line_start > 0 and province_content[line_start - 1] not in ['\n', '\r']:
                            line_start -= 1
                        
                        line_end = block_end
                        while line_end < len(province_content) and province_content[line_end] not in ['\n', '\r']:
                            line_end += 1
                        if line_end < len(province_content):
                            line_end += 1  # 包含换行符
                        
                        population_data['removed_details'].append({
                            'type': pop_type,
                            'culture': culture,
                            'pop_id': pop_id,
                            'size': size,
                            'line_start': line_start,
                            'line_end': line_end,
                            'block_content': pop_content
                        })
            else:
                # 如果无法识别文化，保留人口以确保安全
                population_data['kept_pops'] += 1
                print(f"    保留未识别文化人口: {pop_type}, ID={pop_id}")
    
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

def extract_pop_id_from_block(pop_content):
    """从人口块中提取人口ID"""
    id_match = re.search(r'\bid\s*=\s*(\d+)', pop_content)
    return id_match.group(1) if id_match else None

def check_pop_references(content, pop_id):
    """检查人口ID是否被其他地方引用"""
    if not pop_id:
        return False
    
    # 查找pop={ id=数字 type=数字 }格式的引用
    pop_ref_pattern = rf'pop=\s*{{\s*id={re.escape(pop_id)}\s*type=\d+\s*}}'
    references = re.findall(pop_ref_pattern, content)
    
    # 如果找到引用，说明这个人口被军队或其他单位引用
    return len(references) > 0

def build_population_reference_map(content):
    """构建人口引用映射表"""
    print("构建人口引用映射表...")
    
    # 查找所有pop引用
    pop_ref_pattern = r'pop=\s*{\s*id=(\d+)\s*type=(\d+)\s*}'
    pop_refs = re.findall(pop_ref_pattern, content)
    
    referenced_pop_ids = set()
    for pop_id, pop_type in pop_refs:
        referenced_pop_ids.add(pop_id)
    
    print(f"发现 {len(pop_refs)} 个人口引用，涉及 {len(referenced_pop_ids)} 个不同的人口ID")
    return referenced_pop_ids

def plan_population_cleanup(content, china_provinces, primary_culture, accepted_cultures):
    """规划人口清理方案"""
    print("规划人口清理方案...")
    
    # 首先构建人口引用映射表
    referenced_pop_ids = build_population_reference_map(content)
    
    cleanup_plan = {
        'provinces_affected': 0,
        'total_pops_removed': 0,
        'total_pops_protected': 0,  # 被引用保护的人口数
        'total_population_size_removed': 0,
        'modifications': [],
        'summary': {
            'by_culture': {},
            'by_pop_type': {},
            'protected_by_culture': {}  # 被保护的人口按文化统计
        }
    }
    
    for province in china_provinces:
        province_id = province['id']
        province_name = province['name']
        start_pos = province['start']
        end_pos = province['end']
        
        province_content = content[start_pos:end_pos]
        
        # 分析省份人口（传入引用映射表）
        pop_data = analyze_population_in_province(province_content, primary_culture, accepted_cultures, referenced_pop_ids)
        
        # 统计被保护的人口
        cleanup_plan['total_pops_protected'] += pop_data['protected_pops']
        
        if pop_data['removed_pops'] > 0:
            cleanup_plan['provinces_affected'] += 1
            cleanup_plan['total_pops_removed'] += pop_data['removed_pops']
            
            province_modifications = []
            
            for pop_detail in pop_data['removed_details']:
                cleanup_plan['total_population_size_removed'] += pop_detail['size']
                
                # 统计按文化
                culture = pop_detail['culture']
                if culture not in cleanup_plan['summary']['by_culture']:
                    cleanup_plan['summary']['by_culture'][culture] = 0
                cleanup_plan['summary']['by_culture'][culture] += 1
                
                # 统计按人口类型
                pop_type = pop_detail['type']
                if pop_type not in cleanup_plan['summary']['by_pop_type']:
                    cleanup_plan['summary']['by_pop_type'][pop_type] = 0
                cleanup_plan['summary']['by_pop_type'][pop_type] += 1
                
                province_modifications.append({
                    'pop_type': pop_detail['type'],
                    'culture': pop_detail['culture'],
                    'pop_id': pop_detail.get('pop_id'),
                    'size': pop_detail['size'],
                    'line_start': pop_detail['line_start'],
                    'line_end': pop_detail['line_end']
                })
            
            cleanup_plan['modifications'].append({
                'province_id': province_id,
                'province_name': province_name,
                'province_start': start_pos,
                'province_end': end_pos,
                'pops_to_remove': province_modifications
            })
    
    print(f"规划完成: {cleanup_plan['provinces_affected']} 个省份需要清理")
    print(f"将删除 {cleanup_plan['total_pops_removed']} 个人口单位")
    print(f"保护 {cleanup_plan['total_pops_protected']} 个被引用的人口单位")
    return cleanup_plan

def display_cleanup_plan(cleanup_plan, primary_culture, accepted_cultures):
    """显示清理计划"""
    print("\n" + "=" * 60)
    print("中国人口清理方案")
    print("=" * 60)
    
    print(f"\n保留文化:")
    print(f"  主流文化: {primary_culture}")
    print(f"  可接受文化: {', '.join(accepted_cultures) if accepted_cultures else '无'}")
    
    print(f"\n统计信息:")
    print(f"  受影响省份: {cleanup_plan['provinces_affected']} 个")
    print(f"  删除人口单位: {cleanup_plan['total_pops_removed']} 个")
    print(f"  保护人口单位: {cleanup_plan['total_pops_protected']} 个 (被其他地方引用)")
    print(f"  删除人口总数: {cleanup_plan['total_population_size_removed']:.0f}")
    
    print(f"\n按文化统计 (前10个):")
    culture_stats = sorted(cleanup_plan['summary']['by_culture'].items(), 
                          key=lambda x: x[1], reverse=True)
    for i, (culture, count) in enumerate(culture_stats[:10], 1):
        print(f"  {i:2d}. {culture}: {count} 个人口单位")
    
    print(f"\n按人口类型统计:")
    pop_type_stats = sorted(cleanup_plan['summary']['by_pop_type'].items(), 
                           key=lambda x: x[1], reverse=True)
    for i, (pop_type, count) in enumerate(pop_type_stats, 1):
        print(f"  {i:2d}. {pop_type}: {count} 个人口单位")
    
    print(f"\n受影响省份 (前10个):")
    for i, modification in enumerate(cleanup_plan['modifications'][:10], 1):
        province_name = modification['province_name']
        pops_count = len(modification['pops_to_remove'])
        print(f"  {i:2d}. {province_name}: 删除 {pops_count} 个人口单位")
    
    if len(cleanup_plan['modifications']) > 10:
        print(f"  ... 还有 {len(cleanup_plan['modifications']) - 10} 个省份")
    
    if cleanup_plan['total_pops_protected'] > 0:
        print(f"\n✅ 安全保护: {cleanup_plan['total_pops_protected']} 个被引用的人口将被保留，避免游戏崩溃")

def execute_population_cleanup(content, cleanup_plan):
    """执行人口清理 - 修复版"""
    print("\n开始执行人口清理...")
    
    modified_content = content
    total_removed = 0
    
    # 收集所有删除操作并按全局位置排序
    all_removals = []
    
    for province_mod in cleanup_plan['modifications']:
        province_start = province_mod['province_start']
        
        for pop_mod in province_mod['pops_to_remove']:
            # 计算全局位置 - 修正错误的位置计算
            global_line_start = province_start + pop_mod['line_start']
            global_line_end = province_start + pop_mod['line_end']
            
            all_removals.append({
                'global_start': global_line_start,
                'global_end': global_line_end,
                'pop_type': pop_mod['pop_type'],
                'culture': pop_mod['culture']
            })
    
    # 按全局位置从后往前排序，避免位置偏移
    all_removals.sort(key=lambda x: x['global_start'], reverse=True)
    
    print(f"准备删除 {len(all_removals)} 个人口单位...")
    
    for i, removal in enumerate(all_removals):
        start_pos = removal['global_start']
        end_pos = removal['global_end']
        
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
    return difference == -1  # Victoria II 通常期望 -1

def create_backup(filename):
    """创建备份文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"{filename}.backup_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(filename, backup_filename)
        print(f"备份创建成功: {backup_filename}")
        return backup_filename
    except Exception as e:
        print(f"备份创建失败: {e}")
        return None

def save_modified_file(filename, content, cleanup_plan):
    """保存修改后的文件"""
    # 检查花括号平衡
    if not check_bracket_balance(content):
        print("错误: 花括号不平衡，拒绝保存!")
        return False
    
    # 创建备份
    backup_file = create_backup(filename)
    if not backup_file:
        print("警告: 备份失败，但继续保存...")
    
    try:
        # 保存修改后的文件
        with open(filename, 'w', encoding='latin1') as f:
            f.write(content)
        
        print(f"文件保存成功: {filename}")
        
        # 保存执行报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"population_cleanup_report_{timestamp}.json"
        
        execution_report = {
            'timestamp': timestamp,
            'original_file': filename,
            'backup_file': backup_file,
            'provinces_affected': cleanup_plan['provinces_affected'],
            'total_pops_removed': cleanup_plan['total_pops_removed'],
            'total_pops_protected': cleanup_plan.get('total_pops_protected', 0),
            'total_population_size_removed': cleanup_plan['total_population_size_removed'],
            'summary': cleanup_plan['summary']
        }
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(execution_report, f, ensure_ascii=False, indent=2)
        
        print(f"清理报告已保存: {report_filename}")
        return True
        
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def save_cleanup_report(cleanup_plan, primary_culture, accepted_cultures, filename_suffix=""):
    """保存清理报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"china_population_cleanup_plan_{timestamp}{filename_suffix}.json"
    
    report_data = {
        'timestamp': timestamp,
        'primary_culture': primary_culture,
        'accepted_cultures': accepted_cultures,
        'provinces_affected': cleanup_plan['provinces_affected'],
        'total_pops_removed': cleanup_plan['total_pops_removed'],
        'total_pops_protected': cleanup_plan.get('total_pops_protected', 0),
        'total_population_size_removed': cleanup_plan['total_population_size_removed'],
        'summary': cleanup_plan['summary'],
        'detailed_modifications': cleanup_plan['modifications']
    }
    
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存: {report_filename}")
        return report_filename
    except Exception as e:
        print(f"保存报告失败: {e}")
        return None

def execute_with_confirmation(filename, content, cleanup_plan, primary_culture, accepted_cultures):
    """确认后执行清理"""
    print("\n" + "=" * 50)
    print("人口清理执行确认")
    print("=" * 50)
    
    print(f"文件: {filename}")
    print(f"将要删除: {cleanup_plan['total_pops_removed']} 个人口单位")
    print(f"受影响省份: {cleanup_plan['provinces_affected']} 个")
    print(f"保留文化: {primary_culture}" + (f", {', '.join(accepted_cultures)}" if accepted_cultures else ""))
    
    print("\n警告:")
    print("- 这将永久删除非保留文化的人口")
    print("- 程序会自动创建备份")
    print("- 建议在执行前手动备份重要存档")
    
    while True:
        confirm = input("\n确认执行人口清理? (直接回车确认，输入 no 取消): ").strip().lower()
        if confirm in ['', 'yes', 'y', '是']:
            break
        elif confirm in ['no', 'n', '否']:
            print("用户取消操作")
            return False
        else:
            print("请直接回车确认，或输入 no 取消")
    
    # 执行清理
    print("\n开始执行人口清理...")
    modified_content = execute_population_cleanup(content, cleanup_plan)
    
    # 保存文件
    if save_modified_file(filename, modified_content, cleanup_plan):
        print("\n" + "=" * 50)
        print("人口清理执行成功!")
        print("=" * 50)
        print(f"删除人口单位: {cleanup_plan['total_pops_removed']} 个")
        print(f"受影响省份: {cleanup_plan['provinces_affected']} 个")
        print("现在可以在游戏中加载修改后的存档文件。")
        return True
    else:
        print("人口清理执行失败!")
        return False

def select_save_file():
    """交互式文件选择"""
    print("\n" + "=" * 50)
    print("选择存档文件")
    print("=" * 50)
    
    # 扫描当前目录下的.v2文件
    v2_files = []
    for filename in os.listdir('.'):
        if filename.endswith('.v2'):
            try:
                file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
                mod_time = os.path.getmtime(filename)
                mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                v2_files.append({
                    'name': filename,
                    'size': file_size,
                    'modified': mod_time_str,
                    'mod_timestamp': mod_time
                })
            except:
                continue
    
    if not v2_files:
        print("当前目录下没有找到 .v2 存档文件")
        print("请确保存档文件位于当前目录，或使用命令行参数指定文件:")
        print("  python china_population_cleaner.py <存档文件名>")
        return None
    
    # 按修改时间倒序排列（最新的在前）
    v2_files.sort(key=lambda x: x['mod_timestamp'], reverse=True)
    
    print(f"找到 {len(v2_files)} 个存档文件:")
    print("=" * 85)
    print(f"{'序号':<4} {'文件名':<30} {'大小(MB)':<10} {'修改时间':<20}")
    print("-" * 85)
    
    for i, file_info in enumerate(v2_files, 1):
        print(f"{i:<4} {file_info['name']:<30} {file_info['size']:<10.1f} {file_info['modified']}")
    
    print("-" * 85)
    print("提示:")
    print("- 输入序号 (1-{}) 选择文件".format(len(v2_files)))
    print("- 输入文件名 (支持自动补全 .v2 后缀)")
    print("- 直接回车退出程序")
    
    while True:
        try:
            choice = input(f"\n请选择文件: ").strip()
            
            if not choice:
                print("未选择文件，退出程序")
                return None
            
            # 尝试解析为数字
            try:
                index = int(choice) - 1
                if 0 <= index < len(v2_files):
                    selected_file = v2_files[index]['name']
                    print(f"已选择: {selected_file} ({v2_files[index]['size']:.1f} MB)")
                    return selected_file
                else:
                    print(f"请输入 1 到 {len(v2_files)} 之间的数字")
                    continue
            except ValueError:
                pass
            
            # 检查是否为有效的文件名
            if choice.endswith('.v2') and os.path.exists(choice):
                file_size = os.path.getsize(choice) / (1024 * 1024)
                print(f"已选择: {choice} ({file_size:.1f} MB)")
                return choice
            elif not choice.endswith('.v2'):
                # 自动添加.v2后缀
                choice_with_ext = choice + '.v2'
                if os.path.exists(choice_with_ext):
                    file_size = os.path.getsize(choice_with_ext) / (1024 * 1024)
                    print(f"已选择: {choice_with_ext} ({file_size:.1f} MB)")
                    return choice_with_ext
            
            print(f"文件 '{choice}' 不存在，请重新选择")
            
        except KeyboardInterrupt:
            print("\n用户中断，退出程序")
            return None
        except Exception as e:
            print(f"选择出错: {e}，请重新选择")

def main():
    """主函数"""
    import sys
    
    print("=" * 60)
    print("Victoria II 中国人口清理工具")
    print("=" * 60)
    print("功能: 删除中国境内非主流文化和非可接受文化的人口")
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        mode = sys.argv[2].lower() if len(sys.argv) > 2 else 'preview'
    else:
        # 使用交互式文件选择
        filename = select_save_file()
        if not filename:
            return
        
        print("\n" + "=" * 50)
        print("选择运行模式")
        print("=" * 50)
        print("1. preview  - 预览模式 (仅显示清理计划，不修改文件)")
        print("2. execute  - 执行模式 (实际执行清理操作)")
        
        while True:
            mode_choice = input("\n请选择模式 (1/2 或 preview/execute，默认: preview): ").strip().lower()
            if not mode_choice or mode_choice in ['1', 'preview']:
                mode = 'preview'
                break
            elif mode_choice in ['2', 'execute']:
                mode = 'execute'
                break
            else:
                print("请输入 1、2、preview 或 execute")
    
    # 检查文件是否存在
    if not os.path.exists(filename):
        print(f"错误: 未找到文件 {filename}")
        return
    
    # 加载文件
    print(f"\n加载文件: {filename}")
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
    cleanup_plan = plan_population_cleanup(content, china_provinces, primary_culture, accepted_cultures)
    
    # 显示方案
    display_cleanup_plan(cleanup_plan, primary_culture, accepted_cultures)
    
    if mode == 'preview':
        print("\n[预览模式]")
        save_cleanup_report(cleanup_plan, primary_culture, accepted_cultures, "_preview")
        print(f"\n注意: 这只是预览! 要实际执行清理，请使用: python {sys.argv[0]} {filename} execute")
    
    elif mode == 'execute':
        print("\n[执行模式]")
        success = execute_with_confirmation(filename, content, cleanup_plan, primary_culture, accepted_cultures)
        if not success:
            print("人口清理未执行")

if __name__ == "__main__":
    main()
