#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 存档编码修复工具
修复 autosave.v2 的编码问题
"""

import os
import shutil
from datetime import datetime

def fix_encoding():
    """修复 autosave.v2 的编码问题"""
    print("🔧 Victoria II 存档编码修复工具")
    print("=" * 50)
    
    # 文件路径
    problem_file = "autosave.v2"
    backup_file = f"autosave_broken_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.v2"
    
    # 检查文件是否存在
    if not os.path.exists(problem_file):
        print(f"❌ 文件不存在: {problem_file}")
        return False
    
    try:
        print(f"1️⃣ 备份损坏文件到: {backup_file}")
        shutil.copy2(problem_file, backup_file)
        
        print("2️⃣ 读取文件内容 (utf-8-sig)")
        with open(problem_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        print("3️⃣ 重新保存为 latin1 编码")
        with open(problem_file, 'w', encoding='latin1') as f:
            f.write(content)
        
        print("4️⃣ 验证修复结果")
        
        # 验证编码
        try:
            with open(problem_file, 'r', encoding='latin1') as f:
                test_content = f.read(1000)
            print("✅ latin1 编码验证成功")
        except UnicodeDecodeError:
            print("❌ latin1 编码验证失败")
            return False
        
        # 检查文件大小
        new_size = os.path.getsize(problem_file)
        backup_size = os.path.getsize(backup_file)
        
        print(f"📊 文件大小对比:")
        print(f"   原始 (损坏): {backup_size:,} 字节")
        print(f"   修复后: {new_size:,} 字节")
        print(f"   差异: {new_size - backup_size:,} 字节")
        
        print("🎉 编码修复完成！")
        print(f"💾 损坏文件已备份到: {backup_file}")
        print("🎮 现在可以尝试在游戏中加载 autosave.v2")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def quick_comparison():
    """快速对比修复前后的文件"""
    print("\n" + "=" * 50)
    print("📋 快速文件检查")
    
    files_to_check = [
        "China1837_07_15.v2",
        "autosave.v2"
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            
            # 检测编码
            encodings = ['latin1', 'utf-8', 'utf-8-sig']
            detected_encoding = None
            
            for enc in encodings:
                try:
                    with open(filename, 'r', encoding=enc) as f:
                        f.read(1000)
                    detected_encoding = enc
                    break
                except:
                    continue
            
            print(f"📁 {filename}:")
            print(f"   大小: {size:,} 字节")
            print(f"   编码: {detected_encoding or '无法检测'}")
        else:
            print(f"❌ 文件不存在: {filename}")

if __name__ == "__main__":
    print("开始修复...")
    
    # 先显示当前状态
    quick_comparison()
    
    # 执行修复
    success = fix_encoding()
    
    # 显示修复后状态
    if success:
        quick_comparison()
