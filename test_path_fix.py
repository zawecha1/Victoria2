#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试路径修复后的存档文件列表功能
"""

from victoria2_main_modifier import get_save_files_list, Victoria2Modifier

def test_save_files_list():
    """测试存档文件列表功能"""
    import os
    
    print("=" * 50)
    print("测试存档文件列表功能")
    print("=" * 50)
    
    print("📁 当前工作目录:", os.getcwd())
    
    # 测试获取存档文件列表
    save_files = get_save_files_list()
    
    if save_files:
        print(f"✅ 成功找到 {len(save_files)} 个存档文件:")
        for i, file in enumerate(save_files[:10], 1):  # 显示前10个
            size = os.path.getsize(file) / (1024 * 1024)  # MB
            print(f"  {i:2d}. {file} ({size:.1f} MB)")
        if len(save_files) > 10:
            print(f"     ... 还有 {len(save_files) - 10} 个文件")
    else:
        print("❌ 未找到任何存档文件")
        return False
    
    print("\n" + "=" * 50)
    print("✅ 路径修复测试完成!")
    print("=" * 50)
    return True

def test_modifier_initialization():
    """测试修改器初始化"""
    print("=" * 50)
    print("测试修改器初始化")
    print("=" * 50)
    
    try:
        modifier = Victoria2Modifier()
        print(f"✅ 修改器初始化成功")
        print(f"📁 默认存档路径: {modifier.default_save_path}")
        return True
    except Exception as e:
        print(f"❌ 修改器初始化失败: {e}")
        return False

if __name__ == "__main__":
    import os
    print("📍 当前工作目录:", os.getcwd())
    
    # 测试修改器初始化
    test1_result = test_modifier_initialization()
    
    # 测试存档文件列表
    test2_result = test_save_files_list()
    
    print(f"\n🎯 总测试结果:")
    print(f"修改器初始化: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"存档文件列表: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过! 路径修复成功!")
    else:
        print("\n⚠️ 部分测试失败，请检查。")
