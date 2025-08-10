#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复军队单位中的孤立人口引用
当删除人口后，需要同时更新或删除引用这些人口的军队单位
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

def get_valid_population_ids(content):
    """获取所有有效的人口ID"""
    print("提取有效的人口ID...")
    valid_pop_ids = set()
    
    # 查找所有省份
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    china_provinces_checked = 0
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
        if 'owner="CHI"' in province_content or 'owner=CHI' in province_content:
            china_provinces_checked += 1
            
            # 提取人口ID
            pop_ids = re.findall(r'id\s*=\s*(\d+)', province_content)
            valid_pop_ids.update(pop_ids)
    
    print(f"从 {china_provinces_checked} 个中国省份中提取到 {len(valid_pop_ids)} 个有效人口ID")
    return valid_pop_ids

def find_army_units_with_orphaned_refs(content, valid_pop_ids):
    """查找包含孤立人口引用的军队单位"""
    print("查找军队单位中的孤立人口引用...")
    
    # 查找中国国家块
    china_pattern = re.compile(r'^CHI=\s*{', re.MULTILINE)
    china_match = china_pattern.search(content)
    
    if not china_match:
        print("错误: 未找到中国国家数据")
        return []
    
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
    
    # 查找军队单位模式 - 改进的方法
    orphaned_units = []
    
    # 查找所有包含 pop={ id=数字 } 的位置
    pop_pattern = r'pop=\s*{\s*id=(\d+)\s*type=(\d+)\s*}'
    pop_matches = list(re.finditer(pop_pattern, china_content))
    
    for pop_match in pop_matches:
        pop_id = pop_match.group(1)
        unit_type = pop_match.group(2)
        
        if pop_id not in valid_pop_ids:
            # 向前查找对应的单位名称
            search_start = max(0, pop_match.start() - 300)
            context_before = china_content[search_start:pop_match.start()]
            
            # 查找name="..."
            name_match = None
            for match in re.finditer(r'name="([^"]+)"', context_before):
                name_match = match
            
            unit_name = name_match.group(1) if name_match else f"Unknown_Unit_{pop_id}"
            
            # 查找单位块的边界 - 更精确的方法
            # 向前查找单位块开始（找到最近的花括号开始）
            unit_start_search = max(0, pop_match.start() - 500)
            context_for_start = china_content[unit_start_search:pop_match.start()]
            
            # 查找最后一个单位开始标记
            unit_start_relative = unit_start_search
            brace_pattern = r'\n\s*([a-zA-Z_][a-zA-Z0-9_]*|unit)\s*=\s*{'
            for match in re.finditer(brace_pattern, context_for_start):
                unit_start_relative = unit_start_search + match.start() + 1  # +1 跳过换行符
            
            # 向后查找单位块结束
            search_from = pop_match.end()
            brace_count = 1  # pop块的闭括号已经算过了，现在找整个单位的闭括号
            
            # 从pop块后面开始计算花括号
            unit_end_relative = search_from
            i = search_from
            while i < len(china_content) and brace_count > 0:
                char = china_content[i]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                i += 1
            
            if brace_count == 0:
                unit_end_relative = i
            else:
                # 如果没找到匹配的闭括号，使用估算位置
                unit_end_relative = search_from + 200
            
            orphaned_units.append({
                'name': unit_name,
                'pop_id': pop_id,
                'unit_type': unit_type,
                'start_pos': start_pos + unit_start_relative,
                'end_pos': start_pos + unit_end_relative,
                'relative_start': unit_start_relative,
                'relative_end': unit_end_relative,
                'pop_match_pos': pop_match.start(),
                'full_context': china_content[unit_start_relative:unit_end_relative]
            })
    
    print(f"找到 {len(orphaned_units)} 个包含孤立引用的军队单位")
    return orphaned_units

def fix_orphaned_army_references(content, orphaned_units, fix_method='remove'):
    """修复孤立的军队引用"""
    print(f"\n开始修复孤立的军队引用 (方法: {fix_method})...")
    
    modified_content = content
    total_fixed = 0
    
    if fix_method == 'remove':
        # 方法1: 删除整个军队单位
        # 按位置从后往前排序，避免位置偏移
        sorted_units = sorted(orphaned_units, key=lambda x: x['start_pos'], reverse=True)
        
        for unit in sorted_units:
            start_pos = unit['start_pos']
            end_pos = unit['end_pos']
            
            # 找到完整行的边界
            line_start = start_pos
            while line_start > 0 and modified_content[line_start - 1] not in ['\n', '\r']:
                line_start -= 1
            
            line_end = end_pos
            while line_end < len(modified_content) and modified_content[line_end] not in ['\n', '\r']:
                line_end += 1
            if line_end < len(modified_content):
                line_end += 1  # 包含换行符
            
            # 验证删除内容
            to_delete = modified_content[line_start:line_end]
            if unit['name'] in to_delete:
                # 执行删除
                modified_content = modified_content[:line_start] + modified_content[line_end:]
                total_fixed += 1
                print(f"  删除军队单位: {unit['name']} (pop_id: {unit['pop_id']})")
            else:
                print(f"  警告: 无法验证删除内容 {unit['name']}")
    
    elif fix_method == 'update':
        # 方法2: 更新引用到有效的人口ID (这需要知道替代的ID)
        print("更新方法暂未实现 - 需要确定替代的人口ID")
        return content
    
    print(f"修复完成! 处理了 {total_fixed} 个军队单位")
    return modified_content

