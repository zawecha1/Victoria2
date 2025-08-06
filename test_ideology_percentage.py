#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import sys

# 强制重新加载模块
if 'victoria2_main_modifier' in sys.modules:
    importlib.reload(sys.modules['victoria2_main_modifier'])

from victoria2_main_modifier import Victoria2Modifier

def test_ideology_percentage_system():
    """测试更新后的意识形态百分比系统"""
    
    print("🎭 测试意识形态百分比系统")
    print("="*60)
    
    # 创建修改器实例
    modifier = Victoria2Modifier()
    modifier.debug_mode = True
    
    # 测试样本数据 - 基于您提供的结构
    sample_ideology_content = """1=7.89395
2=3.94125
3=36.15530
4=19.19250
5=1.22287
6=30.37112
7=1.22287"""
    
    print("📊 原始意识形态分布:")
    print("1=7.89395  (Reactionary - 反动派)")
    print("2=3.94125  (Fascist - 法西斯)")
    print("3=36.15530 (Conservative - 保守派)")
    print("4=19.19250 (Socialist - 社会主义)")
    print("5=1.22287  (Anarcho-Liberal - 无政府自由派)")
    print("6=30.37112 (Liberal - 自由派)")
    print("7=1.22287  (Communist - 共产主义)")
    
    # 计算原始总和
    original_values = [7.89395, 3.94125, 36.15530, 19.19250, 1.22287, 30.37112, 1.22287]
    original_total = sum(original_values)
    print(f"\n📈 原始百分比总和: {original_total:.5f}%")
    
    print("\n🔄 执行意识形态转换...")
    result = modifier._modify_ideology_distribution(sample_ideology_content)
    
    print(f"\n✅ 转换后的意识形态分布:")
    print(result)
    
    # 解析转换后的结果
    import re
    ideology_pairs = re.findall(r'(\d+)=([\d.]+)', result)
    new_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
    new_total = sum(new_dist.values())
    
    print(f"\n📊 转换后百分比总和: {new_total:.5f}%")
    
    # 验证转换规则
    print(f"\n🎯 转换验证:")
    print(f"Conservative(3): {new_dist.get(3, 0):.5f}%")
    print(f"Liberal(6): {new_dist.get(6, 0):.5f}%")
    
    # 检查应该为0的意识形态
    should_be_zero = [1, 2, 4, 5, 7]
    for ideology_id in should_be_zero:
        value = new_dist.get(ideology_id, 0)
        if value > 0:
            print(f"⚠️ 意识形态 {ideology_id} 应该为0，但是值为 {value}")
        else:
            print(f"✅ 意识形态 {ideology_id} 正确设为0")
    
    # 验证百分比总和
    if abs(new_total - 100.0) < 0.00001:
        print(f"\n✅ 百分比总和验证通过: {new_total:.5f}%")
    else:
        print(f"\n❌ 百分比总和验证失败: {new_total:.5f}% (应该是100%)")

if __name__ == "__main__":
    test_ideology_percentage_system()
