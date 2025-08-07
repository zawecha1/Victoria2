"""
详细验证金钱修改功能的准确性
检查具体的中国和非中国省份的金钱修改情况
"""

import re
from victoria2_main_modifier import Victoria2Modifier

def detailed_money_verification():
    print("🔍 详细验证金钱修改功能...")
    
    # 读取修改后的文件
    filename = "ChinaUseIt_money_test.v2"
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        print(f"📄 已读取文件: {filename}")
        
        # 创建修改器实例来获取省份映射
        original_modifier = Victoria2Modifier("ChinaUseIt.v2")
        province_owners = original_modifier._build_province_owner_mapping()
        
        # 统计不同类型的金钱值
        money_stats = {
            'chinese_high_money': 0,    # 中国人口高金额money
            'chinese_high_bank': 0,     # 中国人口高金额bank
            'chinese_other_money': 0,   # 中国人口其他金额money
            'chinese_other_bank': 0,    # 中国人口其他金额bank
            'non_chinese_zero_money': 0, # 非中国人口零金额money
            'non_chinese_zero_bank': 0,  # 非中国人口零金额bank
            'non_chinese_other_money': 0, # 非中国人口其他金额money
            'non_chinese_other_bank': 0   # 非中国人口其他金额bank
        }
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(content))
        
        print(f"🗺️ 检查 {len(province_matches)} 个省份...")
        
        chinese_provinces_checked = 0
        non_chinese_provinces_checked = 0
        
        for i, match in enumerate(province_matches[:10]):  # 检查前10个省份作为样本
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 找到省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+10000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 5000
            
            province_content = content[start_pos:end_pos]
            owner = province_owners.get(province_id, "")
            
            # 统计金钱值
            money_values = re.findall(r'money=([\d.]+)', province_content)
            bank_values = re.findall(r'bank=([\d.]+)', province_content)
            
            if owner == "CHI":
                chinese_provinces_checked += 1
                print(f"  🇨🇳 省份 {province_id} (中国):")
                
                for value in money_values:
                    if float(value) == 9999999999.0:
                        money_stats['chinese_high_money'] += 1
                    else:
                        money_stats['chinese_other_money'] += 1
                        print(f"    ⚠️  发现非目标money值: {value}")
                
                for value in bank_values:
                    if float(value) == 9999999999.0:
                        money_stats['chinese_high_bank'] += 1
                    else:
                        money_stats['chinese_other_bank'] += 1
                        print(f"    ⚠️  发现非目标bank值: {value}")
                
                print(f"    💰 Money字段: {len(money_values)} 个, Bank字段: {len(bank_values)} 个")
            
            elif owner and owner != "CHI":
                non_chinese_provinces_checked += 1
                print(f"  🌍 省份 {province_id} ({owner}):")
                
                for value in money_values:
                    if float(value) == 0.0:
                        money_stats['non_chinese_zero_money'] += 1
                    else:
                        money_stats['non_chinese_other_money'] += 1
                        print(f"    ⚠️  发现非零money值: {value}")
                
                for value in bank_values:
                    if float(value) == 0.0:
                        money_stats['non_chinese_zero_bank'] += 1
                    else:
                        money_stats['non_chinese_other_bank'] += 1
                        print(f"    ⚠️  发现非零bank值: {value}")
                
                print(f"    💸 Money字段: {len(money_values)} 个, Bank字段: {len(bank_values)} 个")
        
        print(f"\n📊 样本验证统计 (前10个省份):")
        print(f"  🇨🇳 中国省份检查: {chinese_provinces_checked} 个")
        print(f"  🌍 非中国省份检查: {non_chinese_provinces_checked} 个")
        
        print(f"\n💰 金钱字段统计:")
        print(f"  🇨🇳 中国人口:")
        print(f"    ✅ Money = 9,999,999,999: {money_stats['chinese_high_money']} 个")
        print(f"    ✅ Bank = 9,999,999,999: {money_stats['chinese_high_bank']} 个")
        if money_stats['chinese_other_money'] > 0:
            print(f"    ⚠️  Money ≠ 9,999,999,999: {money_stats['chinese_other_money']} 个")
        if money_stats['chinese_other_bank'] > 0:
            print(f"    ⚠️  Bank ≠ 9,999,999,999: {money_stats['chinese_other_bank']} 个")
        
        print(f"  🌍 非中国人口:")
        print(f"    ✅ Money = 0: {money_stats['non_chinese_zero_money']} 个")
        print(f"    ✅ Bank = 0: {money_stats['non_chinese_zero_bank']} 个")
        if money_stats['non_chinese_other_money'] > 0:
            print(f"    ⚠️  Money ≠ 0: {money_stats['non_chinese_other_money']} 个")
        if money_stats['non_chinese_other_bank'] > 0:
            print(f"    ⚠️  Bank ≠ 0: {money_stats['non_chinese_other_bank']} 个")
        
        # 计算成功率
        total_chinese_money = money_stats['chinese_high_money'] + money_stats['chinese_other_money']
        total_chinese_bank = money_stats['chinese_high_bank'] + money_stats['chinese_other_bank']
        total_non_chinese_money = money_stats['non_chinese_zero_money'] + money_stats['non_chinese_other_money']
        total_non_chinese_bank = money_stats['non_chinese_zero_bank'] + money_stats['non_chinese_other_bank']
        
        chinese_money_success = (money_stats['chinese_high_money'] / total_chinese_money * 100) if total_chinese_money > 0 else 0
        chinese_bank_success = (money_stats['chinese_high_bank'] / total_chinese_bank * 100) if total_chinese_bank > 0 else 0
        non_chinese_money_success = (money_stats['non_chinese_zero_money'] / total_non_chinese_money * 100) if total_non_chinese_money > 0 else 0
        non_chinese_bank_success = (money_stats['non_chinese_zero_bank'] / total_non_chinese_bank * 100) if total_non_chinese_bank > 0 else 0
        
        print(f"\n📈 修改成功率:")
        print(f"  🇨🇳 中国人口 Money: {chinese_money_success:.1f}%")
        print(f"  🇨🇳 中国人口 Bank: {chinese_bank_success:.1f}%")
        print(f"  🌍 非中国人口 Money: {non_chinese_money_success:.1f}%")
        print(f"  🌍 非中国人口 Bank: {non_chinese_bank_success:.1f}%")
        
        # 总体评估
        overall_success = (chinese_money_success + chinese_bank_success + non_chinese_money_success + non_chinese_bank_success) / 4
        print(f"\n🎯 总体成功率: {overall_success:.1f}%")
        
        if overall_success >= 95:
            print("✅ 验证结果：优秀！金钱修改功能工作正常")
        elif overall_success >= 80:
            print("⚠️  验证结果：良好，但可能需要进一步优化")
        else:
            print("❌ 验证结果：需要检查和修复问题")
        
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    detailed_money_verification()
