#!/usr/bin/env python3
"""
修复验证脚本 - 测试修复后的程序能否正常处理实际存档文件
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_real_file_fix():
    """测试修复后的程序在真实文件上的表现"""
    print("🧪 测试修复后的程序 - 真实文件验证")
    print("="*50)
    
    # 使用较小的测试文件
    test_files = ["autosave.v2", "China1836_02_20.v2"]
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"⚠️ 跳过不存在的文件: {test_file}")
            continue
            
        print(f"\n📁 测试文件: {test_file}")
        print("-" * 30)
        
        try:
            from victoria2_main_modifier import Victoria2Modifier
            
            # 创建修改器实例
            modifier = Victoria2Modifier(debug_mode=False)
            
            print(f"📁 加载文件...")
            file_size = os.path.getsize(test_file)
            print(f"文件大小: {file_size:,} 字节")
            
            # 加载文件
            if not modifier.load_file(test_file):
                print("❌ 文件加载失败")
                continue
            
            print("✅ 文件加载成功")
            
            # 测试CHI块查找
            print(f"\n🔍 测试CHI块查找...")
            
            try:
                culture_blocks = modifier.find_blocks_by_function_type('culture')
                infamy_blocks = modifier.find_blocks_by_function_type('infamy')
                
                print(f"文化修改CHI块: {len(culture_blocks)} 个")
                print(f"恶名度修改CHI块: {len(infamy_blocks)} 个")
                
                if len(culture_blocks) > 0 and len(infamy_blocks) > 0:
                    print("✅ CHI块查找正常")
                    
                    # 显示最大的CHI块信息
                    if len(culture_blocks) > 1:
                        largest_block = max(culture_blocks, key=lambda b: len(b.content))
                        print(f"最大CHI块: {len(largest_block.content):,} 字符")
                    else:
                        print(f"CHI块大小: {len(culture_blocks[0].content):,} 字符")
                else:
                    print("❌ CHI块查找异常")
                    
            except Exception as e:
                print(f"❌ CHI块查找出错: {e}")
                continue
            
            # 如果文件不太大，可以尝试实际修改测试
            if file_size < 50 * 1024 * 1024:  # 小于50MB
                print(f"\n🧪 尝试小规模修改测试...")
                
                try:
                    # 创建备份
                    backup_file = f"{test_file}.test_backup"
                    import shutil
                    shutil.copy2(test_file, backup_file)
                    
                    # 尝试恶名度修改
                    success = modifier.modify_china_infamy(0.0)
                    if success:
                        print("✅ 恶名度修改测试成功")
                    else:
                        print("❌ 恶名度修改测试失败")
                    
                    # 恢复备份
                    shutil.move(backup_file, test_file)
                    print("✅ 文件已恢复")
                    
                except Exception as e:
                    print(f"❌ 修改测试出错: {e}")
                    # 确保恢复文件
                    if os.path.exists(backup_file):
                        shutil.move(backup_file, test_file)
            else:
                print(f"⚠️ 文件过大，跳过修改测试")
        
        except Exception as e:
            print(f"❌ 文件处理出错: {e}")
        
        print(f"✅ 文件 {test_file} 测试完成")

if __name__ == "__main__":
    test_real_file_fix()
    print("\n🎯 修复验证完成！")
