#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证清理结果 (verify_cleanup_result.py)
======================================
验证已灭亡国家清理的结果
"""

from victoria2_main_modifier import Victoria2Modifier
import os

def verify_files():
    """验证清理前后的文件对比"""
    print("🔍 Victoria II 清理结果验证")
    print("=" * 40)
    
    # 检查文件
    original_file = "autosave_before_cleanup_20250809_194252_backup_20250809_194252.v2"
    cleaned_file = "autosave_cleaned.v2"
    
    if not os.path.exists(original_file):
        print(f"❌ 未找到清理后文件: {original_file}")
        return False
    
    if not os.path.exists("autosave.v2"):
        print("❌ 未找到当前文件: autosave.v2")
        return False
    
    # 文件大小对比
    cleaned_size = os.path.getsize(original_file)
    current_size = os.path.getsize("autosave.v2")
    
    print(f"📊 文件大小对比:")
    print(f"   当前 autosave.v2: {current_size:,} 字节 ({current_size/1024/1024:.2f} MB)")
    print(f"   清理后版本: {cleaned_size:,} 字节 ({cleaned_size/1024/1024:.2f} MB)")
    
    if cleaned_size < current_size:
        saved_bytes = current_size - cleaned_size
        print(f"   节省空间: {saved_bytes:,} 字节 ({saved_bytes/1024/1024:.2f} MB)")
        print(f"   压缩率: {saved_bytes/current_size*100:.2f}%")
        
        # 加载清理后的文件并验证
        print(f"\\n🔍 验证清理后文件...")
        try:
            modifier = Victoria2Modifier(original_file, debug_mode=True)
            dead_countries = modifier.find_dead_countries()
            
            print(f"📊 清理后统计:")
            print(f"   剩余已灭亡国家: {len(dead_countries)} 个")
            
            if len(dead_countries) == 0:
                print("🎉 所有已灭亡国家数据块已成功清理！")
                
                # 如果用户想要应用清理结果
                apply = input("\\n是否将清理结果应用到 autosave.v2? (y/N): ").strip().lower()
                if apply in ['y', 'yes', '是']:
                    try:
                        import shutil
                        shutil.copy2(original_file, "autosave.v2")
                        print("✅ 清理结果已应用到 autosave.v2")
                        return True
                    except Exception as e:
                        print(f"❌ 应用失败: {e}")
                        return False
                else:
                    print("📝 清理结果未应用，原文件保持不变")
                    return True
            else:
                print(f"⚠️ 清理不完整，仍有 {len(dead_countries)} 个已灭亡国家")
                return False
                
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False
    else:
        print("⚠️ 清理后文件大小未减少")
        return False

def main():
    """主函数"""
    verify_files()

if __name__ == "__main__":
    main()