def create_backup(filename):
    """创建备份文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"{filename}.backup_army_fix_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(filename, backup_filename)
        print(f"备份创建成功: {backup_filename}")
        return backup_filename
    except Exception as e:
        print(f"备份创建失败: {e}")
        return None

def check_bracket_balance(content):
    """检查花括号平衡"""
    open_count = content.count('{')
    close_count = content.count('}')
    difference = open_count - close_count
    
    print(f"花括号检查: 开={open_count}, 闭={close_count}, 差异={difference}")
    return difference == -1

def main():
    """主函数"""
    print("=" * 70)
    print("军队单位孤立人口引用修复工具")
    print("=" * 70)
    
    filename = 'autosave.v2'
    
    # 加载文件
    content = load_file_simple(filename)
    if not content:
        return
    
    # 获取有效人口ID
    valid_pop_ids = get_valid_population_ids(content)
    
    # 查找孤立引用的军队单位
    orphaned_units = find_army_units_with_orphaned_refs(content, valid_pop_ids)
    
    if not orphaned_units:
        print("未发现孤立引用的军队单位")
        return
    
    # 显示发现的问题
    print(f"\n发现的问题军队单位:")
    for i, unit in enumerate(orphaned_units[:10], 1):  # 显示前10个
        print(f"  {i:2d}. {unit['name']} (人口ID: {unit['pop_id']}, 类型: {unit['unit_type']})")
    
    if len(orphaned_units) > 10:
        print(f"  ... 还有 {len(orphaned_units) - 10} 个单位")
    
    # 询问修复方法
    print(f"\n修复选项:")
    print("1. remove  - 删除包含孤立引用的军队单位")
    print("2. analyze - 仅分析，不修改文件")
    
    while True:
        choice = input("\n请选择修复方法 (1/2 或 remove/analyze，默认: analyze): ").strip().lower()
        if not choice or choice in ['2', 'analyze']:
            print("仅进行分析，不修改文件")
            
            # 保存分析报告
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f"army_orphaned_refs_analysis_{timestamp}.json"
            
            analysis_data = {
                'timestamp': timestamp,
                'file_analyzed': filename,
                'valid_pop_ids_count': len(valid_pop_ids),
                'orphaned_units_count': len(orphaned_units),
                'orphaned_units': orphaned_units
            }
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            print(f"分析报告已保存: {report_filename}")
            return
            
        elif choice in ['1', 'remove']:
            break
        else:
            print("请输入 1、2、remove 或 analyze")
    
    # 执行修复
    print(f"\n警告: 即将删除 {len(orphaned_units)} 个军队单位")
    print("这些单位引用了已删除的人口，保留它们会导致游戏崩溃")
    
    confirm = input("\n确认执行修复? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("用户取消操作")
        return
    
    # 创建备份
    backup_file = create_backup(filename)
    if not backup_file:
        print("警告: 备份失败，但继续修复...")
    
    # 执行修复
    modified_content = fix_orphaned_army_references(content, orphaned_units, 'remove')
    
    # 检查花括号平衡
    if not check_bracket_balance(modified_content):
        print("错误: 花括号不平衡，拒绝保存!")
        return
    
    # 保存修复后的文件
    try:
        with open(filename, 'w', encoding='latin1') as f:
            f.write(modified_content)
        
        print(f"文件修复完成: {filename}")
        print(f"原始大小: {len(content):,} 字符")
        print(f"修复后大小: {len(modified_content):,} 字符")
        print(f"差异: {len(content) - len(modified_content):,} 字符")
        
        print(f"\n修复总结:")
        print(f"- 删除了 {len(orphaned_units)} 个引用已删除人口的军队单位")
        print(f"- 花括号平衡正确")
        print(f"- 备份文件: {backup_file}")
        print(f"- 现在可以尝试在游戏中加载存档文件")
        
    except Exception as e:
        print(f"保存失败: {e}")

if __name__ == "__main__":
    main()
