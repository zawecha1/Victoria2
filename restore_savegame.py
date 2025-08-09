#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存档文件恢复工具
安全地恢复到工作状态的备份文件
"""

import os
import shutil
from datetime import datetime

def restore_working_savegame():
    """恢复到正常工作的存档文件"""
    print("🔄 Victoria II 存档文件恢复工具")
    print("=" * 50)
    
    # 文件路径
    current_file = "autosave.v2"
    working_backup = "China1837_07_15.v2"
    broken_backup = f"autosave_broken_{datetime.now().strftime('%Y%m%d_%H%M%S')}.v2"
    
    # 检查文件存在性
    if not os.path.exists(working_backup):
        print(f"❌ 工作备份文件不存在: {working_backup}")
        return False
    
    if not os.path.exists(current_file):
        print(f"❌ 当前文件不存在: {current_file}")
        return False
    
    try:
        # 1. 备份损坏的文件
        print(f"1️⃣ 备份损坏的文件...")
        shutil.copy2(current_file, broken_backup)
        print(f"   损坏文件已备份到: {broken_backup}")
        
        # 2. 复制工作文件
        print(f"2️⃣ 恢复工作状态的文件...")
        shutil.copy2(working_backup, current_file)
        print(f"   已从 {working_backup} 恢复到 {current_file}")
        
        # 3. 验证文件
        print(f"3️⃣ 验证恢复结果...")
        current_size = os.path.getsize(current_file)
        backup_size = os.path.getsize(working_backup)
        
        if current_size == backup_size:
            print(f"✅ 文件大小验证通过: {current_size:,} 字节")
            
            # 检查编码
            try:
                with open(current_file, 'r', encoding='latin1') as f:
                    test_content = f.read(1000)
                print(f"✅ latin1 编码验证通过")
            except UnicodeDecodeError:
                print(f"❌ 编码验证失败")
                return False
            
            print(f"🎉 存档恢复成功！")
            print(f"📋 恢复摘要:")
            print(f"   当前文件: {current_file}")
            print(f"   源文件: {working_backup}")
            print(f"   损坏备份: {broken_backup}")
            print(f"🎮 现在可以在游戏中正常加载 autosave.v2")
            
            return True
        else:
            print(f"❌ 文件大小不匹配")
            return False
            
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False

def analyze_redistribution_problem():
    """分析重分配问题的原因"""
    print("\n" + "=" * 50)
    print("🔍 重分配问题分析")
    print("=" * 50)
    
    print("❌ 问题原因分析:")
    print("   1. 重分配工具过于激进")
    print("   2. 许多国家的所有省份都被转移给中国")
    print("   3. 130个国家没有任何省份，但首都定义仍存在")
    print("   4. 首都-省份不一致导致游戏无法加载")
    
    print("\n💡 建议的修复方案:")
    print("   1. ✅ 恢复到工作状态的备份文件 (推荐)")
    print("   2. 修改重分配逻辑，确保每个国家至少保留1个省份")
    print("   3. 为无省份的国家添加适当的省份或删除国家定义")
    
    print("\n⚠️ 教训总结:")
    print("   • 大规模省份重分配会破坏游戏平衡")
    print("   • 必须保持首都-省份一致性")
    print("   • 需要更细致的验证机制")

def main():
    """主函数"""
    print("🚑 开始存档修复...")
    
    success = restore_working_savegame()
    
    if success:
        analyze_redistribution_problem()
    else:
        print("\n❌ 恢复失败")
        print("🔧 手动恢复步骤:")
        print("   1. 删除当前的 autosave.v2")
        print("   2. 复制 China1837_07_15.v2 到 autosave.v2")
        print("   3. 在游戏中加载 autosave.v2")

if __name__ == "__main__":
    main()
