#!/usr/bin/env python3
"""
简单测试文明化状态修改功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from victoria2_main_modifier import Victoria2Modifier

def test_civilized_modification():
    """测试文明化状态修改功能"""
    print("🔧 开始文明化状态修改测试...")
    
    try:
        # 初始化修改器
        modifier = Victoria2Modifier("autosave.v2")
        
        # 执行文明化状态修改
        print("🔍 正在修改所有国家的文明化状态...")
        result = modifier.modify_all_countries_civilized("no", exclude_china=True)
        
        print(f"✅ 修改结果: {result}")
        
        if result:
            # 保存文件
            timestamp = modifier.get_timestamp()
            output_file = f"autosave_civilized_fixed_{timestamp}.v2"
            modifier.save_file(output_file)
            print(f"📁 文件已保存为: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_civilized_modification()
    if success:
        print("🎉 文明化状态修改测试成功！")
    else:
        print("❌ 文明化状态修改测试失败！")
