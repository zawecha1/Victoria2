#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析并修复孤立的人口ID引用
"""

import re
import json
from datetime import datetime

def find_orphaned_references_details(content, valid_pop_ids):
    """查找孤立引用的详细位置"""
    print("查找孤立人口ID引用的详细位置...")
    
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
    
    # 查找所有ID引用
    id_references = []
    
    # 查找各种可能的ID引用模式
    patterns = [
        (r'id\s*=\s*(\d+)', 'direct_id'),
        (r'pop_id\s*=\s*(\d+)', 'pop_id'),
        (r'leader\s*=\s*(\d+)', 'leader_id'),
        (r'pops\s*=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', 'pops_block'),
        (r'demographics\s*=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', 'demographics_block'),
        (r'(\d{7,})', 'large_number')  # 7位以上数字，可能是人口ID
    ]
    
    for pattern, ref_type in patterns:
        matches = list(re.finditer(pattern, china_content))
        
        for match in matches:
            if ref_type in ['pops_block', 'demographics_block']:
                # 在块内查找ID
                block_content = match.group(1)
                block_ids = re.findall(r'(\d{7,})', block_content)
                
                for block_id in block_ids:
                    if block_id not in valid_pop_ids:
                        id_references.append({
                            'id': block_id,
                            'type': ref_type,
                            'position': start_pos + match.start(),
                            'context': china_content[max(0, match.start()-50):match.end()+50]
                        })
            else:
                ref_id = match.group(1)
                if len(ref_id) >= 7 and ref_id not in valid_pop_ids:  # 长ID且不在有效列表中
                    id_references.append({
                        'id': ref_id,
                        'type': ref_type,
                        'position': start_pos + match.start(),
                        'context': china_content[max(0, match.start()-50):match.end()+50]
                    })
    
    return id_references

def analyze_orphaned_references():
    """分析孤立引用"""
    print("=" * 60)
    print("孤立人口ID引用分析")
    print("=" * 60)
    
    # 加载文件
    try:
        with open('autosave.v2', 'r', encoding='latin1') as f:
            content = f.read()
        print(f"文件加载成功: autosave.v2, 大小: {len(content):,} 字符")
    except Exception as e:
        print(f"加载失败: {e}")
        return
    
    # 获取有效的人口ID（从省份中提取）
    print("提取有效的人口ID...")
    valid_pop_ids = set()
    
    # 查找中国省份中的人口
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    china_provinces_checked = 0
    for i, match in enumerate(province_matches):
        if china_provinces_checked >= 200:  # 检查更多省份
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
            china_provinces_checked += 1
            
            # 提取人口ID
            pop_ids = re.findall(r'id\s*=\s*(\d+)', province_content)
            valid_pop_ids.update(pop_ids)
    
    print(f"从 {china_provinces_checked} 个中国省份中提取到 {len(valid_pop_ids)} 个有效人口ID")
    
    # 查找孤立引用
    orphaned_refs = find_orphaned_references_details(content, valid_pop_ids)
    
    print(f"\n发现 {len(orphaned_refs)} 个孤立的人口ID引用")
    
    # 按类型分组
    by_type = {}
    for ref in orphaned_refs:
        ref_type = ref['type']
        if ref_type not in by_type:
            by_type[ref_type] = []
        by_type[ref_type].append(ref)
    
    print("\n按类型统计:")
    for ref_type, refs in by_type.items():
        print(f"  {ref_type}: {len(refs)} 个")
        
        # 显示示例
        print(f"    示例ID: {[r['id'] for r in refs[:5]]}")
        if refs:
            print(f"    示例上下文: {repr(refs[0]['context'][:100])}")
    
    # 保存详细报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"orphaned_references_analysis_{timestamp}.json"
    
    analysis_data = {
        'timestamp': timestamp,
        'valid_pop_ids_count': len(valid_pop_ids),
        'provinces_checked': china_provinces_checked,
        'orphaned_references_count': len(orphaned_refs),
        'orphaned_by_type': {k: len(v) for k, v in by_type.items()},
        'orphaned_references_sample': orphaned_refs[:50],  # 前50个详细信息
        'all_orphaned_ids': [ref['id'] for ref in orphaned_refs]
    }
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细报告已保存: {report_filename}")
    
    # 分析这些孤立引用是否来自被删除的人口
    print(f"\n" + "=" * 50)
    print("孤立引用来源分析")
    print("=" * 50)
    
    # 加载原始文件进行比较
    try:
        with open('China1844_09_16.v2', 'r', encoding='latin1') as f:
            original_content = f.read()
        
        # 从原始文件提取人口ID
        original_pop_ids = set()
        for i, match in enumerate(province_matches[:200]):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', original_content[start_pos:start_pos+20000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 10000
            
            province_content = original_content[start_pos:end_pos]
            
            if 'owner="CHI"' in province_content or 'owner=CHI' in province_content:
                pop_ids = re.findall(r'id\s*=\s*(\d+)', province_content)
                original_pop_ids.update(pop_ids)
        
        deleted_ids = original_pop_ids - valid_pop_ids
        orphaned_ids = set(ref['id'] for ref in orphaned_refs)
        
        refs_from_deleted = orphaned_ids & deleted_ids
        
        print(f"原始文件人口ID数量: {len(original_pop_ids)}")
        print(f"删除的人口ID数量: {len(deleted_ids)}")
        print(f"孤立引用ID数量: {len(orphaned_ids)}")
        print(f"来自删除人口的孤立引用: {len(refs_from_deleted)} 个")
        
        if refs_from_deleted:
            print(f"示例删除人口的孤立引用: {sorted(list(refs_from_deleted))[:10]}")
            
            print(f"\n这解释了问题:")
            print(f"1. 人口删除操作正确删除了省份中的人口数据")
            print(f"2. 但国家级统计数据中仍保留了对这些人口的引用")
            print(f"3. 这些孤立引用导致游戏尝试访问不存在的人口数据")
            print(f"4. 结果: 游戏崩溃或无法正常加载")
        
    except Exception as e:
        print(f"无法加载原始文件进行比较: {e}")

if __name__ == "__main__":
    analyze_orphaned_references()
