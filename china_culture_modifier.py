#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Victoria II 中国多文化设置工具
将中国的主文化和接受文化设置为：beifaren, nanfaren, manchu
"""

import re
import shutil
from pathlib import Path
from datetime import datetime


class ChinaCultureModifier:
    def __init__(self, save_file_path: str):
        self.save_file_path = Path(save_file_path)
        self.backup_path = None
        self.content = ""
        
    def create_backup(self) -> str:
        """创建存档文件备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.save_file_path.stem}_culture_backup_{timestamp}{self.save_file_path.suffix}"
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
    
    def find_china_section(self) -> tuple:
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
    
    def modify_china_culture(self):
        """修改中国的文化设置"""
        print("开始修改中国文化设置...")
        
        # 创建备份
        self.create_backup()
        
        # 加载文件
        self.load_file()
        
        # 查找中国数据段
        china_start, china_end = self.find_china_section()
        china_section = self.content[china_start:china_end]
        
        print(f"找到中国数据段: 位置 {china_start} - {china_end}")
        
        # 修改主文化
        new_china_section = self._modify_primary_culture(china_section)
        
        # 添加或修改接受文化
        new_china_section = self._modify_accepted_cultures(new_china_section)
        
        # 替换原始内容
        self.content = self.content[:china_start] + new_china_section + self.content[china_end:]
        
        # 保存文件
        self.save_file()
        
        print("中国文化设置修改完成！")
    
    def _modify_primary_culture(self, china_section: str) -> str:
        """修改主文化设置"""
        # 设置主文化为 beifaren（北方人）
        if 'primary_culture=' in china_section:
            # 替换现有的主文化设置
            new_section = re.sub(
                r'primary_culture="[^"]*"',
                'primary_culture="beifaren"',
                china_section
            )
            print("✓ 主文化已设置为 beifaren（北方人）")
        else:
            # 添加主文化设置
            religion_match = re.search(r'(\s+religion="[^"]*")', china_section)
            if religion_match:
                insert_pos = religion_match.end()
                new_line = '\n\tprimary_culture="beifaren"'
                new_section = (china_section[:insert_pos] + 
                             new_line + 
                             china_section[insert_pos:])
                print("✓ 已添加主文化设置为 beifaren（北方人）")
            else:
                print("⚠ 无法找到合适位置添加主文化设置")
                new_section = china_section
        
        return new_section
    
    def _modify_accepted_cultures(self, china_section: str) -> str:
        """修改接受文化设置"""
        # 接受的文化：nanfaren（南方人）和 manchu（满族）
        accepted_cultures = ["nanfaren", "manchu"]
        
        # 查找现有的culture块
        culture_match = re.search(r'(\s+culture=\s*\{[^}]*\})', china_section, re.DOTALL)
        
        if culture_match:
            # 替换现有的culture块
            culture_block = f'\n\tculture=\n\t{{\n'
            for culture in accepted_cultures:
                culture_block += f'\t\t"{culture}"\n'
            culture_block += '\t}'
            
            new_section = china_section.replace(culture_match.group(0), culture_block)
            print(f"✓ 已更新接受文化: {', '.join(accepted_cultures)}")
        else:
            # 添加新的culture块
            # 在primary_culture之后添加
            primary_culture_match = re.search(r'(\s+primary_culture="[^"]*")', china_section)
            if primary_culture_match:
                insert_pos = primary_culture_match.end()
                culture_block = f'\n\tculture=\n\t{{\n'
                for culture in accepted_cultures:
                    culture_block += f'\t\t"{culture}"\n'
                culture_block += '\t}'
                
                new_section = (china_section[:insert_pos] + 
                             culture_block + 
                             china_section[insert_pos:])
                print(f"✓ 已添加接受文化: {', '.join(accepted_cultures)}")
            else:
                print("⚠ 无法找到合适位置添加接受文化设置")
                new_section = china_section
        
        return new_section
    
    def save_file(self):
        """保存修改后的文件"""
        try:
            with open(self.save_file_path, 'w', encoding='utf-8-sig') as f:
                f.write(self.content)
            print(f"文件已保存: {self.save_file_path}")
        except Exception as e:
            print(f"保存文件时出错: {e}")
    
    def verify_modifications(self):
        """验证修改结果"""
        print("\n验证修改结果...")
        
        # 重新读取文件
        try:
            with open(self.save_file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(self.save_file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # 查找中国的文化设置
        china_match = re.search(r'CHI=\s*\{[^}]*primary_culture="([^"]*)"[^}]*\}', content, re.DOTALL)
        if china_match:
            primary_culture = china_match.group(1)
            print(f"✓ 主文化: {primary_culture}")
        
        # 查找接受文化
        culture_block_match = re.search(r'CHI=\s*\{[^}]*culture=\s*\{([^}]*)\}[^}]*\}', content, re.DOTALL)
        if culture_block_match:
            culture_content = culture_block_match.group(1)
            cultures = re.findall(r'"([^"]*)"', culture_content)
            print(f"✓ 接受文化: {', '.join(cultures)}")
        
        print("验证完成！")


def main():
    save_file = "China1836_04_29.v2"
    
    print("="*60)
    print("Victoria II 中国文化设置修改工具")
    print("="*60)
    print(f"目标文件: {save_file}")
    print("主文化: beifaren（北方人）")
    print("接受文化: nanfaren（南方人）, manchu（满族）")
    print("="*60)
    
    # 询问用户确认
    confirm = input("确认要修改文化设置吗？(输入 'yes' 确认): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    try:
        modifier = ChinaCultureModifier(save_file)
        modifier.modify_china_culture()
        modifier.verify_modifications()
        
        print("\n" + "="*60)
        print("✅ 中国文化设置修改成功!")
        print("📁 备份文件已创建")
        print("🎮 可以继续游戏了!")
        print("="*60)
        
    except Exception as e:
        print(f"修改过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
