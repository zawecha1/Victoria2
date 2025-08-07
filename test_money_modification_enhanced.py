"""
测试修改后的 modify_chinese_population_money 功能
验证中国人口金钱设为9,999,999,999，非中国人口金钱清零
"""

from victoria2_main_modifier import Victoria2Modifier

def test_money_modification():
    print("🧪 测试人口金钱修改功能...")
    
    # 使用实际的存档文件进行测试
    save_file = "ChinaUseIt.v2"
    
    try:
        # 创建修改器实例
        modifier = Victoria2Modifier(save_file)
        
        print("\n📊 修改前状态分析...")
        
        # 执行金钱修改
        print("\n🚀 开始执行金钱修改...")
        result = modifier.modify_chinese_population_money(
            chinese_money=9999999999.0,
            non_chinese_money=0.0
        )
        
        print(f"\n📈 修改结果:")
        print(f"  ✅ 功能状态: {'成功' if result else '失败'}")
        print(f"  📊 总修改次数: {modifier.money_changes}")
        
        if result:
            # 保存修改后的文件
            output_file = "ChinaUseIt_money_test.v2"
            with open(output_file, 'w', encoding='utf-8-sig') as f:
                f.write(modifier.content)
            print(f"💾 修改后的文件已保存为: {output_file}")
            
            # 简单验证：检查是否有目标金额
            chinese_money_count = modifier.content.count('money=9999999999.00000')
            chinese_bank_count = modifier.content.count('bank=9999999999.00000')
            zero_money_count = modifier.content.count('money=0.00000')
            zero_bank_count = modifier.content.count('bank=0.00000')
            
            print(f"\n🔍 简单验证结果:")
            print(f"  💰 找到 {chinese_money_count} 个 money=9999999999.00000")
            print(f"  🏦 找到 {chinese_bank_count} 个 bank=9999999999.00000")
            print(f"  💸 找到 {zero_money_count} 个 money=0.00000")
            print(f"  🏦 找到 {zero_bank_count} 个 bank=0.00000")
            
            if chinese_money_count > 0 and zero_money_count > 0:
                print("✅ 验证通过：同时发现了中国人口的高金额和非中国人口的零金额")
            else:
                print("⚠️  验证警告：可能需要进一步检查修改结果")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_money_modification()
