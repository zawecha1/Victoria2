#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恢复损坏的文件从备份
"""
import shutil
import os
from datetime import datetime

def restore_from_backup():
    """从备份恢复文件"""
    backup_file = "China1841_10_22_unified_backup_20250809_174727.v2"
    target_file = "China1841_10_22.v2"
    
    if not os.path.exists(backup_file):
        print(f"❌ 备份文件不存在: {backup_file}")
        return False
    
    try:
        # 创建当前损坏文件的备份（以防需要调试）
        damaged_backup = f"China1841_10_22_DAMAGED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.v2"
        if os.path.exists(target_file):
            shutil.copy2(target_file, damaged_backup)
            print(f"📁 损坏文件已备份为: {damaged_backup}")
        
        # 从备份恢复
        shutil.copy2(backup_file, target_file)
        print(f"✅ 已从备份恢复文件: {backup_file} → {target_file}")
        
        # 验证恢复后的文件 - 尝试多种编码
        encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(target_file, 'r', encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"❌ 无法读取恢复后的文件")
            return False
        
        open_braces = content.count('{')
        close_braces = content.count('}')
        difference = open_braces - close_braces
        
        print(f"📊 恢复后验证 (编码: {used_encoding}):")
        print(f"  文件大小: {len(content):,} 字符")
        print(f"  开括号: {open_braces:,}")
        print(f"  闭括号: {close_braces:,}")
        print(f"  差异: {difference}")
        
        if abs(difference) <= 1:
            print(f"✅ 花括号平衡正常")
            return True
        else:
            print(f"⚠️ 花括号仍有差异: {difference}")
            return False
            
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False

if __name__ == "__main__":
    print("🔄 开始从备份恢复文件...")
    success = restore_from_backup()
    
    if success:
        print("\\n🎉 文件恢复成功！")
        print("现在可以重新尝试修改操作了。")
    else:
        print("\\n❌ 文件恢复失败！")
        print("请检查备份文件是否存在和可读。")
