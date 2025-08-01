#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Victoria II 存档文件政治修改工具

该工具用于修改中国的政治和文化设置：
1. 修改执政党的宗教政策为无神论
2. 添加南方人文化到主文化
"""

import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class PoliticalModifier:
    def __init__(self, save_file_path: str):
        self.save_file_path = Path(save_file_path)
        self.backup_path = None
        self.content = ""
        
    def create_backup(self) -> str:
        """创建存档文件备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.save_file_path.stem}_backup_{timestamp}{self.save_file_path.suffix}"
        self.backup_path = self.save_file_path.parent / backup_name
        
        shutil.copy2(self.save_file_path, self.backup_path)
        print(f"备份文件已创建: {self.backup_path}")
        return str(self.backup_path)
    
    def load_file(self):
        """加载存档文件"""
        try:
            with open(self.save_file_path, 'r', encoding='utf-8-sig') as f:
                self.content = f.read()
            print(f"成功加载文件: {self.save_file_path}")
        except UnicodeDecodeError:
            with open(self.save_file_path, 'r', encoding='latin-1') as f:
                self.content = f.read()
            print(f"成功加载文件（latin-1编码）: {self.save_file_path}")
    
    def find_china_section(self) -> Tuple[int, int]:
        """查找中国数据段的开始和结束位置"""
        chi_start = self.content.find("CHI=\n{")
        if chi_start == -1:
            chi_start = self.content.find("CHI=\r\n{")
        if chi_start == -1:
            raise ValueError("无法找到中国数据段")
        
        # 找到对应的结束大括号
        brace_count = 0
        start_pos = chi_start + len("CHI=\n{") - 1
        for i, char in enumerate(self.content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return chi_start, i + 1
        
        raise ValueError("无法找到中国数据段的结束位置")
    
    def find_political_parties_section(self) -> Dict[str, Dict]:
        """查找政党定义部分"""
        # 查找所有政党定义
        party_pattern = r'(\d+)=\{[^}]*name="([^"]*)"[^}]*\}'
        parties = {}
        
        for match in re.finditer(party_pattern, self.content, re.DOTALL):
            party_id = match.group(1)
            party_name = match.group(2)
            parties[party_id] = {
                'name': party_name,
                'full_text': match.group(0),
                'start': match.start(),
                'end': match.end()
            }
        
        return parties
    
    def modify_ruling_party_religion(self, china_start: int, china_end: int):
        """修改中国执政党的宗教政策为无神论"""
        china_section = self.content[china_start:china_end]
        
        # 查找ruling_party的ID
        ruling_party_match = re.search(r'ruling_party=(\d+)', china_section)
        if not ruling_party_match:
            print("警告: 未找到执政党信息")
            return
        
        ruling_party_id = ruling_party_match.group(1)
        print(f"找到执政党ID: {ruling_party_id}")
        
        # 在全文中查找这个政党的定义
        party_pattern = rf'{ruling_party_id}=\{{[^}}]*\}}'
        party_match = re.search(party_pattern, self.content, re.DOTALL)
        
        if party_match:
            party_text = party_match.group(0)
            print(f"找到执政党定义: {party_text[:200]}...")
            
            # 查找是否有religious_policy字段
            if 'religious_policy=' in party_text:
                # 替换宗教政策为secularized（无神论）
                new_party_text = re.sub(
                    r'religious_policy="[^"]*"',
                    'religious_policy="secularized"',
                    party_text
                )
                self.content = self.content.replace(party_text, new_party_text)
                print("已修改执政党宗教政策为secularized（无神论）")
            else:
                print("执政党定义中未找到religious_policy字段")
        else:
            print(f"警告: 未找到ID为{ruling_party_id}的政党定义")
    
    def modify_primary_culture(self, china_start: int, china_end: int):
        """修改中国主文化，添加南方人文化"""
        china_section = self.content[china_start:china_end]
        
        # 查找主文化设置
        if 'primary_culture=' in china_section:
            # 如果已有主文化设置，直接替换
            new_china_section = re.sub(
                r'primary_culture="[^"]*"',
                'primary_culture="nanfaren"',
                china_section
            )
            self.content = self.content[:china_start] + new_china_section + self.content[china_end:]
            print("已修改主文化为nanfaren（南方人）")
        else:
            # 如果没有主文化设置，在适当位置添加
            # 通常在religion字段之后添加
            religion_match = re.search(r'religion="[^"]*"', china_section)
            if religion_match:
                insert_pos = china_start + religion_match.end()
                new_line = '\n\tprimary_culture="nanfaren"'
                self.content = self.content[:insert_pos] + new_line + self.content[insert_pos:]
                print("已添加主文化设置为nanfaren（南方人）")
            else:
                print("警告: 无法找到合适的位置添加主文化设置")
    
    def save_file(self):
        """保存修改后的文件"""
        try:
            with open(self.save_file_path, 'w', encoding='utf-8-sig') as f:
                f.write(self.content)
            print(f"文件已保存: {self.save_file_path}")
        except Exception as e:
            print(f"保存文件时出错: {e}")
    
    def modify_political_settings(self):
        """执行政治设置修改"""
        print("开始修改中国政治设置...")
        
        # 创建备份
        self.create_backup()
        
        # 加载文件
        self.load_file()
        
        # 查找中国数据段
        try:
            china_start, china_end = self.find_china_section()
            print(f"找到中国数据段: 位置 {china_start} - {china_end}")
        except ValueError as e:
            print(f"错误: {e}")
            return
        
        # 修改执政党宗教政策
        self.modify_ruling_party_religion(china_start, china_end)
        
        # 重新查找中国数据段（因为内容可能已改变）
        china_start, china_end = self.find_china_section()
        
        # 修改主文化
        self.modify_primary_culture(china_start, china_end)
        
        # 保存文件
        self.save_file()
        
        print("政治设置修改完成！")


def main():
    save_file = "China1836_04_29.v2"
    
    try:
        modifier = PoliticalModifier(save_file)
        modifier.modify_political_settings()
        
    except Exception as e:
        print(f"修改过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
