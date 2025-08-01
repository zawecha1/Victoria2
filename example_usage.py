#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 修改器 - 使用示例
演示如何以编程方式使用统一修改工具
"""

from victoria2_modifier import Victoria2Modifier

def example_usage():
    """演示统一修改工具的使用"""
    
    # 创建修改器实例
    modifier = Victoria2Modifier()
    
    # 目标文件
    filename = "China1836_04_29.v2"
    
    print("="*60)
    print("Victoria II 修改器 - 编程使用示例")
    print("="*60)
    
    # 示例1: 单独修改人口斗争性
    print("\n示例1: 修改人口斗争性")
    print("-" * 30)
    success = modifier.modify_militancy(filename, china_militancy=0.0, other_militancy=10.0)
    print(f"结果: {'成功' if success else '失败'}")
    
    # 示例2: 单独修改文化
    print("\n示例2: 修改中国文化")
    print("-" * 30)
    success = modifier.modify_china_culture(filename, "beifaren", ["nanfaren", "manchu"])
    print(f"结果: {'成功' if success else '失败'}")
    
    # 示例3: 单独修改恶名度
    print("\n示例3: 修改中国恶名度")
    print("-" * 30)
    success = modifier.modify_china_infamy(filename, 0.0)
    print(f"结果: {'成功' if success else '失败'}")
    
    print("\n" + "="*60)
    print("所有修改完成！")
    print("="*60)

def custom_modification_example():
    """自定义修改示例"""
    modifier = Victoria2Modifier()
    filename = "China1836_04_29.v2"
    
    print("\n" + "="*60)
    print("自定义修改示例")
    print("="*60)
    
    # 自定义参数
    china_mil = 0.5      # 中国人口斗争性
    other_mil = 8.0      # 其他国家人口斗争性
    primary_culture = "beifaren"  # 主文化
    accepted_cultures = ["nanfaren", "manchu", "mongol"]  # 接受文化
    infamy = 5.0         # 恶名度
    
    print(f"自定义设置:")
    print(f"- 中国人口斗争性: {china_mil}")
    print(f"- 其他国家人口斗争性: {other_mil}")
    print(f"- 主文化: {primary_culture}")
    print(f"- 接受文化: {', '.join(accepted_cultures)}")
    print(f"- 恶名度: {infamy}")
    
    # 执行修改
    success1 = modifier.modify_militancy(filename, china_mil, other_mil)
    success2 = modifier.modify_china_culture(filename, primary_culture, accepted_cultures)
    success3 = modifier.modify_china_infamy(filename, infamy)
    
    print(f"\n修改结果:")
    print(f"- 人口斗争性: {'✅' if success1 else '❌'}")
    print(f"- 文化设置: {'✅' if success2 else '❌'}")
    print(f"- 恶名度: {'✅' if success3 else '❌'}")

if __name__ == "__main__":
    print("Victoria II 修改器 - 统一工具演示")
    print("此文件展示了如何以编程方式使用修改器")
    print("运行 python victoria2_modifier.py 来使用交互式界面")
    print("\n提示: 取消注释下面的函数调用来运行示例")
    
    # 取消注释来运行示例:
    # example_usage()
    # custom_modification_example()
