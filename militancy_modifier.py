#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 存档人口斗争性修改器
修改存档文件中各国人口的斗争性(militancy)数值
"""

import re
import time
import shutil
from typing import Dict, List

class MilitancyModifier:
    """人口斗争性修改器"""
    
    def __init__(self):
        self.content = ""
        self.province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        
    def modify_file(self, filename: str, china_militancy: float = 0.0, other_militancy: float = 10.0):
        """修改存档文件中的人口斗争性"""
        print(f"开始修改存档文件: {filename}")
        start_time = time.time()
        
        # 创建备份
        backup_filename = filename + ".backup"
        print(f"创建备份文件: {backup_filename}")
        shutil.copy2(filename, backup_filename)
        
        # 读取文件
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                self.content = f.read()
            print(f"文件读取完成，大小: {len(self.content):,} 字符")
        except Exception as e:
            print(f"文件读取失败: {e}")
            return False
        
        # 首先构建省份所有者映射
        print("构建省份-国家映射...")
        province_owners = self._build_province_owner_mapping()
        print(f"找到 {len(province_owners)} 个省份")
        
        # 修改人口斗争性
        print("开始修改人口斗争性...")
        modified_content = self._modify_militancy_in_content(
            province_owners, china_militancy, other_militancy
        )
        
        # 保存修改后的文件
        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(modified_content)
            print(f"文件保存完成")
        except Exception as e:
            print(f"文件保存失败: {e}")
            # 恢复备份
            shutil.copy2(backup_filename, filename)
            return False
        
        elapsed = time.time() - start_time
        print(f"斗争性修改完成! 耗时: {elapsed:.2f}秒")
        
        # 验证修改结果
        self._verify_modifications(filename, china_militancy, other_militancy)
        
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
    
    def _verify_modifications(self, filename: str, china_militancy: float, other_militancy: float):
        """验证修改结果"""
        print("\n验证修改结果...")
        
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
        
        print("验证完成!")


def main():
    """主函数"""
    modifier = MilitancyModifier()
    
    filename = "China1836_04_29.v2"
    china_militancy = 0.0  # 中国人口斗争性设为0
    other_militancy = 10.0  # 其他国家人口斗争性设为10
    
    print("="*60)
    print("Victoria II 人口斗争性修改工具")
    print("="*60)
    print(f"目标文件: {filename}")
    print(f"中国人口斗争性: {china_militancy}")
    print(f"其他国家人口斗争性: {other_militancy}")
    print("="*60)
    
    # 询问用户确认
    confirm = input("确认要修改存档文件吗？(输入 'yes' 确认): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    success = modifier.modify_file(filename, china_militancy, other_militancy)
    
    if success:
        print("\n" + "="*60)
        print("✅ 斗争性修改成功完成!")
        print("📁 备份文件已创建 (" + filename + ".backup)")
        print("🎮 可以继续游戏了!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ 斗争性修改失败!")
        print("🔄 文件已恢复为原始状态")
        print("="*60)


if __name__ == "__main__":
    main()
