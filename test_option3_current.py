#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的选项3功能：中国=0，其他=10
"""

import re
import sys
import os

def test_option3_functionality():
    """测试选项3的完整功能"""
    print("🧪 测试选项3：人口斗争性修改 (中国=0, 其他=10)")
    print("=" * 60)
    
    filename = "China1837_01_24.v2"
    
    # 读取文件
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        print(f"✅ 文件读取成功，大小: {len(content):,} 字符")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return False
    
    # 统计当前所有省份的loyalty_value状态
    print("\n🔍 分析当前loyalty_value状态...")
    
    # 中国省份
    chinese_provinces = set(str(i) for i in range(2687, 2741))
    
    # 查找所有省份
    province_pattern = r'^(\d+)=\s*{'
    province_matches = list(re.finditer(province_pattern, content, re.MULTILINE))
    
    print(f"📊 总共找到 {len(province_matches)} 个省份")
    
    # 分析每个省份的loyalty_value
    chinese_loyalty_stats = {"0.0": 0, "10.0": 0, "other": 0, "none": 0}
    non_chinese_loyalty_stats = {"0.0": 0, "10.0": 0, "other": 0, "none": 0}
    
    chinese_provinces_found = 0
    non_chinese_provinces_found = 0
    
    for i, match in enumerate(province_matches):
        province_id = match.group(1)
        start_pos = match.start()
        
        # 找到这个省份的结束位置
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            end_pos = len(content)
        
        province_content = content[start_pos:end_pos]
        
        # 查找loyalty_value
        loyalty_pattern = r'loyalty_value=([\d.]+)'
        loyalty_matches = re.findall(loyalty_pattern, province_content)
        
        is_chinese = province_id in chinese_provinces
        
        if is_chinese:
            chinese_provinces_found += 1
            stats = chinese_loyalty_stats
        else:
            non_chinese_provinces_found += 1
            stats = non_chinese_loyalty_stats
        
        if not loyalty_matches:
            stats["none"] += 1
        else:
            for value in loyalty_matches:
                val = float(value)
                if abs(val - 0.0) < 0.001:
                    stats["0.0"] += 1
                elif abs(val - 10.0) < 0.001:
                    stats["10.0"] += 1
                else:
                    stats["other"] += 1
    
    print(f"\n📊 中国省份 ({chinese_provinces_found} 个省份):")
    print(f"  - loyalty_value=0.0:   {chinese_loyalty_stats['0.0']} 个")
    print(f"  - loyalty_value=10.0:  {chinese_loyalty_stats['10.0']} 个")
    print(f"  - 其他值:               {chinese_loyalty_stats['other']} 个")
    print(f"  - 无loyalty_value:     {chinese_loyalty_stats['none']} 个")
    
    print(f"\n📊 非中国省份 ({non_chinese_provinces_found} 个省份):")
    print(f"  - loyalty_value=0.0:   {non_chinese_loyalty_stats['0.0']} 个")
    print(f"  - loyalty_value=10.0:  {non_chinese_loyalty_stats['10.0']} 个")
    print(f"  - 其他值:               {non_chinese_loyalty_stats['other']} 个")
    print(f"  - 无loyalty_value:     {non_chinese_loyalty_stats['none']} 个")
    
    # 分析是否符合"中国=0，其他=10"的要求
    print(f"\n✅ 选项3功能评估:")
    
    # 中国省份应该全为0
    chinese_correct = chinese_loyalty_stats["0.0"]
    chinese_total = sum(chinese_loyalty_stats.values()) - chinese_loyalty_stats["none"]
    chinese_ok = chinese_total == 0 or chinese_correct == chinese_total
    
    # 非中国省份应该全为10
    non_chinese_correct = non_chinese_loyalty_stats["10.0"] 
    non_chinese_total = sum(non_chinese_loyalty_stats.values()) - non_chinese_loyalty_stats["none"]
    non_chinese_ok = non_chinese_total == 0 or non_chinese_correct == non_chinese_total
    
    print(f"中国省份 (应该全为0):    {'✅' if chinese_ok else '❌'} {chinese_correct}/{chinese_total}")
    print(f"非中国省份 (应该全为10):  {'✅' if non_chinese_ok else '❌'} {non_chinese_correct}/{non_chinese_total}")
    
    if chinese_ok and non_chinese_ok:
        print(f"\n🎉 选项3功能完全正确!")
        return True
    else:
        print(f"\n⚠️ 选项3功能需要修复!")
        
        if not chinese_ok:
            print(f"   - 中国省份问题: {chinese_total - chinese_correct} 个loyalty_value不是0")
        if not non_chinese_ok:
            print(f"   - 非中国省份问题: {non_chinese_total - non_chinese_correct} 个loyalty_value不是10")
        
        return False

if __name__ == "__main__":
    success = test_option3_functionality()
    
    if not success:
        print(f"\n🔧 建议:")
        print(f"  1. 当前代码只处理中国省份 -> 0")
        print(f"  2. 需要添加处理非中国省份 -> 10 的逻辑")
        print(f"  3. 运行修复脚本来完善功能")
