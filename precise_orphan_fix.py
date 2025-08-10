#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确修复工具 - 查找并修复剩余的孤立引用
"""

import re
from datetime import datetime

def precise_fix_remaining_orphans():
    """精确修复剩余的孤立引用"""
    print("=" * 60)
    print("精确修复剩余孤立引用")
    print("=" * 60)
    
    filename = 'autosave.v2'
    
    # 加载文件
    try:
        with open(filename, 'r', encoding='latin1') as f:
            content = f.read()
        print(f"文件加载成功: {len(content):,} 字符")
    except Exception as e:
        print(f"加载失败: {e}")
        return
    
    # 提取有效人口ID - 使用更全面的方法
    print("提取有效人口ID...")
    valid_pop_ids = set()
    
    # 查找所有省份
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    total_provinces_checked = 0
    china_provinces_checked = 0
    
    for i, match in enumerate(province_matches):
        if total_provinces_checked >= 3000:  # 检查更多省份
            break
            
        total_provinces_checked += 1
        province_id = int(match.group(1))
        start_pos = match.end()
        
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+20000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 15000
        
        province_content = content[start_pos:end_pos]
        
        # 检查是否是中国省份
        if 'owner="CHI"' in province_content or 'owner=CHI' in province_content:
            china_provinces_checked += 1
            # 提取所有人口ID
            pop_ids = re.findall(r'\bid\s*=\s*(\d+)', province_content)
            valid_pop_ids.update(pop_ids)
    
    print(f"检查了 {total_provinces_checked} 个省份")
    print(f"中国省份: {china_provinces_checked} 个")
    print(f"有效人口ID: {len(valid_pop_ids)} 个")
    
    # 查找所有pop引用
    print("\n查找孤立的pop引用...")
    pop_pattern = r'pop=\s*{\s*id=(\d+)\s*type=(\d+)\s*}'
    pop_matches = list(re.finditer(pop_pattern, content))
    
    orphaned_refs = []
    for match in pop_matches:
        pop_id = match.group(1)
        if pop_id not in valid_pop_ids:
            # 查找这个引用在文件中的上下文
            start_pos = max(0, match.start() - 200)
            end_pos = min(len(content), match.end() + 200)
            context = content[start_pos:end_pos]
            
            # 查找包含这个引用的单位名称
            unit_name_match = re.search(r'name="([^"]+)"', context)
            unit_name = unit_name_match.group(1) if unit_name_match else "未知单位"
            
            orphaned_refs.append({
                'pop_id': pop_id,
                'type_id': match.group(2),
                'start': match.start(),
                'end': match.end(),
                'unit_name': unit_name,
                'context': context,
                'match_text': match.group(0)
            })
    
    print(f"找到 {len(orphaned_refs)} 个孤立引用")
    
    if not orphaned_refs:
        print("✅ 没有发现孤立引用")
        return
    
    # 显示详情
    print(f"\n孤立引用详情:")
    for i, ref in enumerate(orphaned_refs[:10], 1):
        print(f"  {i}. {ref['unit_name']} - pop_id={ref['pop_id']}, type={ref['type_id']}")
    
    if len(orphaned_refs) > 10:
        print(f"  ... 还有 {len(orphaned_refs) - 10} 个引用")
    
    # 询问是否修复
    confirm = input(f"\n确认删除这 {len(orphaned_refs)} 个孤立引用? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("取消修复")
        return
    
    # 创建备份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"autosave.v2.backup_precise_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(filename, backup_filename)
        print(f"备份创建: {backup_filename}")
    except Exception as e:
        print(f"备份失败: {e}")
        return
    
    # 执行修复 - 从后往前删除避免位置偏移
    orphaned_refs.sort(key=lambda x: x['start'], reverse=True)
    
    modified_content = content
    removed_count = 0
    
    for ref in orphaned_refs:
        start = ref['start']
        end = ref['end']
        
        # 找到完整行的范围
        line_start = start
        while line_start > 0 and modified_content[line_start - 1] not in ['\n', '\r']:
            line_start -= 1
        
        line_end = end
        while line_end < len(modified_content) and modified_content[line_end] not in ['\n', '\r']:
            line_end += 1
        if line_end < len(modified_content):
            line_end += 1  # 包含换行符
        
        # 验证要删除的内容
        to_delete = modified_content[line_start:line_end]
        if ref['pop_id'] in to_delete:
            modified_content = modified_content[:line_start] + modified_content[line_end:]
            removed_count += 1
        else:
            print(f"警告: 位置不匹配，跳过 pop_id={ref['pop_id']}")
    
    # 检查花括号平衡
    orig_open = content.count('{')
    orig_close = content.count('}')
    new_open = modified_content.count('{')
    new_close = modified_content.count('}')
    
    print(f"\n花括号检查:")
    print(f"原始: 开={orig_open}, 闭={orig_close}, 差异={orig_open-orig_close}")
    print(f"修改: 开={new_open}, 闭={new_close}, 差异={new_open-new_close}")
    
    if (new_open - new_close) != (orig_open - orig_close):
        print("警告: 花括号平衡发生变化!")
        choice = input("是否继续保存? (yes/no): ").strip().lower()
        if choice not in ['yes', 'y']:
            print("取消保存")
            return
    
    # 保存修复后的文件
    try:
        with open(filename, 'w', encoding='latin1') as f:
            f.write(modified_content)
        
        print(f"\n修复完成!")
        print(f"删除了 {removed_count} 个孤立引用")
        print(f"文件大小: {len(content):,} → {len(modified_content):,} 字符")
        print(f"减少: {len(content) - len(modified_content):,} 字符")
        print(f"备份文件: {backup_filename}")
        
    except Exception as e:
        print(f"保存失败: {e}")

if __name__ == "__main__":
    precise_fix_remaining_orphans()
