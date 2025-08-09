#!/usr/bin/env python3
"""
简化的文明化状态修改测试
"""

import re
import os
from datetime import datetime

def simple_civilized_test():
    """简化的文明化状态修改测试"""
    print("🧪 简化的文明化状态修改测试")
    print("="*60)
    
    filename = "autosave.v2"
    
    if not os.path.exists(filename):
        print(f"❌ 文件 {filename} 不存在")
        return False
    
    try:
        # 读取文件
        print("📂 正在读取文件...")
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        print(f"✅ 文件读取成功，大小: {len(content):,} 字符")
        
        # 统计当前状态
        print("\n📊 当前文明化状态统计:")
        civilized_yes = len(re.findall(r'civilized\s*=\s*"?yes"?', content, re.IGNORECASE))
        civilized_no = len(re.findall(r'civilized\s*=\s*"?no"?', content, re.IGNORECASE))
        print(f"  civilized=\"yes\": {civilized_yes}")
        print(f"  civilized=\"no\": {civilized_no}")
        print(f"  总计: {civilized_yes + civilized_no}")
        
        # 执行修改：将所有 civilized="yes" 改为 civilized="no"
        print(f"\n🔧 执行修改: 将所有 civilized=\"yes\" 改为 civilized=\"no\"")
        
        # 使用正则表达式替换
        modified_content = re.sub(
            r'civilized\s*=\s*"?yes"?',
            'civilized="no"',
            content,
            flags=re.IGNORECASE
        )
        
        # 统计修改后的状态
        print("\n📊 修改后文明化状态统计:")
        new_civilized_yes = len(re.findall(r'civilized\s*=\s*"?yes"?', modified_content, re.IGNORECASE))
        new_civilized_no = len(re.findall(r'civilized\s*=\s*"?no"?', modified_content, re.IGNORECASE))
        print(f"  civilized=\"yes\": {new_civilized_yes}")
        print(f"  civilized=\"no\": {new_civilized_no}")
        print(f"  总计: {new_civilized_yes + new_civilized_no}")
        
        changes = civilized_yes - new_civilized_yes
        print(f"  修改数量: {changes}")
        
        # 保存测试文件
        test_filename = f"test_civilized_simple_{datetime.now().strftime('%H%M%S')}.v2"
        print(f"\n💾 保存测试文件: {test_filename}")
        
        with open(test_filename, 'w', encoding='utf-8-sig', errors='ignore') as f:
            f.write(modified_content)
        
        print(f"✅ 测试文件保存成功")
        
        # 验证保存的文件
        print(f"\n🔍 验证保存的文件...")
        with open(test_filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            verify_content = f.read()
        
        verify_yes = len(re.findall(r'civilized\s*=\s*"?yes"?', verify_content, re.IGNORECASE))
        verify_no = len(re.findall(r'civilized\s*=\s*"?no"?', verify_content, re.IGNORECASE))
        
        print(f"  验证 civilized=\"yes\": {verify_yes}")
        print(f"  验证 civilized=\"no\": {verify_no}")
        
        if verify_yes == new_civilized_yes and verify_no == new_civilized_no:
            print("✅ 文件验证成功!")
            return True
        else:
            print("❌ 文件验证失败!")
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    simple_civilized_test()
