#!/usr/bin/env python3
"""
比较两个存档文件的civilized字段差异
"""

import re
import os

def analyze_civilized_fields(filename):
    """分析文件中的civilized字段"""
    print(f"\n🔍 分析文件: {filename}")
    
    if not os.path.exists(filename):
        print(f"❌ 文件不存在: {filename}")
        return None
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        print(f"📂 文件大小: {len(content):,} 字符")
        
        # 统计civilized字段
        civilized_yes = re.findall(r'civilized\s*=\s*"?yes"?', content, re.IGNORECASE)
        civilized_no = re.findall(r'civilized\s*=\s*"?no"?', content, re.IGNORECASE)
        
        print(f"📊 Civilized字段统计:")
        print(f"  civilized=\"yes\": {len(civilized_yes)}")
        print(f"  civilized=\"no\": {len(civilized_no)}")
        print(f"  总计: {len(civilized_yes) + len(civilized_no)}")
        
        # 查找带有国家标识符的civilized字段
        print(f"\n🌍 国家civilized状态样本:")
        
        # 查找国家块中的civilized字段
        country_pattern = r'([A-Z]{2,3})\s*=\s*\{[^{}]*civilized\s*=\s*"?([^"\s}]+)"?[^{}]*\}'
        countries = re.findall(country_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if countries:
            print(f"  找到 {len(countries)} 个国家的civilized状态")
            
            # 按状态分组
            yes_countries = [c[0] for c in countries if c[1].lower() == 'yes']
            no_countries = [c[0] for c in countries if c[1].lower() == 'no']
            
            print(f"  文明化国家 (yes): {len(yes_countries)}")
            if yes_countries:
                print(f"    前10个: {yes_countries[:10]}")
            
            print(f"  非文明化国家 (no): {len(no_countries)}")
            if no_countries:
                print(f"    前10个: {no_countries[:10]}")
            
            # 检查中国状态
            china_status = None
            for country, status in countries:
                if country == 'CHI':
                    china_status = status
                    break
            
            print(f"  🇨🇳 中国(CHI)状态: {china_status if china_status else '未找到'}")
        
        return {
            'total_yes': len(civilized_yes),
            'total_no': len(civilized_no),
            'countries': countries,
            'china_status': china_status if 'china_status' in locals() else None
        }
        
    except Exception as e:
        print(f"❌ 分析文件时出错: {e}")
        return None

def compare_files():
    """比较两个文件的差异"""
    print("🔍 比较 autosave.v2 和 test_civilized_simple_143915.v2")
    print("="*80)
    
    # 分析原始文件
    original_data = analyze_civilized_fields("autosave.v2")
    
    # 分析测试文件
    test_data = analyze_civilized_fields("test_civilized_simple_143915.v2")
    
    if original_data and test_data:
        print(f"\n" + "="*80)
        print("📊 对比结果:")
        print("="*80)
        
        print(f"文件                          yes    no    总计")
        print(f"autosave.v2                  {original_data['total_yes']:3d}   {original_data['total_no']:3d}   {original_data['total_yes'] + original_data['total_no']:3d}")
        print(f"test_civilized_simple_*.v2   {test_data['total_yes']:3d}   {test_data['total_no']:3d}   {test_data['total_yes'] + test_data['total_no']:3d}")
        
        print(f"\n🔍 差异分析:")
        yes_diff = original_data['total_yes'] - test_data['total_yes']
        no_diff = original_data['total_no'] - test_data['total_no']
        
        print(f"  yes字段差异: {yes_diff:+d}")
        print(f"  no字段差异: {no_diff:+d}")
        
        if yes_diff > 0:
            print(f"⚠️ autosave.v2 比测试文件多了 {yes_diff} 个 civilized=\"yes\"")
            print("这意味着主程序的文明化修改可能没有正常工作")
        elif yes_diff < 0:
            print(f"✅ autosave.v2 比测试文件少了 {-yes_diff} 个 civilized=\"yes\"")
            print("文明化修改似乎生效了")
        else:
            print("🤔 两个文件的yes数量相同，可能修改没有生效")
        
        return original_data, test_data
    else:
        print("❌ 无法比较文件")
        return None, None

if __name__ == "__main__":
    compare_files()
