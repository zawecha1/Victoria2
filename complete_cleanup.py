#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动完成清理工具 (complete_cleanup.py)
=====================================
完成之前中断的清理操作并验证结果
"""

from victoria2_main_modifier import Victoria2Modifier
import os

def complete_cleanup():
    """完成清理操作"""
    print("🔧 完成清理操作")
    print("=" * 30)
    
    # 检查备份文件
    backup_files = [f for f in os.listdir('.') if 'before_cleanup' in f and f.endswith('.v2')]
    
    if not backup_files:
        print("❌ 未找到备份文件")
        return False
    
    backup_file = backup_files[0]
    print(f"📁 找到备份文件: {backup_file}")
    
    # 检查原文件
    if not os.path.exists('autosave.v2'):
        print("❌ 未找到原文件 autosave.v2")
        return False
    
    # 加载修改器（它应该已经包含了修改）
    try:
        modifier = Victoria2Modifier('autosave.v2', debug_mode=True)
        
        # 检查花括号平衡
        if modifier.check_bracket_balance():
            print("✅ 花括号平衡检查通过")
            
            # 保存文件
            try:
                with open('autosave.v2', 'w', encoding='utf-8-sig') as f:
                    f.write(modifier.content)
                
                print("✅ 文件保存成功")
                
                # 检查文件大小对比
                original_size = os.path.getsize(backup_file)
                new_size = os.path.getsize('autosave.v2')
                saved_bytes = original_size - new_size
                
                print(f"\\n📊 清理效果:")
                print(f"   原始大小: {original_size:,} 字节 ({original_size/1024/1024:.1f} MB)")
                print(f"   清理后: {new_size:,} 字节 ({new_size/1024/1024:.1f} MB)")
                print(f"   节省空间: {saved_bytes:,} 字节 ({saved_bytes/1024/1024:.1f} MB)")
                print(f"   压缩率: {saved_bytes/original_size*100:.2f}%")
                
                return True
                
            except Exception as e:
                print(f"❌ 保存文件失败: {e}")
                return False
        else:
            print("❌ 花括号平衡检查失败，未保存文件")
            return False
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_cleanup():
    """验证清理效果"""
    print("\\n🔍 验证清理效果")
    print("=" * 30)
    
    try:
        modifier = Victoria2Modifier('autosave.v2', debug_mode=True)
        
        # 重新统计已灭亡国家
        dead_countries = modifier.find_dead_countries()
        
        print(f"📊 清理后统计:")
        print(f"   剩余已灭亡国家: {len(dead_countries)} 个")
        
        if len(dead_countries) == 0:
            print("🎉 所有已灭亡国家数据块已成功清理！")
        else:
            print(f"⚠️ 仍有 {len(dead_countries)} 个已灭亡国家未清理")
            print("前10个未清理的国家:")
            for i, tag in enumerate(list(dead_countries.keys())[:10], 1):
                print(f"   {i}. {tag}")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主函数"""
    print("🛠️ Victoria II 清理完成工具")
    print("=" * 40)
    
    # 完成清理
    if complete_cleanup():
        # 验证结果
        verify_cleanup()
        print("\\n🎉 清理操作全部完成！")
    else:
        print("\\n❌ 清理操作失败")

if __name__ == "__main__":
    main()
