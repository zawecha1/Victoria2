#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
已灭亡国家清理工具 (clean_dead_countries.py)
============================================
安全清理Victoria II存档中已灭亡国家的数据块

功能:
1. 识别已灭亡国家（有数据但无省份）
2. 统计这些国家在存档中的引用次数
3. 安全删除已灭亡国家的数据块（保持花括号平衡）
4. 自动备份和完整性检查

使用方法:
    python clean_dead_countries.py [模式]
    
模式:
    preview  - 仅预览，不删除 (默认)
    clean    - 实际清理
"""

from victoria2_main_modifier import Victoria2Modifier
import sys
import os

def preview_dead_countries(filename='autosave.v2'):
    """预览已灭亡国家"""
    print("🔍 已灭亡国家预览模式")
    print("=" * 30)
    
    if not os.path.exists(filename):
        print(f"❌ 未找到文件: {filename}")
        return False
    
    try:
        modifier = Victoria2Modifier(filename, debug_mode=True)
        result = modifier.remove_dead_country_blocks(dry_run=True)
        
        if result:
            print(f"\\n📊 预览结果:")
            print(f"   发现已灭亡国家: {len(result['removed_countries'])} 个")
            
            # 显示引用次数最多的前10个
            if result['references']:
                sorted_refs = sorted(result['references'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
                print(f"\\n🔗 引用次数最多的已灭亡国家:")
                for i, (tag, count) in enumerate(sorted_refs, 1):
                    print(f"   {i:2d}. {tag}: {count} 次引用")
            
            # 计算可节省的空间（估算）
            total_refs = sum(result['references'].values())
            print(f"\\n💾 预计效果:")
            print(f"   删除国家数据块: {len(result['removed_countries'])} 个")
            print(f"   总引用次数: {total_refs}")
            print(f"   可能节省存档大小: 估计数千字符")
            
            return True
        else:
            print("❌ 预览失败")
            return False
            
    except Exception as e:
        print(f"❌ 预览出错: {e}")
        return False

def clean_dead_countries(filename='autosave.v2'):
    """实际清理已灭亡国家"""
    print("🗑️ 已灭亡国家清理模式")
    print("=" * 30)
    
    if not os.path.exists(filename):
        print(f"❌ 未找到文件: {filename}")
        return False
    
    try:
        modifier = Victoria2Modifier(filename, debug_mode=True)
        result = modifier.clean_dead_countries_with_backup()
        
        if result:
            print(f"\\n🎉 清理成功完成!")
            print(f"   删除的国家: {len(result['removed_countries'])} 个")
            if result.get('removed_blocks'):
                total_saved = sum(block['size'] for block in result['removed_blocks'])
                print(f"   节省空间: {total_saved} 字符")
            return True
        else:
            print("❌ 清理失败或被取消")
            return False
            
    except Exception as e:
        print(f"❌ 清理出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def interactive_mode():
    """交互式模式"""
    print("🌍 Victoria II 已灭亡国家清理工具")
    print("=" * 40)
    
    # 检查存档文件
    available_files = [f for f in os.listdir('.') if f.endswith('.v2')]
    
    if not available_files:
        print("❌ 未找到.v2存档文件")
        return
    
    print(f"📁 找到 {len(available_files)} 个存档文件:")
    for i, file in enumerate(available_files, 1):
        size_mb = os.path.getsize(file) / (1024 * 1024)
        print(f"   {i}. {file} ({size_mb:.1f} MB)")
    
    # 选择文件
    if len(available_files) == 1:
        selected_file = available_files[0]
        print(f"\\n📂 自动选择: {selected_file}")
    else:
        try:
            choice = input(f"\\n请选择文件 (1-{len(available_files)}): ").strip()
            if not choice:
                selected_file = available_files[0]
            else:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(available_files):
                    selected_file = available_files[choice_idx]
                else:
                    selected_file = available_files[0]
        except ValueError:
            selected_file = available_files[0]
    
    # 选择操作模式
    print(f"\\n选择操作模式:")
    print(f"1. 预览模式 - 仅查看要删除的国家 (推荐)")
    print(f"2. 清理模式 - 实际删除已灭亡国家数据")
    
    mode_choice = input("\\n请选择模式 (1/2): ").strip()
    
    if mode_choice == "2":
        print(f"\\n⚠️ 注意: 清理模式将永久删除已灭亡国家数据")
        print(f"   程序会自动创建备份，但请确保重要数据已保存")
        confirm = input("\\n确认执行清理模式? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes', '是']:
            clean_dead_countries(selected_file)
        else:
            print("❌ 用户取消清理操作")
    else:
        preview_dead_countries(selected_file)

def main():
    """主函数"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "preview":
            preview_dead_countries()
        elif mode == "clean":
            clean_dead_countries()
        else:
            print(f"❌ 未知模式: {mode}")
            print(f"支持的模式: preview, clean")
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
