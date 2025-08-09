#!/usr/bin/env python3
"""
找出真正导致人口丢失的原因
"""

import re
import os

def find_real_population_issue():
    """寻找真正的人口问题"""
    print("🔍 寻找真正的人口问题原因")
    print("="*60)
    
    files = {
        "China1839_08_08_unified_backup_20250808_001305.v2": "原始文件",
        "autosave.v2": "修改后文件"
    }
    
    results = {}
    
    for filename, description in files.items():
        if not os.path.exists(filename):
            print(f"❌ 文件不存在: {filename}")
            continue
            
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
            
            print(f"\n📄 分析 {description} ({filename}):")
            
            # 详细的人口结构分析
            # 1. 查找province块
            province_pattern = r'(\d{3,4})\s*=\s*\{'
            provinces = re.findall(province_pattern, content)
            print(f"  省份数量: {len(provinces)}")
            
            # 2. 查找人口id块模式 - 在province内的人口
            # Victoria II的人口结构通常是: province = { ... population = { id1={ ... } id2={ ... } } ... }
            pop_id_pattern = r'(\d+)\s*=\s*\{\s*type\s*=\s*(\d+)'
            pop_ids = re.findall(pop_id_pattern, content)
            print(f"  人口ID块: {len(pop_ids)}")
            
            # 3. 查找size字段
            size_pattern = r'size\s*=\s*([\d.]+)'
            sizes = re.findall(size_pattern, content)
            non_zero_sizes = [float(x) for x in sizes if float(x) > 0]
            print(f"  size字段: {len(sizes)} (非零: {len(non_zero_sizes)})")
            print(f"  总人口: {sum(non_zero_sizes):,.0f}")
            
            # 4. 查找population块
            # 在Victoria II中，人口数据通常在province的population字段下
            population_block_pattern = r'population\s*=\s*\{'
            pop_blocks = re.findall(population_block_pattern, content)
            print(f"  population块: {len(pop_blocks)}")
            
            # 5. 检查特定省份的人口结构（以省份1为例）
            prov_1_pattern = r'1\s*=\s*\{[^}]*?population\s*=\s*\{([^{}]*(?:\{[^}]*\}[^{}]*)*)\}'
            prov_1_match = re.search(prov_1_pattern, content, re.DOTALL)
            if prov_1_match:
                prov_1_pop = prov_1_match.group(1)
                prov_1_sizes = re.findall(r'size\s*=\s*([\d.]+)', prov_1_pop)
                print(f"  省份1人口: {len(prov_1_sizes)} 个pop, 总数: {sum(float(x) for x in prov_1_sizes):,.0f}")
            else:
                print(f"  省份1人口: 未找到")
            
            # 6. 检查最近修改的痕迹
            recent_changes = []
            if 'civilized="no"' in content:
                recent_changes.append("civilized修改")
            if 'badboy=' in content:
                recent_changes.append("badboy修改")
            print(f"  最近修改: {', '.join(recent_changes) if recent_changes else '无'}")
            
            results[filename] = {
                'provinces': len(provinces),
                'pop_ids': len(pop_ids),
                'sizes': len(sizes),
                'non_zero_pop': sum(non_zero_sizes),
                'pop_blocks': len(pop_blocks)
            }
            
        except Exception as e:
            print(f"❌ 分析 {filename} 时出错: {e}")
    
    # 比较结果
    if len(results) == 2:
        original_file = "China1839_08_08_unified_backup_20250808_001305.v2"
        modified_file = "autosave.v2"
        
        if original_file in results and modified_file in results:
            orig = results[original_file]
            mod = results[modified_file]
            
            print(f"\n📊 关键差异:")
            print(f"  省份数量: 原始 {orig['provinces']}, 修改后 {mod['provinces']}, 差异: {mod['provinces'] - orig['provinces']:+d}")
            print(f"  人口ID块: 原始 {orig['pop_ids']}, 修改后 {mod['pop_ids']}, 差异: {mod['pop_ids'] - orig['pop_ids']:+d}")
            print(f"  population块: 原始 {orig['pop_blocks']}, 修改后 {mod['pop_blocks']}, 差异: {mod['pop_blocks'] - orig['pop_blocks']:+d}")
            print(f"  总人口: 原始 {orig['non_zero_pop']:,.0f}, 修改后 {mod['non_zero_pop']:,.0f}, 差异: {mod['non_zero_pop'] - orig['non_zero_pop']:+,.0f}")
            
            # 判断问题所在
            if abs(mod['provinces'] - orig['provinces']) > 0:
                print(f"  ❌ 省份数量发生变化！")
            elif abs(mod['pop_blocks'] - orig['pop_blocks']) > 0:
                print(f"  ❌ population块数量发生变化！")
            elif abs(mod['pop_ids'] - orig['pop_ids']) > 100:
                print(f"  ❌ 人口ID块数量显著变化！")
            elif abs(mod['non_zero_pop'] - orig['non_zero_pop']) > 1000000:
                print(f"  ❌ 总人口显著变化！")
            else:
                print(f"  ❓ 数据结构看起来正常，问题可能在别处")

if __name__ == "__main__":
    find_real_population_issue()
