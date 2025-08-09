#!/usr/bin/env python3
"""
深度分析文件结构损坏问题
"""

import re
import os

def analyze_bracket_corruption():
    """分析花括号损坏问题"""
    print("🔍 深度分析花括号结构损坏")
    print("="*60)
    
    files = ["autosave.v2", "test_civilized_simple_143915.v2"]
    
    for filename in files:
        if not os.path.exists(filename):
            continue
            
        print(f"\n📄 分析 {filename}:")
        
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
            
            # 查找问题模式
            patterns = {
                "三重闭括号": r'\}\s*\}\s*\}',
                "四重闭括号": r'\}\s*\}\s*\}\s*\}',
                "五重闭括号": r'\}\s*\}\s*\}\s*\}\s*\}',
                "连续等号": r'=\s*=',
                "孤立的值": r'^\s*[\d.]+\s*$',
                "不完整块": r'\{\s*[\d.]+\s*=\s*$',
                "错误嵌套": r'\{\s*\w+\s*=\s*\{[^{}]*\{[^{}]*\}\s*\w+\s*=',
            }
            
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, content, re.MULTILINE)
                if matches:
                    print(f"  ❌ {pattern_name}: {len(matches)} 个")
                    # 显示前几个例子
                    for i, match in enumerate(matches[:3]):
                        print(f"    例子 {i+1}: {repr(match[:50])}")
                else:
                    print(f"  ✅ {pattern_name}: 0 个")
        except Exception as e:
            print(f"❌ 分析 {filename} 时出错: {e}")

def check_population_block_structure():
    """检查人口块结构"""
    print(f"\n" + "="*60)
    print("🔍 检查人口块结构")
    print("="*60)
    
    files = ["autosave.v2", "test_civilized_simple_143915.v2"]
    
    for filename in files:
        if not os.path.exists(filename):
            continue
            
        print(f"\n📄 分析 {filename} 的人口块:")
        
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
            
            # 查找人口块模式 - 更准确的正则
            # 人口块通常是 数字={ type=数字 culture=文化 religion=宗教 size=数字 con=数字 mil=数字 }
            pop_pattern = r'(\d+)\s*=\s*\{\s*type\s*=\s*(\d+)\s+culture\s*=\s*(\w+)\s+religion\s*=\s*(\w+)\s+size\s*=\s*([\d.]+)'
            pop_matches = re.findall(pop_pattern, content)
            
            print(f"  完整人口块: {len(pop_matches)}")
            
            if pop_matches:
                # 分析前几个人口块的结构
                print(f"  前3个人口块示例:")
                for i, (pop_id, pop_type, culture, religion, size) in enumerate(pop_matches[:3]):
                    print(f"    {i+1}. ID={pop_id}, 类型={pop_type}, 文化={culture}, 宗教={religion}, 人口={size}")
            
            # 检查损坏的人口块
            broken_patterns = {
                "缺少结束括号的人口块": r'\d+\s*=\s*\{\s*type\s*=\s*\d+[^}]*size\s*=\s*[\d.]+[^}]*$',
                "重复等号的人口块": r'\d+\s*=\s*=\s*\{',
                "嵌套错误的人口块": r'\d+\s*=\s*\{\s*\d+\s*=\s*\{',
            }
            
            for pattern_name, pattern in broken_patterns.items():
                matches = re.findall(pattern, content, re.MULTILINE)
                if matches:
                    print(f"  ❌ {pattern_name}: {len(matches)}")
                else:
                    print(f"  ✅ {pattern_name}: 0")
                    
        except Exception as e:
            print(f"❌ 分析 {filename} 时出错: {e}")

def find_corruption_source():
    """寻找损坏来源"""
    print(f"\n" + "="*60)
    print("🔍 寻找损坏来源")
    print("="*60)
    
    # 检查是否有备份文件可以对比
    backup_files = [f for f in os.listdir('.') if f.endswith('.v2') and 'backup' in f.lower()]
    original_files = [f for f in os.listdir('.') if f.endswith('.v2') and 'autosave' not in f and 'backup' not in f.lower()]
    
    print(f"找到备份文件: {backup_files}")
    print(f"找到原始文件: {original_files}")
    
    # 如果有原始文件，比较结构
    if original_files:
        original_file = original_files[0]
        print(f"\n对比原始文件 {original_file} 和 autosave.v2:")
        
        try:
            # 读取原始文件
            with open(original_file, 'r', encoding='utf-8-sig', errors='ignore') as f:
                original_content = f.read()
            
            # 读取修改后文件
            with open('autosave.v2', 'r', encoding='utf-8-sig', errors='ignore') as f:
                modified_content = f.read()
            
            # 比较基本结构
            orig_open = original_content.count('{')
            orig_close = original_content.count('}')
            mod_open = modified_content.count('{')
            mod_close = modified_content.count('}')
            
            print(f"  原始文件括号: 开 {orig_open}, 闭 {orig_close}, 平衡: {'✅' if orig_open == orig_close else '❌'}")
            print(f"  修改后括号: 开 {mod_open}, 闭 {mod_close}, 平衡: {'✅' if mod_open == mod_close else '❌'}")
            print(f"  差异: 开括号 {mod_open - orig_open:+d}, 闭括号 {mod_close - orig_close:+d}")
            
            # 查找可能的修改痕迹
            civilized_pattern = r'civilized\s*=\s*"?no"?'
            orig_civilized = len(re.findall(civilized_pattern, original_content))
            mod_civilized = len(re.findall(civilized_pattern, modified_content))
            
            print(f"  civilized='no' 数量: 原始 {orig_civilized}, 修改后 {mod_civilized}")
            
        except Exception as e:
            print(f"❌ 对比时出错: {e}")

if __name__ == "__main__":
    analyze_bracket_corruption()
    check_population_block_structure()
    find_corruption_source()
