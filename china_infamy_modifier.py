#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Victoria II 中国恶名度(infamy)修改工具
将中国的恶名度设置为 0
"""

import re
import shutil
from pathlib import Path
from datetime import datetime


class ChinaInfamyModifier:
    def __init__(self, save_file_path: str):
        self.save_file_path = Path(save_file_path)
        self.backup_path = None
        self.content = ""
        
    def create_backup(self) -> str:
        """创建存档文件备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.save_file_path.stem}_infamy_backup_{timestamp}{self.save_file_path.suffix}"
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
    
    def modify_china_infamy(self):
        """修改中国的恶名度"""
        print("开始修改中国恶名度...")
        
        # 创建备份
        self.create_backup()
        
        # 加载文件
        self.load_file()
        
        # 查找中国数据段
        china_start, china_end = self.find_china_section()
        china_section = self.content[china_start:china_end]
        
        print(f"找到中国数据段: 位置 {china_start} - {china_end}")
        
        # 查找当前的恶名度值
        infamy_match = re.search(r'(\s+)badboy=([\d.]+)', china_section)
        
        if infamy_match:
            current_infamy = float(infamy_match.group(2))
            print(f"当前恶名度: {current_infamy}")
            
            # 替换恶名度值
            new_china_section = re.sub(
                r'(\s+)badboy=([\d.]+)',
                r'\g<1>badboy=0.000',
                china_section
            )
            
            # 替换原始内容
            self.content = self.content[:china_start] + new_china_section + self.content[china_end:]
            print("✓ 恶名度已设置为 0.000")
            
        else:
            print("⚠ 在中国数据中未找到恶名度(badboy)字段")
            # 尝试添加恶名度字段
            religion_match = re.search(r'(\s+religion="[^"]*")', china_section)
            if religion_match:
                insert_pos = religion_match.end()
                new_line = '\n\tbadboy=0.000'
                new_china_section = (china_section[:insert_pos] + 
                                   new_line + 
                                   china_section[insert_pos:])
                self.content = self.content[:china_start] + new_china_section + self.content[china_end:]
                print("✓ 已添加恶名度字段并设置为 0.000")
            else:
                print("✗ 无法找到合适位置添加恶名度字段")
                return False
        
        # 保存文件
        self.save_file()
        
        print("中国恶名度修改完成！")
        return True
    
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
        
        # 查找中国的恶名度设置
        china_infamy_match = re.search(r'CHI=\s*\{[^}]*badboy=([\d.]+)[^}]*\}', content, re.DOTALL)
        if china_infamy_match:
            infamy_value = float(china_infamy_match.group(1))
            print(f"✓ 中国恶名度: {infamy_value}")
            if infamy_value == 0.0:
                print("✓ 恶名度修改成功！")
            else:
                print(f"⚠ 恶名度值不为0，当前值: {infamy_value}")
        else:
            print("✗ 无法找到中国恶名度设置")
        
        print("验证完成！")


def main():
    save_file = "China1836_04_29.v2"
    
    print("="*60)
    print("Victoria II 中国恶名度修改工具")
    print("="*60)
    print(f"目标文件: {save_file}")
    print("目标恶名度: 0.000")
    print("="*60)
    
    # 询问用户确认
    confirm = input("确认要修改中国恶名度吗？(输入 'yes' 确认): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    try:
        modifier = ChinaInfamyModifier(save_file)
        success = modifier.modify_china_infamy()
        
        if success:
            modifier.verify_modifications()
            
            print("\n" + "="*60)
            print("✅ 中国恶名度修改成功!")
            print("📁 备份文件已创建")
            print("🎮 可以继续游戏了!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ 恶名度修改失败!")
            print("="*60)
        
    except Exception as e:
        print(f"修改过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
