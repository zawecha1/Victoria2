#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面诊断工具 - 检查存档文件问题
"""

import re
import os
from datetime import datetime

def compare_files():
    """对比修改前后的文件差异"""
    print("=" * 60)
    print("存档文件对比诊断")
    print("=" * 60)
    
    # 检查文件是否存在
    original_file = "China1844_09_16.v2"  # 正确的备份
    current_file = "autosave.v2"          # 修改后的文件
    
    if not os.path.exists(original_file):
        print(f"错误: 备份文件 {original_file} 不存在")
        return
    
    if not os.path.exists(current_file):
        print(f"错误: 当前文件 {current_file} 不存在")
        return
    
    # 加载文件
    try:
        with open(original_file, 'r', encoding='latin1') as f:
            original_content = f.read()
        with open(current_file, 'r', encoding='latin1') as f:
            current_content = f.read()
    except Exception as e:
        print(f"文件加载失败: {e}")
        return
    
    print(f"原始文件 ({original_file}):")
    print(f"  大小: {len(original_content):,} 字符")
    print(f"  开花括号: {original_content.count('{'):,}")
    print(f"  闭花括号: {original_content.count('}'):,}")
    print(f"  差异: {original_content.count('{') - original_content.count('}')}")
    
    print(f"\n修改文件 ({current_file}):")
    print(f"  大小: {len(current_content):,} 字符")
    print(f"  开花括号: {current_content.count('{'):,}")
    print(f"  闭花括号: {current_content.count('}'):,}")
    print(f"  差异: {current_content.count('{') - current_content.count('}')}")
    
    size_diff = len(original_content) - len(current_content)
    print(f"\n文件大小差异: {size_diff:,} 字符 ({size_diff/(1024*1024):.1f} MB)")
    
    return original_content, current_content

def check_file_structure(content, filename):
    """检查文件结构完整性"""
    print(f"\n检查 {filename} 的结构完整性:")
    
    # 检查重要部分是否存在
    critical_sections = [
        ('date=', '游戏日期'),
        ('CHI={', '中国国家数据'),
        ('provinces={', '省份数据'),
        ('diplomacy={', '外交数据'),
        ('technology={', '科技数据'),
        ('economy={', '经济数据')
    ]
    
    missing_sections = []
    for pattern, description in critical_sections:
        count = content.count(pattern)
        print(f"  {description}: {count} 个")
        if count == 0:
            missing_sections.append(description)
    
    if missing_sections:
        print(f"  ❌ 缺失关键部分: {', '.join(missing_sections)}")
        return False
    else:
        print(f"  ✅ 所有关键部分都存在")
        return True

def check_population_integrity(content, filename):
    """检查人口数据完整性"""
    print(f"\n检查 {filename} 的人口数据完整性:")
    
    # 统计省份数量
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    print(f"  总省份数: {len(province_matches)}")
    
    # 统计中国省份
    china_provinces = 0
    total_china_pops = 0
    
    for i, match in enumerate(province_matches):
        if i >= 1000:  # 只检查前1000个省份避免超时
            break
            
        province_id = int(match.group(1))
        start_pos = match.end()
        
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+10000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 8000
        
        province_content = content[start_pos:end_pos]
        
        if 'owner="CHI"' in province_content or 'owner=CHI' in province_content:
            china_provinces += 1
            # 统计人口数量
            pop_types = ['aristocrats', 'artisans', 'bureaucrats', 'capitalists', 'clergymen', 
                        'clerks', 'craftsmen', 'farmers', 'labourers', 'officers', 'soldiers']
            for pop_type in pop_types:
                pop_count = len(re.findall(rf'\b{pop_type}\s*=\s*{{', province_content))
                total_china_pops += pop_count
    
    print(f"  中国省份数: {china_provinces}")
    print(f"  中国人口单位: {total_china_pops}")
    
    return china_provinces, total_china_pops

def check_army_units(content, filename):
    """检查军队单位"""
    print(f"\n检查 {filename} 的军队单位:")
    
    # 统计军队单位类型
    army_types = ['infantry', 'cavalry', 'artillery', 'dragoon', 'guard']
    total_units = 0
    
    for army_type in army_types:
        pattern = rf'\b{army_type}\s*=\s*{{'
        count = len(re.findall(pattern, content))
        total_units += count
        if count > 0:
            print(f"  {army_type}: {count} 个单位")
    
    print(f"  总军队单位: {total_units}")
    
    # 检查pop引用
    pop_refs = len(re.findall(r'pop=\s*{\s*id=\d+\s*type=\d+\s*}', content))
    print(f"  军队pop引用: {pop_refs}")
    
    return total_units, pop_refs

def check_syntax_errors(content, filename):
    """检查语法错误"""
    print(f"\n检查 {filename} 的语法错误:")
    
    errors = []
    
    # 检查未闭合的花括号
    open_braces = content.count('{')
    close_braces = content.count('}')
    brace_diff = open_braces - close_braces
    
    if brace_diff != -1:  # Victoria II通常是-1
        errors.append(f"花括号不平衡: 差异={brace_diff} (应该是-1)")
    
    # 检查常见语法问题
    lines = content.split('\n')
    for i, line in enumerate(lines[:1000], 1):  # 只检查前1000行
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # 检查未闭合的引号
        if line.count('"') % 2 != 0:
            errors.append(f"第{i}行: 未闭合的引号")
            
        # 检查等号前后是否合理
        if '=' in line and not re.match(r'^[a-zA-Z_0-9]+\s*=', line):
            if not line.startswith('\t') and not line.startswith('    '):
                errors.append(f"第{i}行: 等号格式可能有误")
    
    if errors:
        print(f"  ❌ 发现 {len(errors)} 个语法问题:")
        for error in errors[:5]:  # 只显示前5个
            print(f"    - {error}")
        if len(errors) > 5:
            print(f"    ... 还有 {len(errors) - 5} 个问题")
        return False
    else:
        print(f"  ✅ 未发现明显的语法错误")
        return True

def check_orphaned_references(content, filename):
    """检查孤立引用"""
    print(f"\n检查 {filename} 的孤立引用:")
    
    # 提取有效的人口ID
    valid_pop_ids = set()
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    china_provinces_checked = 0
    for i, match in enumerate(province_matches):
        if china_provinces_checked >= 500:
            break
            
        province_id = int(match.group(1))
        start_pos = match.end()
        
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+10000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 8000
        
        province_content = content[start_pos:end_pos]
        
        if 'owner="CHI"' in province_content or 'owner=CHI' in province_content:
            china_provinces_checked += 1
            pop_ids = re.findall(r'id\s*=\s*(\d+)', province_content)
            valid_pop_ids.update(pop_ids)
    
    print(f"  有效人口ID: {len(valid_pop_ids)} 个")
    
    # 检查孤立的pop引用
    pop_pattern = r'pop=\s*{\s*id=(\d+)\s*type=(\d+)\s*}'
    pop_matches = list(re.finditer(pop_pattern, content))
    
    orphaned_count = 0
    for match in pop_matches:
        pop_id = match.group(1)
        if pop_id not in valid_pop_ids:
            orphaned_count += 1
    
    print(f"  总pop引用: {len(pop_matches)} 个")
    print(f"  孤立引用: {orphaned_count} 个")
    
    if orphaned_count > 0:
        print(f"  ❌ 发现孤立引用")
        return False
    else:
        print(f"  ✅ 没有孤立引用")
        return True

def main():
    """主函数"""
    print("Victoria II 存档全面诊断工具")
    
    # 对比文件
    result = compare_files()
    if not result:
        return
    
    original_content, current_content = result
    
    # 检查原始文件
    print("\n" + "=" * 60)
    print("原始文件检查 (China1844_09_16.v2)")
    print("=" * 60)
    check_file_structure(original_content, "China1844_09_16.v2")
    orig_provinces, orig_pops = check_population_integrity(original_content, "China1844_09_16.v2")
    orig_units, orig_refs = check_army_units(original_content, "China1844_09_16.v2")
    orig_syntax_ok = check_syntax_errors(original_content, "China1844_09_16.v2")
    orig_refs_ok = check_orphaned_references(original_content, "China1844_09_16.v2")
    
    # 检查修改后文件
    print("\n" + "=" * 60)
    print("修改后文件检查 (autosave.v2)")
    print("=" * 60)
    check_file_structure(current_content, "autosave.v2")
    curr_provinces, curr_pops = check_population_integrity(current_content, "autosave.v2")
    curr_units, curr_refs = check_army_units(current_content, "autosave.v2")
    curr_syntax_ok = check_syntax_errors(current_content, "autosave.v2")
    curr_refs_ok = check_orphaned_references(current_content, "autosave.v2")
    
    # 对比总结
    print("\n" + "=" * 60)
    print("对比总结")
    print("=" * 60)
    
    print(f"文件大小变化: {len(original_content) - len(current_content):,} 字符")
    print(f"中国省份变化: {orig_provinces} → {curr_provinces} ({curr_provinces - orig_provinces:+d})")
    print(f"中国人口变化: {orig_pops} → {curr_pops} ({curr_pops - orig_pops:+d})")
    print(f"军队单位变化: {orig_units} → {curr_units} ({curr_units - orig_units:+d})")
    print(f"军队引用变化: {orig_refs} → {curr_refs} ({curr_refs - orig_refs:+d})")
    
    print(f"\n文件完整性:")
    print(f"  原始文件语法: {'✅ 正常' if orig_syntax_ok else '❌ 有问题'}")
    print(f"  修改文件语法: {'✅ 正常' if curr_syntax_ok else '❌ 有问题'}")
    print(f"  原始文件引用: {'✅ 正常' if orig_refs_ok else '❌ 有问题'}")
    print(f"  修改文件引用: {'✅ 正常' if curr_refs_ok else '❌ 有问题'}")
    
    # 建议
    print(f"\n建议:")
    if not curr_syntax_ok:
        print("  ❌ 修改后的文件存在语法错误，需要修复")
    if not curr_refs_ok:
        print("  ❌ 修改后的文件存在孤立引用，需要清理")
    if curr_provinces < orig_provinces:
        print("  ⚠️  中国省份数量减少，可能删除了重要数据")
    if curr_pops == 0:
        print("  ❌ 中国人口为0，这肯定有问题")
    if curr_units < orig_units * 0.8:
        print("  ⚠️  军队单位大幅减少，可能过度删除")
    
    if curr_syntax_ok and curr_refs_ok and curr_pops > 0:
        print("  ✅ 文件看起来基本正常")

if __name__ == "__main__":
    main()
