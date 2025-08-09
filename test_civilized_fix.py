#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文明化修改功能，监控花括号变化
"""

import os
import shutil
from datetime import datetime

def test_civilized_modification():
    """测试文明化修改功能"""
    
    # 备份当前文件
    backup_file = f"China1841_10_22_TEST_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.v2"
    shutil.copy2("China1841_10_22.v2", backup_file)
    print(f"📁 测试前备份: {backup_file}")
    
    # 检查修改前的花括号状态
    def check_braces(filename, desc):
        encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252']
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    content = f.read()
                open_braces = content.count('{')
                close_braces = content.count('}')
                difference = open_braces - close_braces
                print(f"{desc}:")
                print(f"  编码: {encoding}")
                print(f"  开括号: {open_braces:,}")
                print(f"  闭括号: {close_braces:,}")
                print(f"  差异: {difference}")
                return open_braces, close_braces, difference
            except UnicodeDecodeError:
                continue
        return None, None, None
    
    print("🔍 修改前状态检查:")
    before_open, before_close, before_diff = check_braces("China1841_10_22.v2", "修改前")
    
    if before_open is None:
        print("❌ 无法读取文件")
        return False
    
    # 执行修改 - 只修改一个小范围测试
    print("\\n🔧 开始执行文明化修改测试...")
    
    # 导入修改器
    try:
        from victoria2_main_modifier import Victoria2Modifier
        
        # 创建修改器实例
        modifier = Victoria2Modifier()
        
        # 加载文件
        if not modifier.load_file("China1841_10_22.v2"):
            print("❌ 文件加载失败")
            return False
        
        print("✅ 文件加载成功")
        
        # 执行修改 - 使用修复后的方法
        print("🎯 执行所有国家文明化状态修改 (除中国外设为no)...")
        success = modifier.modify_all_countries_civilized("no", exclude_china=True)
        
        if success:
            print("✅ 修改操作报告成功")
            
            # 保存文件
            modifier.save_file("China1841_10_22.v2")
            print("💾 文件已保存")
        else:
            print("❌ 修改操作失败")
            return False
            
    except Exception as e:
        print(f"❌ 修改过程出错: {e}")
        return False
    
    # 检查修改后的花括号状态
    print("\\n🔍 修改后状态检查:")
    after_open, after_close, after_diff = check_braces("China1841_10_22.v2", "修改后")
    
    if after_open is None:
        print("❌ 修改后无法读取文件")
        return False
    
    # 分析变化
    print("\\n📊 变化分析:")
    open_change = after_open - before_open
    close_change = after_close - before_close
    diff_change = after_diff - before_diff
    
    print(f"  开括号变化: {open_change:+d}")
    print(f"  闭括号变化: {close_change:+d}")
    print(f"  差异变化: {diff_change:+d}")
    
    # 判断结果
    if abs(open_change) <= 1 and abs(close_change) <= 1 and abs(diff_change) <= 1:
        print("✅ 花括号变化在可接受范围内")
        return True
    else:
        print("❌ 花括号变化过大，可能存在结构破坏")
        print(f"🔄 正在从备份恢复...")
        shutil.copy2(backup_file, "China1841_10_22.v2")
        print("✅ 已从备份恢复")
        return False

if __name__ == "__main__":
    print("🧪 开始测试文明化修改功能...")
    success = test_civilized_modification()
    
    if success:
        print("\\n🎉 测试通过！修改功能工作正常。")
    else:
        print("\\n❌ 测试失败！需要进一步修复。")
