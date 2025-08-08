"""
测试修改后的人口金钱和需求满足度功能
"""

import re

def test_money_and_needs_modification():
    """测试金钱和需求满足度修改功能"""
    
    # 模拟一个省份的人口数据
    sample_province_content = '''1612={
    {
        farmers={
            size=12345
            culture=beifaren
            religion=mahayana
            money=1000.50000
            bank=500.25000
            literacy=0.85000
            luxury_needs=0.30000
            everyday_needs=0.70000
            life_needs=0.90000
        }
        clerks={
            size=5678
            culture=beifaren
            religion=mahayana
            money=2000.75000
            bank=1000.12500
            literacy=0.95000
            luxury_needs=0.40000
            everyday_needs=0.80000
            life_needs=0.95000
        }
    }
}'''
    
    print("🧪 测试金钱和需求满足度修改功能")
    print("="*60)
    
    # 显示原始数据
    print("📋 原始人口数据:")
    money_matches = re.findall(r'money=([\d.]+)', sample_province_content)
    bank_matches = re.findall(r'bank=([\d.]+)', sample_province_content)
    luxury_matches = re.findall(r'luxury_needs=([\d.]+)', sample_province_content)
    everyday_matches = re.findall(r'everyday_needs=([\d.]+)', sample_province_content)
    life_matches = re.findall(r'life_needs=([\d.]+)', sample_province_content)
    
    print(f"  Money: {money_matches}")
    print(f"  Bank: {bank_matches}")
    print(f"  Luxury needs: {luxury_matches}")
    print(f"  Everyday needs: {everyday_matches}")
    print(f"  Life needs: {life_matches}")
    
    # 模拟修改过程 - 中国人口 (设为高值)
    def test_chinese_modification(content, target_money, target_needs):
        """测试中国人口修改"""
        money_pattern = r'money=([\d.]+)'
        bank_pattern = r'bank=([\d.]+)'
        luxury_needs_pattern = r'luxury_needs=([\d.]+)'
        everyday_needs_pattern = r'everyday_needs=([\d.]+)'
        life_needs_pattern = r'life_needs=([\d.]+)'
        
        # 依次修改所有相关字段
        modified_content = re.sub(money_pattern, f'money={target_money:.5f}', content)
        modified_content = re.sub(bank_pattern, f'bank={target_money:.5f}', modified_content)
        modified_content = re.sub(luxury_needs_pattern, f'luxury_needs={target_needs:.5f}', modified_content)
        modified_content = re.sub(everyday_needs_pattern, f'everyday_needs={target_needs:.5f}', modified_content)
        modified_content = re.sub(life_needs_pattern, f'life_needs={target_needs:.5f}', modified_content)
        
        return modified_content
    
    # 测试中国人口修改
    print("\n🇨🇳 测试中国人口修改 (金钱=9,999,999,999, 需求=1.0):")
    chinese_modified = test_chinese_modification(sample_province_content, 9999999999.0, 1.0)
    
    # 检查修改结果
    new_money = re.findall(r'money=([\d.]+)', chinese_modified)
    new_bank = re.findall(r'bank=([\d.]+)', chinese_modified)
    new_luxury = re.findall(r'luxury_needs=([\d.]+)', chinese_modified)
    new_everyday = re.findall(r'everyday_needs=([\d.]+)', chinese_modified)
    new_life = re.findall(r'life_needs=([\d.]+)', chinese_modified)
    
    print(f"  Money: {new_money}")
    print(f"  Bank: {new_bank}")
    print(f"  Luxury needs: {new_luxury}")
    print(f"  Everyday needs: {new_everyday}")
    print(f"  Life needs: {new_life}")
    
    # 验证修改效果
    all_money_correct = all(float(m) == 9999999999.0 for m in new_money)
    all_bank_correct = all(float(b) == 9999999999.0 for b in new_bank)
    all_luxury_correct = all(float(l) == 1.0 for l in new_luxury)
    all_everyday_correct = all(float(e) == 1.0 for e in new_everyday)
    all_life_correct = all(float(lf) == 1.0 for lf in new_life)
    
    if all([all_money_correct, all_bank_correct, all_luxury_correct, all_everyday_correct, all_life_correct]):
        print("✅ 中国人口修改成功！所有字段都设置正确")
    else:
        print("❌ 中国人口修改失败")
    
    # 测试非中国人口修改
    print("\n🌍 测试非中国人口修改 (金钱=0, 需求=0.0):")
    non_chinese_modified = test_chinese_modification(sample_province_content, 0.0, 0.0)
    
    # 检查修改结果
    zero_money = re.findall(r'money=([\d.]+)', non_chinese_modified)
    zero_bank = re.findall(r'bank=([\d.]+)', non_chinese_modified)
    zero_luxury = re.findall(r'luxury_needs=([\d.]+)', non_chinese_modified)
    zero_everyday = re.findall(r'everyday_needs=([\d.]+)', non_chinese_modified)
    zero_life = re.findall(r'life_needs=([\d.]+)', non_chinese_modified)
    
    print(f"  Money: {zero_money}")
    print(f"  Bank: {zero_bank}")
    print(f"  Luxury needs: {zero_luxury}")
    print(f"  Everyday needs: {zero_everyday}")
    print(f"  Life needs: {zero_life}")
    
    # 验证修改效果
    all_money_zero = all(float(m) == 0.0 for m in zero_money)
    all_bank_zero = all(float(b) == 0.0 for b in zero_bank)
    all_luxury_zero = all(float(l) == 0.0 for l in zero_luxury)
    all_everyday_zero = all(float(e) == 0.0 for e in zero_everyday)
    all_life_zero = all(float(lf) == 0.0 for lf in zero_life)
    
    if all([all_money_zero, all_bank_zero, all_luxury_zero, all_everyday_zero, all_life_zero]):
        print("✅ 非中国人口修改成功！所有字段都清零")
    else:
        print("❌ 非中国人口修改失败")
    
    print("\n🎉 功能测试完成！")
    return True

if __name__ == "__main__":
    test_money_and_needs_modification()
