#!/usr/bin/env python3
"""
验证autosave.v2的文明化状态是否正确
"""

import re
import os

def verify_current_file():
    """验证当前文件的正确性"""
    print("🔍 验证 autosave.v2 的文明化状态")
    print("="*60)
    
    filename = "autosave.v2"
    
    if not os.path.exists(filename):
        print(f"❌ 文件不存在: {filename}")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        print(f"📂 文件大小: {len(content):,} 字符")
        
        # 统计总的civilized字段
        all_yes = re.findall(r'civilized\s*=\s*"?yes"?', content, re.IGNORECASE)
        all_no = re.findall(r'civilized\s*=\s*"?no"?', content, re.IGNORECASE)
        
        print(f"\n📊 总体统计:")
        print(f"  civilized=\"yes\": {len(all_yes)}")
        print(f"  civilized=\"no\": {len(all_no)}")
        print(f"  总计: {len(all_yes) + len(all_no)}")
        
        # 查找所有国家的civilized状态
        # 使用更精确的模式匹配国家块
        country_pattern = r'([A-Z]{2,3})\s*=\s*\{[^{}]*?civilized\s*=\s*"?([^"\s}]+)"?'
        countries = re.findall(country_pattern, content, re.IGNORECASE | re.DOTALL)
        
        print(f"\n🌍 国家级别分析:")
        print(f"  找到 {len(countries)} 个国家的civilized状态")
        
        # 分析各个国家
        yes_countries = []
        no_countries = []
        china_status = None
        
        for country, status in countries:
            if status.lower() == 'yes':
                yes_countries.append(country)
                if country == 'CHI':
                    china_status = 'yes'
            elif status.lower() == 'no':
                no_countries.append(country)
                if country == 'CHI':
                    china_status = 'no'
        
        print(f"\n📋 详细结果:")
        print(f"  文明化国家 (yes): {len(yes_countries)}")
        if yes_countries:
            print(f"    国家列表: {yes_countries}")
        
        print(f"  非文明化国家 (no): {len(no_countries)}")
        print(f"    数量: {len(no_countries)} (不显示完整列表)")
        
        print(f"\n🇨🇳 中国状态检查:")
        print(f"  CHI civilized状态: {china_status if china_status else '未找到'}")
        
        # 验证结果
        print(f"\n✅ 验证结果:")
        
        expected_behavior = True
        issues = []
        
        # 检查1: 中国应该保持文明化状态
        if china_status != 'yes':
            expected_behavior = False
            issues.append(f"❌ 中国(CHI)应该是civilized=\"yes\"，但实际是\"{china_status}\"")
        else:
            print("  ✅ 中国(CHI)正确保持了civilized=\"yes\"状态")
        
        # 检查2: 应该只有中国是yes状态(或者很少的yes国家)
        if len(yes_countries) == 1 and 'CHI' in yes_countries:
            print("  ✅ 只有中国是文明化状态，其他国家都正确改为非文明化")
        elif len(yes_countries) <= 3:  # 允许少量文明化国家
            print(f"  ⚠️ 有 {len(yes_countries)} 个文明化国家: {yes_countries}")
            print("     这可能是正常的，因为某些国家可能原本就应该保持文明化")
        else:
            expected_behavior = False
            issues.append(f"❌ 太多国家仍然是文明化状态 ({len(yes_countries)} 个)")
        
        # 检查3: 大部分国家应该是no状态
        if len(no_countries) >= 200:  # 假设至少200个国家应该是非文明化
            print(f"  ✅ 大部分国家 ({len(no_countries)}) 正确设为非文明化状态")
        else:
            issues.append(f"⚠️ 非文明化国家数量较少 ({len(no_countries)})")
        
        # 最终判断
        if expected_behavior and not issues:
            print(f"\n🎉 验证通过! autosave.v2 的文明化状态是正确的")
            print("主程序的文明化修改功能工作正常")
            return True
        else:
            print(f"\n⚠️ 发现问题:")
            for issue in issues:
                print(f"  {issue}")
            return False
        
    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")
        return False

if __name__ == "__main__":
    verify_current_file()
