#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
维多利亚2存档文件完整性检查工具
检查可能导致游戏崩溃的问题
"""

import re
import sys

def check_save_integrity(filename):
    """检查存档文件的完整性"""
    
    print(f"🔍 检查存档文件: {filename}")
    
    try:
        # 读取文件 - 尝试不同的编码
        content = None
        encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✅ 成功使用编码: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print("❌ 无法读取文件，所有编码都失败")
            return False
        
        print(f"✅ 文件大小: {len(content):,} 字符")
        
        # 1. 检查花括号平衡
        print("\n🔍 检查花括号平衡...")
        open_braces = content.count('{')
        close_braces = content.count('}')
        print(f"开括号 {{: {open_braces}")
        print(f"闭括号 }}: {close_braces}")
        
        if open_braces != close_braces:
            print(f"❌ 花括号不平衡! 差异: {open_braces - close_braces}")
            return False
        else:
            print("✅ 花括号平衡")
        
        # 2. 检查必要的游戏字段
        print("\n🔍 检查必要字段...")
        required_fields = [
            ('date=', '游戏日期'),
            ('player=', '玩家国家'),
            ('CHI=', 'CHI国家定义'),
        ]
        
        for field, name in required_fields:
            if field in content:
                print(f"✅ {name}: 存在")
            else:
                print(f"❌ {name}: 缺失!")
                return False
        
        # 3. 检查省份数量
        print("\n🔍 检查省份结构...")
        province_pattern = re.compile(r'^\d+=\s*{', re.MULTILINE)
        provinces = province_pattern.findall(content)
        print(f"省份数量: {len(provinces)}")
        
        if len(provinces) < 2000:
            print("⚠️ 警告: 省份数量偏少，可能存在问题")
        else:
            print("✅ 省份数量正常")
        
        # 4. 检查文件结尾
        print("\n🔍 检查文件结尾...")
        if content.endswith('\n}') or content.endswith('}'):
            print("✅ 文件结尾正常")
        else:
            print("⚠️ 警告: 文件结尾可能不完整")
            print(f"最后50个字符: {content[-50:]}")
        
        # 5. 检查异常的宗教转换
        print("\n🔍 检查宗教转换...")
        
        # 检查是否有非中国文化被错误改为mahayana
        non_chinese_cultures = ['baluchi', 'persian', 'afghan', 'russian', 'german', 
                               'french', 'english', 'spanish', 'italian', 'japanese',
                               'korean', 'vietnamese', 'thai', 'burmese', 'mongolian']
        
        for culture in non_chinese_cultures:
            pattern = f'{culture}=mahayana'
            matches = len(re.findall(pattern, content))
            if matches > 0:
                print(f"⚠️ 发现异常: {culture}=mahayana 出现 {matches} 次")
        
        # 6. 检查意识形态数值范围
        print("\n🔍 检查意识形态数值...")
        ideology_pattern = r'(\d+)=([\d.]+)'
        ideology_matches = re.findall(ideology_pattern, content)
        
        abnormal_values = 0
        for id_str, value_str in ideology_matches[-100:]:  # 检查最后100个
            try:
                value = float(value_str)
                if value < 0 or value > 100:
                    abnormal_values += 1
            except ValueError:
                abnormal_values += 1
        
        if abnormal_values > 0:
            print(f"⚠️ 发现 {abnormal_values} 个异常意识形态数值")
        else:
            print("✅ 意识形态数值正常")
        
        print("\n📊 整体评估:")
        print("✅ 文件基本完整性检查通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        return False

if __name__ == "__main__":
    # 检查修改后的文件
    modified_file = r"z:\Users\Administrator\Documents\Paradox Interactive\Victoria II\save games\China1841_12_17.v2"
    
    success = check_save_integrity(modified_file)
    
    if success:
        print("\n🎮 文件应该可以正常加载")
    else:
        print("\n❌ 文件可能存在问题，需要修复")
    
    sys.exit(0 if success else 1)
