#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单修复军队单位中的孤立人口引用 - 只删除pop引用，保留单位
"""

import re
from datetime import datetime

def simple_fix_army_references():
    """简单修复：只删除pop={...}块，保留军队单位"""
    print("=" * 60)
    print("简单军队引用修复工具")
    print("=" * 60)
    
    # 加载文件
    try:
        with open('autosave.v2', 'r', encoding='latin1') as f:
            content = f.read()
        print(f"文件加载成功: autosave.v2, 大小: {len(content):,} 字符")
    except Exception as e:
        print(f"加载失败: {e}")
        return
    
    # 获取有效人口ID
    print("提取有效的人口ID...")
    valid_pop_ids = set()
    
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    china_provinces_checked = 0
    for i, match in enumerate(province_matches):
        if china_provinces_checked >= 500:  # 检查更多省份确保完整性
            break
            
        province_id = int(match.group(1))
        start_pos = match.end()
        
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+20000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 10000
        
        province_content = content[start_pos:end_pos]
        
        if 'owner="CHI"' in province_content or 'owner=CHI' in province_content:
            china_provinces_checked += 1
            pop_ids = re.findall(r'id\s*=\s*(\d+)', province_content)
            valid_pop_ids.update(pop_ids)
    
    print(f"从 {china_provinces_checked} 个中国省份中提取到 {len(valid_pop_ids)} 个有效人口ID")
    
    # 查找并修复孤立的pop引用
    print("查找孤立的pop引用...")
    
    # 查找所有 pop={ id=数字 type=数字 } 模式
    pop_pattern = r'pop=\s*{\s*id=(\d+)\s*type=(\d+)\s*}'
    pop_matches = list(re.finditer(pop_pattern, content))
    
    orphaned_pops = []
    for match in pop_matches:
        pop_id = match.group(1)
        if pop_id not in valid_pop_ids:
            orphaned_pops.append({
                'pop_id': pop_id,
                'start': match.start(),
                'end': match.end(),
                'full_match': match.group(0)
            })
    
    print(f"找到 {len(orphaned_pops)} 个孤立的pop引用")
    
    if not orphaned_pops:
        print("未发现孤立的pop引用")
        return
    
    # 显示示例
    for i, pop in enumerate(orphaned_pops[:5], 1):
        print(f"  {i}. pop_id={pop['pop_id']}, 位置={pop['start']}-{pop['end']}")
    
    if len(orphaned_pops) > 5:
        print(f"  ... 还有 {len(orphaned_pops) - 5} 个引用")
    
    # 询问是否修复
    confirm = input(f"\n确认删除这 {len(orphaned_pops)} 个孤立的pop引用? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("用户取消操作")
        return
    
    # 创建备份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"autosave.v2.backup_simple_fix_{timestamp}"
    
    try:
        import shutil
        shutil.copy2('autosave.v2', backup_filename)
        print(f"备份创建成功: {backup_filename}")
    except Exception as e:
        print(f"备份创建失败: {e}")
        return
    
    # 执行修复：从后往前删除
    orphaned_pops.sort(key=lambda x: x['start'], reverse=True)
    
    modified_content = content
    for pop in orphaned_pops:
        start = pop['start']
        end = pop['end']
        
        # 查找完整行的范围，包括前面的换行和缩进
        line_start = start
        while line_start > 0 and modified_content[line_start - 1] not in ['\n', '\r']:
            line_start -= 1
        
        # 查找行结束
        line_end = end
        while line_end < len(modified_content) and modified_content[line_end] not in ['\n', '\r']:
            line_end += 1
        if line_end < len(modified_content):
            line_end += 1  # 包含换行符
        
        # 执行删除
        modified_content = modified_content[:line_start] + modified_content[line_end:]
    
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
        with open('autosave.v2', 'w', encoding='latin1') as f:
            f.write(modified_content)
        
        print(f"\n修复完成!")
        print(f"原始大小: {len(content):,} 字符")
        print(f"修复后大小: {len(modified_content):,} 字符")
        print(f"差异: {len(content) - len(modified_content):,} 字符")
        print(f"删除了 {len(orphaned_pops)} 个孤立的pop引用")
        print(f"备份文件: {backup_filename}")
        
    except Exception as e:
        print(f"保存失败: {e}")

if __name__ == "__main__":
    simple_fix_army_references()
