#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import sys

# 强制重新加载模块
if 'victoria2_main_modifier' in sys.modules:
    importlib.reload(sys.modules['victoria2_main_modifier'])

from victoria2_main_modifier import Victoria2Modifier

# 测试中国人口金钱修改功能 (选项6)
print("🎮 测试维多利亚2中国人口金钱修改功能 (选项6)")
print("="*60)

modifier = Victoria2Modifier()
modifier.debug_mode = True  # 开启调试模式以查看详细输出

# 加载存档文件
filename = 'China1836_02_20.v2'
print(f"📁 加载存档文件: {filename}")
modifier.load_file(filename)

# 执行金钱修改 (money 和 bank 都设为 9999999)
print("\n💰 开始执行金钱修改...")
result = modifier.modify_chinese_population_money(target_money=9999999.0)

if result:
    print(f"\n✅ 金钱修改成功!")
    print(f"📊 修改统计:")
    print(f"   - 金钱字段修改: {modifier.money_changes} 个")
    
    # 保存修改后的文件
    output_filename = 'China1836_02_20_money_modified.v2'
    modifier.save_file(output_filename)
    print(f"💾 已保存修改后的文件: {output_filename}")
else:
    print("❌ 未进行任何修改")

print("\n🎉 测试完成!")
