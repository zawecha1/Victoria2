#!/usr/bin/env python3
"""
分析autosave.v2和test_civilized_simple_143915.v2之间的关键差异
重点检查人口数据
"""

import re
import os

def analyze_population_data(filename):
    """分析文件中的人口数据"""
    print(f"\n🔍 分析 {filename} 中的人口数据")
    
    if not os.path.exists(filename):
        print(f"❌ 文件不存在: {filename}")
        return None
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        print(f"📂 文件大小: {len(content):,} 字符")
        
        # 分析人口相关的关键指标
        analysis = {}
        
        # 1. 人口块数量 - 查找省份中的人口组
        pop_blocks = re.findall(r'\s+(\d+)\s*=\s*\{[^{}]*?size\s*=\s*[\d.]+[^{}]*?\}', content, re.DOTALL)
        analysis['pop_blocks'] = len(pop_blocks)
        
        # 2. size字段 - 人口数量
        size_matches = re.findall(r'size\s*=\s*([\d.]+)', content)
        analysis['size_fields'] = len(size_matches)
        if size_matches:
            sizes = [float(x) for x in size_matches]
            analysis['total_population'] = sum(sizes)
            analysis['avg_pop_size'] = sum(sizes) / len(sizes)
            analysis['max_pop_size'] = max(sizes)
        else:
            analysis['total_population'] = 0
            analysis['avg_pop_size'] = 0
            analysis['max_pop_size'] = 0
        
        # 3. 省份数量
        province_blocks = re.findall(r'(\d{3,4})\s*=\s*\{[^{}]*?trade_goods\s*=', content)
        analysis['provinces'] = len(province_blocks)
        
        # 4. 人口类型统计
        pop_types = re.findall(r'type\s*=\s*(\d+)', content)
        analysis['pop_type_entries'] = len(pop_types)
        
        # 5. 文化统计
        cultures = re.findall(r'culture\s*=\s*(\w+)', content)
        analysis['culture_entries'] = len(cultures)
        unique_cultures = list(set(cultures))
        analysis['unique_cultures'] = len(unique_cultures)
        
        # 6. 宗教统计
        religions = re.findall(r'religion\s*=\s*(\w+)', content)
        analysis['religion_entries'] = len(religions)
        
        # 7. 意识形态统计
        ideologies = re.findall(r'ideology\s*=\s*\{[^{}]*?\}', content, re.DOTALL)
        analysis['ideology_blocks'] = len(ideologies)
        
        # 8. 检查是否有空的人口块
        empty_pops = re.findall(r'\d+\s*=\s*\{\s*\}', content)
        analysis['empty_pop_blocks'] = len(empty_pops)
        
        print(f"📊 人口数据统计:")
        print(f"  人口块数量: {analysis['pop_blocks']}")
        print(f"  size字段数量: {analysis['size_fields']}")
        print(f"  总人口数: {analysis['total_population']:,.0f}")
        print(f"  平均人口大小: {analysis['avg_pop_size']:.1f}")
        print(f"  最大人口大小: {analysis['max_pop_size']:,.0f}")
        print(f"  省份数量: {analysis['provinces']}")
        print(f"  人口类型条目: {analysis['pop_type_entries']}")
        print(f"  文化条目: {analysis['culture_entries']} (唯一: {analysis['unique_cultures']})")
        print(f"  宗教条目: {analysis['religion_entries']}")
        print(f"  意识形态块: {analysis['ideology_blocks']}")
        print(f"  空人口块: {analysis['empty_pop_blocks']}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ 分析 {filename} 时出错: {e}")
        return None

def compare_files():
    """比较两个文件的差异"""
    print("🔍 比较 autosave.v2 和 test_civilized_simple_143915.v2")
    print("重点检查人口数据差异")
    print("="*80)
    
    # 分析两个文件
    autosave_data = analyze_population_data("autosave.v2")
    test_data = analyze_population_data("test_civilized_simple_143915.v2")
    
    if autosave_data and test_data:
        print(f"\n" + "="*80)
        print("📊 关键差异对比:")
        print("="*80)
        
        # 比较关键指标
        comparisons = [
            ('总人口数', 'total_population'),
            ('人口块数量', 'pop_blocks'),
            ('size字段数量', 'size_fields'),
            ('省份数量', 'provinces'),
            ('人口类型条目', 'pop_type_entries'),
            ('文化条目', 'culture_entries'),
            ('宗教条目', 'religion_entries'),
            ('意识形态块', 'ideology_blocks'),
            ('空人口块', 'empty_pop_blocks')
        ]
        
        print(f"{'指标':<15} {'autosave.v2':<15} {'test_file':<15} {'差异':<15} {'状态'}")
        print("-" * 80)
        
        critical_issues = []
        
        for name, key in comparisons:
            autosave_val = autosave_data.get(key, 0)
            test_val = test_data.get(key, 0)
            diff = autosave_val - test_val
            
            if key == 'total_population':
                status = "❌ 严重" if abs(diff) > 1000000 else "⚠️ 注意" if abs(diff) > 100000 else "✅ 正常"
                if abs(diff) > 100000:
                    critical_issues.append(f"人口数差异: {diff:+,.0f}")
            elif key in ['pop_blocks', 'size_fields'] and abs(diff) > 100:
                status = "❌ 严重"
                critical_issues.append(f"{name}差异: {diff:+d}")
            elif abs(diff) > 10:
                status = "⚠️ 注意"
            else:
                status = "✅ 正常"
            
            print(f"{name:<15} {autosave_val:<15,.0f} {test_val:<15,.0f} {diff:<+15,.0f} {status}")
        
        print(f"\n🚨 关键问题分析:")
        if critical_issues:
            for issue in critical_issues:
                print(f"  ❌ {issue}")
            
            # 检查可能的原因
            print(f"\n🔍 可能的问题原因:")
            if autosave_data['total_population'] < test_data['total_population'] * 0.5:
                print(f"  💀 autosave.v2 人口大量丢失!")
                print(f"  📉 人口丢失比例: {(1 - autosave_data['total_population']/test_data['total_population'])*100:.1f}%")
                
            if autosave_data['empty_pop_blocks'] > test_data['empty_pop_blocks']:
                print(f"  🕳️ autosave.v2 有更多空的人口块")
                
            if autosave_data['size_fields'] < test_data['size_fields']:
                print(f"  📊 autosave.v2 丢失了 {test_data['size_fields'] - autosave_data['size_fields']} 个size字段")
                
        else:
            print(f"  ✅ 没有发现关键人口数据问题")
        
        return autosave_data, test_data
    else:
        print("❌ 无法完成比较分析")
        return None, None

if __name__ == "__main__":
    compare_files()
