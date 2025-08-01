#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 存档综合修改器
统一入口，包含人口斗争性、文化、恶名度修改功能
"""

import re
import time
import shutil
from typing import Dict, List, Optional
from datetime import datetime

class Victoria2Modifier:
    """Victoria II 存档修改器 - 统一工具"""
    
    def __init__(self):
        self.content = ""
        self.province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        
    def create_backup(self, filename: str, suffix: str = "") -> str:
        """创建备份文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename.replace('.v2', '')}_{suffix}_backup_{timestamp}.v2"
        print(f"创建备份文件: {backup_filename}")
        shutil.copy2(filename, backup_filename)
        return backup_filename
    
    def load_file(self, filename: str) -> bool:
        """加载存档文件"""
        try:
            # 尝试多种编码方式
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(filename, 'r', encoding=encoding, errors='ignore') as f:
                        self.content = f.read()
                    print(f"文件读取完成 (编码: {encoding})，大小: {len(self.content):,} 字符")
                    return True
                except UnicodeDecodeError:
                    continue
            
            print("所有编码尝试失败")
            return False
            
        except Exception as e:
            print(f"文件读取失败: {e}")
            return False
    
    def save_file(self, filename: str) -> bool:
        """保存修改后的文件"""
        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(self.content)
            print(f"文件保存完成: {filename}")
            return True
        except Exception as e:
            print(f"文件保存失败: {e}")
            return False
    
    # =============== 人口斗争性修改功能 ===============
    
    def modify_militancy(self, filename: str, china_militancy: float = 0.0, other_militancy: float = 10.0) -> bool:
        """修改存档文件中的人口斗争性"""
        print(f"\n{'='*60}")
        print("人口斗争性修改")
        print(f"{'='*60}")
        print(f"目标文件: {filename}")
        print(f"中国人口斗争性: {china_militancy}")
        print(f"其他国家人口斗争性: {other_militancy}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # 创建备份
        backup_filename = self.create_backup(filename, "militancy")
        
        # 读取文件
        if not self.load_file(filename):
            return False
        
        # 首先构建省份所有者映射
        print("构建省份-国家映射...")
        province_owners = self._build_province_owner_mapping()
        print(f"找到 {len(province_owners)} 个省份")
        
        # 修改人口斗争性
        print("开始修改人口斗争性...")
        self.content = self._modify_militancy_in_content(
            province_owners, china_militancy, other_militancy
        )
        
        # 保存修改后的文件
        if not self.save_file(filename):
            # 恢复备份
            shutil.copy2(backup_filename, filename)
            return False
        
        elapsed = time.time() - start_time
        print(f"斗争性修改完成! 耗时: {elapsed:.2f}秒")
        
        # 验证修改结果
        self._verify_militancy_modifications(filename, china_militancy, other_militancy)
        
        return True
    
    def _build_province_owner_mapping(self) -> Dict[int, str]:
        """构建省份ID到所有者国家的映射"""
        province_owners = {}
        province_matches = list(self.province_pattern.finditer(self.content))
        
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 找到省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+10000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 5000
            
            province_content = self.content[start_pos:end_pos]
            
            # 提取owner信息
            owner_match = re.search(r'owner="?([A-Z]{3})"?', province_content)
            if owner_match:
                province_owners[province_id] = owner_match.group(1)
            
            # 进度显示
            if (i + 1) % 500 == 0:
                print(f"已处理 {i + 1}/{len(province_matches)} 个省份映射...")
        
        return province_owners
    
    def _modify_militancy_in_content(self, province_owners: Dict[int, str], 
                                   china_militancy: float, other_militancy: float) -> str:
        """在内容中修改斗争性数值"""
        modified_content = self.content
        province_matches = list(self.province_pattern.finditer(self.content))
        
        china_changes = 0
        other_changes = 0
        
        # 从后往前处理，避免位置偏移问题
        for i in reversed(range(len(province_matches))):
            match = province_matches[i]
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 找到省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+10000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 5000
            
            province_content = modified_content[start_pos:end_pos]
            owner = province_owners.get(province_id, "")
            
            # 根据国家设置斗争性
            if owner == "CHI":
                target_militancy = china_militancy
            else:
                target_militancy = other_militancy
            
            # 修改这个省份中所有人口的斗争性
            new_province_content, changes = self._modify_province_militancy(
                province_content, target_militancy
            )
            
            if changes > 0:
                # 替换省份内容
                modified_content = (modified_content[:start_pos] + 
                                  new_province_content + 
                                  modified_content[end_pos:])
                
                if owner == "CHI":
                    china_changes += changes
                else:
                    other_changes += changes
            
            # 进度显示
            if (len(province_matches) - i) % 500 == 0:
                print(f"已处理 {len(province_matches) - i}/{len(province_matches)} 个省份...")
        
        print(f"中国人口斗争性修改: {china_changes} 个人口组")
        print(f"其他国家人口斗争性修改: {other_changes} 个人口组")
        
        return modified_content
    
    def _modify_province_militancy(self, province_content: str, target_militancy: float) -> tuple:
        """修改单个省份中所有人口的斗争性"""
        # 查找所有人口组的斗争性字段 (mil=数值)
        militancy_pattern = r'mil=([\d.]+)'
        changes = 0
        
        def replace_militancy(match):
            nonlocal changes
            changes += 1
            return f'mil={target_militancy:.5f}'
        
        modified_content = re.sub(militancy_pattern, replace_militancy, province_content)
        
        return modified_content, changes
    
    def _verify_militancy_modifications(self, filename: str, china_militancy: float, other_militancy: float):
        """验证斗争性修改结果"""
        print("\n验证斗争性修改结果...")
        
        # 重新读取文件并检查一些样本
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"验证时文件读取失败: {e}")
            return
        
        # 查找中国省份的样本
        china_sample = re.search(r'owner="?CHI"?[\s\S]{1,2000}mil=([\d.]+)', content)
        if china_sample:
            china_militancy_found = float(china_sample.group(1))
            print(f"✓ 中国人口斗争性样本: {china_militancy_found} (目标: {china_militancy})")
        
        # 查找其他国家省份的样本
        other_sample = re.search(r'owner="?([A-Z]{3})"?[\s\S]{1,2000}mil=([\d.]+)', content)
        if other_sample and other_sample.group(1) != "CHI":
            other_country = other_sample.group(1)
            other_militancy_found = float(other_sample.group(2))
            print(f"✓ {other_country}人口斗争性样本: {other_militancy_found} (目标: {other_militancy})")
        
        print("斗争性验证完成!")
    
    # =============== 文化修改功能 ===============
    
    def modify_china_culture(self, filename: str, primary_culture: str = "beifaren", 
                           accepted_cultures: List[str] = None) -> bool:
        """修改中国的文化设置"""
        if accepted_cultures is None:
            accepted_cultures = ["nanfaren", "manchu"]
        
        print(f"\n{'='*60}")
        print("中国文化修改")
        print(f"{'='*60}")
        print(f"目标文件: {filename}")
        print(f"主要文化: {primary_culture}")
        print(f"接受文化: {', '.join(accepted_cultures)}")
        print(f"{'='*60}")
        
        # 创建备份
        backup_filename = self.create_backup(filename, "culture")
        
        # 读取文件
        if not self.load_file(filename):
            return False
        
        # 查找中国数据部分
        print("查找中国数据部分...")
        china_start, china_end = self._find_china_section()
        if china_start == -1:
            print("❌ 找不到中国数据部分")
            return False
        
        china_section = self.content[china_start:china_end]
        print(f"找到中国数据段: 位置 {china_start} - {china_end}")
        
        # 修改主要文化
        new_china_section = self._modify_primary_culture_in_section(china_section, primary_culture)
        
        # 修改接受文化
        new_china_section = self._modify_accepted_cultures_in_section(new_china_section, accepted_cultures)
        
        # 替换原始内容
        self.content = self.content[:china_start] + new_china_section + self.content[china_end:]
        
        # 保存文件
        if not self.save_file(filename):
            # 恢复备份
            shutil.copy2(backup_filename, filename)
            return False
        
        print("✅ 中国文化修改完成!")
        
        # 验证修改结果
        self._verify_culture_modifications(filename, primary_culture, accepted_cultures)
        
        return True
    
    def _find_china_section(self) -> tuple:
        """查找中国数据段的开始和结束位置"""
        chi_start = self.content.find("CHI=\n{")
        if chi_start == -1:
            chi_start = self.content.find("CHI=\r\n{")
        if chi_start == -1:
            return -1, -1
        
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
        
        return -1, -1
    
    def _modify_primary_culture_in_section(self, china_section: str, primary_culture: str) -> str:
        """修改主文化"""
        print(f"修改主要文化为: {primary_culture}")
        
        # 设置主文化
        if 'primary_culture=' in china_section:
            # 替换现有的主文化设置
            new_section = re.sub(
                r'primary_culture="[^"]*"',
                f'primary_culture="{primary_culture}"',
                china_section
            )
            print(f"✓ 主要文化已设置为: {primary_culture}")
            return new_section
        else:
            # 添加新的主文化设置（在国家数据的开始部分）
            lines = china_section.split('\n')
            new_lines = []
            added = False
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                # 在开头的几行之后添加主文化设置
                if i == 1 and not added:  # 在第二行添加
                    new_lines.append(f'\tprimary_culture="{primary_culture}"')
                    added = True
            
            print(f"✓ 主要文化已添加为: {primary_culture}")
            return '\n'.join(new_lines)
    
    def _modify_accepted_cultures_in_section(self, china_section: str, accepted_cultures: List[str]) -> str:
        """修改接受文化列表"""
        print(f"修改接受文化为: {', '.join(accepted_cultures)}")
        
        # 构建新的接受文化块
        cultures_block = '\n\t\t'.join([f'"{culture}"' for culture in accepted_cultures])
        new_accepted_block = f"accepted_culture={{\n\t\t{cultures_block}\n\t}}"
        
        # 查找并替换现有的 accepted_culture 块
        if 'accepted_culture=' in china_section:
            # 使用更精确的匹配来替换整个 accepted_culture 块
            pattern = r'accepted_culture=\s*\{[^}]*\}'
            new_section = re.sub(pattern, new_accepted_block, china_section, flags=re.DOTALL)
            print(f"✓ 接受文化已更新为: {', '.join(accepted_cultures)}")
            return new_section
        else:
            # 如果没有 accepted_culture 块，添加一个
            lines = china_section.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                # 在主文化之后添加接受文化
                if 'primary_culture=' in line:
                    new_lines.append(f'\t{new_accepted_block}')
            
            print(f"✓ 接受文化已添加为: {', '.join(accepted_cultures)}")
            return '\n'.join(new_lines)
    
    def _verify_culture_modifications(self, filename: str, primary_culture: str, accepted_cultures: List[str]):
        """验证文化修改结果"""
        print("\n验证文化修改结果...")
        
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"验证时文件读取失败: {e}")
            return
        
        # 验证主要文化
        primary_match = re.search(r'CHI=\s*{[^}]*?primary_culture="?([^"\s]+)"?', content, re.DOTALL)
        if primary_match:
            found_primary = primary_match.group(1)
            print(f"✓ 主要文化: {found_primary} (目标: {primary_culture})")
        
        # 验证接受文化
        accepted_match = re.search(r'CHI=\s*{[^}]*?accepted_culture=\s*{([^}]*)}', content, re.DOTALL)
        if accepted_match:
            found_accepted = re.findall(r'"([^"]+)"', accepted_match.group(1))
            print(f"✓ 接受文化: {', '.join(found_accepted)} (目标: {', '.join(accepted_cultures)})")
        
        print("文化验证完成!")
    
    # =============== 恶名度修改功能 ===============
    
    def modify_china_infamy(self, filename: str, target_infamy: float = 0.0) -> bool:
        """修改中国的恶名度(badboy)"""
        print(f"\n{'='*60}")
        print("中国恶名度修改")
        print(f"{'='*60}")
        print(f"目标文件: {filename}")
        print(f"目标恶名度: {target_infamy}")
        print(f"{'='*60}")
        
        # 创建备份
        backup_filename = self.create_backup(filename, "infamy")
        
        # 读取文件
        if not self.load_file(filename):
            return False
        
        # 查找中国数据部分
        print("查找中国数据部分...")
        china_start, china_end = self._find_china_section()
        if china_start == -1:
            print("❌ 找不到中国数据部分")
            return False
        
        china_section = self.content[china_start:china_end]
        print(f"找到中国数据段: 位置 {china_start} - {china_end}")
        
        # 修改恶名度
        new_china_section, success = self._modify_infamy_in_section(china_section, target_infamy)
        if not success:
            print("❌ 恶名度修改失败")
            return False
        
        # 替换原始内容
        self.content = self.content[:china_start] + new_china_section + self.content[china_end:]
        
        # 保存文件
        if not self.save_file(filename):
            # 恢复备份
            shutil.copy2(backup_filename, filename)
            return False
        
        print("✅ 中国恶名度修改完成!")
        
        # 验证修改结果
        self._verify_infamy_modifications(filename, target_infamy)
        
        return True
    
    def _modify_infamy_in_section(self, china_section: str, target_infamy: float) -> tuple:
        """修改恶名度数值"""
        print(f"修改恶名度为: {target_infamy}")
        
        # 查找当前的恶名度值
        infamy_match = re.search(r'(\s+)badboy=([\d.]+)', china_section)
        if infamy_match:
            old_value = float(infamy_match.group(2))
            print(f"找到当前恶名度: {old_value}")
            
            # 替换恶名度值
            new_section = re.sub(
                r'(\s+)badboy=([\d.]+)',
                f'\\1badboy={target_infamy:.3f}',
                china_section
            )
            print(f"✓ 恶名度已设置为: {target_infamy}")
            return new_section, True
        else:
            print("❌ 恶名度修改失败，未找到 badboy 字段")
            return china_section, False
    
    def _verify_infamy_modifications(self, filename: str, target_infamy: float):
        """验证恶名度修改结果"""
        print("\n验证恶名度修改结果...")
        
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"验证时文件读取失败: {e}")
            return
        
        # 验证恶名度
        infamy_match = re.search(r'CHI=\s*{[^}]*?badboy=([\d.]+)', content, re.DOTALL)
        if infamy_match:
            found_infamy = float(infamy_match.group(1))
            print(f"✓ 中国恶名度: {found_infamy} (目标: {target_infamy})")
        
        print("恶名度验证完成!")


