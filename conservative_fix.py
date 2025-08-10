#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保守修复策略 - 只删除明确孤立的引用，不触及人口数据
"""

import re
from datetime import datetime

def conservative_fix():
    """保守修复策略"""
    print("=" * 60)
    print("保守修复策略 - 只修复孤立引用")
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
    
    # 1. 提取所有有效的人口ID（不只是中国的）
    print("提取所有有效人口ID...")
    valid_pop_ids = set()
    
    # 查找所有省份的所有人口ID
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    total_provinces = 0
    for i, match in enumerate(province_matches):
        if total_provinces >= 3248:  # 检查所有省份
            break
            
        total_provinces += 1
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
        
        # 提取所有人口ID，不管是哪个国家的
        pop_ids = re.findall(r'\bid\s*=\s*(\d+)', province_content)
        valid_pop_ids.update(pop_ids)
        
        if (total_provinces) % 500 == 0:
            print(f"  进度: {total_provinces}/{len(province_matches)}")
    
    print(f"检查了 {total_provinces} 个省份")
    print(f"提取到 {len(valid_pop_ids)} 个有效人口ID")
    
    # 2. 查找孤立的pop引用
    print("\n查找孤立的pop引用...")
    pop_pattern = r'pop=\s*{\s*id=(\d+)\s*type=(\d+)\s*}'
    pop_matches = list(re.finditer(pop_pattern, content))
    
    orphaned_refs = []
    for match in pop_matches:
        pop_id = match.group(1)
        if pop_id not in valid_pop_ids:
            orphaned_refs.append({
                'pop_id': pop_id,
                'type_id': match.group(2),
                'start': match.start(),
                'end': match.end(),
                'match_text': match.group(0)
            })
    
    print(f"找到 {len(orphaned_refs)} 个孤立引用")
    print(f"总pop引用: {len(pop_matches)} 个")
    
    if not orphaned_refs:
        print("✅ 没有孤立引用")
        return
    
    # 显示一些示例
    print(f"\n孤立引用示例:")
    for i, ref in enumerate(orphaned_refs[:10], 1):
        print(f"  {i}. pop_id={ref['pop_id']}, type={ref['type_id']}")
    
    if len(orphaned_refs) > 10:
        print(f"  ... 还有 {len(orphaned_refs) - 10} 个")
    
    # 询问是否修复
    confirm = input(f"\n确认删除这 {len(orphaned_refs)} 个孤立引用? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("取消修复")
        return
    
    # 创建备份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"autosave.v2.backup_conservative_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(filename, backup_filename)
        print(f"备份创建: {backup_filename}")
    except Exception as e:
        print(f"备份失败: {e}")
        return
    
    # 执行修复 - 只删除pop引用行
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
        if ref['pop_id'] in to_delete and 'pop=' in to_delete:
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
        
        print(f"\n保守修复完成!")
        print(f"删除了 {removed_count} 个孤立引用")
        print(f"文件大小: {len(content):,} → {len(modified_content):,} 字符")
        print(f"减少: {len(content) - len(modified_content):,} 字符")
        print(f"备份文件: {backup_filename}")
        
        # 验证修复结果
        print("\n验证修复结果...")
        pop_matches_after = list(re.finditer(pop_pattern, modified_content))
        
        # 重新计算有效ID（使用修复后的内容）
        valid_pop_ids_after = set()
        province_matches_after = list(province_pattern.finditer(modified_content))
        
        for i, match in enumerate(province_matches_after[:1000]):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            if i + 1 < len(province_matches_after):
                end_pos = province_matches_after[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', modified_content[start_pos:start_pos+15000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 10000
            
            province_content = modified_content[start_pos:end_pos]
            pop_ids = re.findall(r'\bid\s*=\s*(\d+)', province_content)
            valid_pop_ids_after.update(pop_ids)
        
        orphaned_after = sum(1 for match in pop_matches_after if match.group(1) not in valid_pop_ids_after)
        
        print(f"修复后总pop引用: {len(pop_matches_after)} 个")
        print(f"修复后孤立引用: {orphaned_after} 个")
        print(f"状态: {'✅ 完美!' if orphaned_after == 0 else f'⚠️ 还有{orphaned_after}个'}")
        
    except Exception as e:
        print(f"保存失败: {e}")

if __name__ == "__main__":
    conservative_fix()