def print_menu():
    """打印主菜单"""
    print(f"\n{'='*60}")
    print("Victoria II 存档修改器 - 统一工具")
    print(f"{'='*60}")
    print("请选择要执行的操作:")
    print("1. 修改人口斗争性 (中国=0, 其他=10)")
    print("2. 修改中国文化 (主要: beifaren, 接受: nanfaren+manchu)")
    print("3. 修改中国恶名度 (设为0)")
    print("4. 执行全部修改 (1+2+3)")
    print("5. 自定义修改")
    print("0. 退出")
    print(f"{'='*60}")


def get_save_file() -> str:
    """获取存档文件名"""
    default_file = "China1836_01_01.v2"
    
    print(f"请输入存档文件名 (默认: {default_file}):")
    filename = input("文件名: ").strip()
    
    if not filename:
        filename = default_file
    
    return filename


def main():
    """主函数"""
    modifier = Victoria2Modifier()
    
    while True:
        print_menu()
        choice = input("请选择操作 (0-5): ").strip()
        
        if choice == "0":
            print("程序退出")
            break
        
        elif choice == "1":
            # 修改人口斗争性
            filename = get_save_file()
            
            print(f"\n即将修改文件: {filename}")
            print("中国人口斗争性: 0.0")
            print("其他国家人口斗争性: 10.0")
            
            confirm = input("确认执行吗？(输入 'yes' 确认): ")
            if confirm.lower() == 'yes':
                success = modifier.modify_militancy(filename, 0.0, 10.0)
                if success:
                    print("✅ 人口斗争性修改成功!")
                else:
                    print("❌ 人口斗争性修改失败!")
        
        elif choice == "2":
            # 修改中国文化
            filename = get_save_file()
            
            print(f"\n即将修改文件: {filename}")
            print("主要文化: beifaren")
            print("接受文化: nanfaren, manchu")
            
            confirm = input("确认执行吗？(输入 'yes' 确认): ")
            if confirm.lower() == 'yes':
                success = modifier.modify_china_culture(filename, "beifaren", ["nanfaren", "manchu"])
                if success:
                    print("✅ 中国文化修改成功!")
                else:
                    print("❌ 中国文化修改失败!")
        
        elif choice == "3":
            # 修改中国恶名度
            filename = get_save_file()
            
            print(f"\n即将修改文件: {filename}")
            print("中国恶名度: 0.0")
            
            confirm = input("确认执行吗？(输入 'yes' 确认): ")
            if confirm.lower() == 'yes':
                success = modifier.modify_china_infamy(filename, 0.0)
                if success:
                    print("✅ 中国恶名度修改成功!")
                else:
                    print("❌ 中国恶名度修改失败!")
        
        elif choice == "4":
            # 执行全部修改
            filename = get_save_file()
            
            print(f"\n即将修改文件: {filename}")
            print("将执行以下修改:")
            print("- 人口斗争性: 中国=0.0, 其他=10.0")
            print("- 中国文化: 主要=beifaren, 接受=nanfaren+manchu")
            print("- 中国恶名度: 0.0")
            
            confirm = input("确认执行全部修改吗？(输入 'yes' 确认): ")
            if confirm.lower() == 'yes':
                print("\n开始执行全部修改...")
                
                # 执行所有修改
                success1 = modifier.modify_militancy(filename, 0.0, 10.0)
                success2 = modifier.modify_china_culture(filename, "beifaren", ["nanfaren", "manchu"])
                success3 = modifier.modify_china_infamy(filename, 0.0)
                
                print(f"\n{'='*60}")
                print("全部修改完成总结:")
                print(f"人口斗争性修改: {'✅ 成功' if success1 else '❌ 失败'}")
                print(f"中国文化修改: {'✅ 成功' if success2 else '❌ 失败'}")
                print(f"中国恶名度修改: {'✅ 成功' if success3 else '❌ 失败'}")
                
                if all([success1, success2, success3]):
                    print("🎉 所有修改都成功完成!")
                else:
                    print("⚠️ 部分修改失败，请检查错误信息")
                print(f"{'='*60}")
        
        elif choice == "5":
            # 自定义修改
            filename = get_save_file()
            
            print("\n自定义修改选项:")
            print("请输入要修改的内容 (留空跳过):")
            
            # 斗争性
            china_mil = input("中国人口斗争性 (默认0.0): ").strip()
            other_mil = input("其他国家人口斗争性 (默认10.0): ").strip()
            china_mil = float(china_mil) if china_mil else 0.0
            other_mil = float(other_mil) if other_mil else 10.0
            
            # 文化
            primary = input("中国主要文化 (默认beifaren): ").strip()
            accepted = input("中国接受文化 (用逗号分隔，默认nanfaren,manchu): ").strip()
            primary = primary if primary else "beifaren"
            accepted = [c.strip() for c in accepted.split(",")] if accepted else ["nanfaren", "manchu"]
            
            # 恶名度
            infamy = input("中国恶名度 (默认0.0): ").strip()
            infamy = float(infamy) if infamy else 0.0
            
            print(f"\n即将执行自定义修改:")
            print(f"文件: {filename}")
            print(f"中国人口斗争性: {china_mil}")
            print(f"其他国家人口斗争性: {other_mil}")
            print(f"中国主要文化: {primary}")
            print(f"中国接受文化: {', '.join(accepted)}")
            print(f"中国恶名度: {infamy}")
            
            confirm = input("确认执行自定义修改吗？(输入 'yes' 确认): ")
            if confirm.lower() == 'yes':
                success1 = modifier.modify_militancy(filename, china_mil, other_mil)
                success2 = modifier.modify_china_culture(filename, primary, accepted)
                success3 = modifier.modify_china_infamy(filename, infamy)
                
                print(f"\n{'='*60}")
                print("自定义修改完成总结:")
                print(f"人口斗争性修改: {'✅ 成功' if success1 else '❌ 失败'}")
                print(f"中国文化修改: {'✅ 成功' if success2 else '❌ 失败'}")
                print(f"中国恶名度修改: {'✅ 成功' if success3 else '❌ 失败'}")
                print(f"{'='*60}")
        
        else:
            print("无效选择，请重新输入")
        
        # 询问是否继续
        if choice != "0":
            input("\n按 Enter 键继续...")


if __name__ == "__main__":
    main()
