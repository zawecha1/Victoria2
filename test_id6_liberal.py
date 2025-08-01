#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ID 6为Liberal的修改器
"""

import re
import shutil
from datetime import datetime
from typing import Dict, List, Tuple

class ChinesePopulationModifier_TestID6:
    """中国人口属性修改器 - 测试Liberal=ID 6"""
    
    def __init__(self):
        self.content = ""
        self.modifications_count = 0
        self.ideology_changes = 0
        self.religion_changes = 0
        
        # 意识形态映射规则 (测试方案B: Liberal = ID 6)
        self.ideology_mapping = {
            # 基于游戏结果分析：ID 1=Reactionary, ID 2=Fascist, ID 3=Conservative, ID 4=Socialist
            # 测试假设：ID 6=Liberal
            1: 3,  # Reactionary(1) -> Conservative(3)
            2: 6,  # Fascist(2) -> Liberal(6) - 测试ID 6是Liberal
            4: 3,  # Socialist(4) -> Conservative(3)  
            5: 6,  # Anarcho-Liberal(5) -> Liberal(6) - 测试ID 6是Liberal
            7: 3   # Communist(7) -> Conservative(3)
        }
    
    def load_file(self, filename: str) -> bool:
        """加载存档文件"""
        try:
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(filename, 'r', encoding=encoding, errors='ignore') as f:
                        self.content = f.read()
                    print(f"文件读取完成 (编码: {encoding})，大小: {len(self.content):,} 字符")
                    return True
                except UnicodeDecodeError:
                    continue
            
            print("❌ 所有编码尝试失败")
            return False
            
        except Exception as e:
            print(f"❌ 文件读取失败: {e}")
            return False
    
    def save_file(self, filename: str) -> bool:
        """保存修改后的文件"""
        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(self.content)
            print(f"文件保存完成: {filename}")
            return True
        except Exception as e:
            print(f"❌ 文件保存失败: {e}")
            return False
    
    def create_backup(self, filename: str) -> str:
        """创建备份文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename.replace('.v2', '')}_backup_id6_test_{timestamp}.v2"
        print(f"创建备份文件: {backup_filename}")
        shutil.copy2(filename, backup_filename)
        return backup_filename
    
    def find_chinese_provinces(self) -> List[int]:
        """查找中国拥有的省份"""
        chinese_provinces = []
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        print("查找中国省份...")
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 确定省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+20000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 10000
            
            province_content = self.content[start_pos:end_pos]
            
            # 检查是否为中国拥有
            owner_match = re.search(r'owner="?CHI"?', province_content)
            if owner_match:
                chinese_provinces.append(province_id)
        
        print(f"找到 {len(chinese_provinces)} 个中国省份")
        return chinese_provinces
    
    def modify_chinese_populations(self, filename: str) -> bool:
        """修改中国人口的宗教和意识形态"""
        print(f"\n{'='*70}")
        print("中国人口属性修改器 - 测试Liberal=ID 6")
        print(f"{'='*70}")
        print(f"目标文件: {filename}")
        print("修改内容:")
        print("- 所有中国人口宗教 → mahayana")
        print("- 意识形态调整 (测试Liberal=ID 6):")
        print("  • Reactionary(1) + Socialist(4) + Communist(7) → Conservative(3)")
        print("  • Fascist(2) + Anarcho-Liberal(5) → Liberal(6)")
        print(f"{'='*70}")
        
        # 创建备份
        backup_filename = self.create_backup(filename)
        
        # 读取文件
        if not self.load_file(filename):
            return False
        
        # 查找中国省份
        chinese_provinces = self.find_chinese_provinces()
        if not chinese_provinces:
            print("❌ 未找到中国省份")
            return False
        
        # 修改中国省份的人口
        print("\n开始修改中国人口属性...")
        for i, province_id in enumerate(chinese_provinces):
            self._modify_province_populations(province_id)
            
            # 进度显示
            if (i + 1) % 20 == 0:
                print(f"已处理 {i + 1}/{len(chinese_provinces)} 个中国省份...")
        
        # 保存文件
        if not self.save_file(filename):
            # 恢复备份
            shutil.copy2(backup_filename, filename)
            return False
        
        print(f"\n{'='*70}")
        print("修改完成统计:")
        print(f"宗教修改: {self.religion_changes} 处")
        print(f"意识形态修改: {self.ideology_changes} 处")
        print(f"总修改数: {self.modifications_count} 个人口组")
        print(f"{'='*70}")
        
        return True
    
    def _modify_province_populations(self, province_id: int):
        """修改单个省份的中国人口"""
        # 查找省份数据块
        province_pattern = f'^{province_id}=\\s*{{'
        province_match = re.search(province_pattern, self.content, re.MULTILINE)
        if not province_match:
            return
        
        start_pos = province_match.end()
        
        # 找到省份块的结束位置
        brace_count = 1
        current_pos = start_pos
        while current_pos < len(self.content) and brace_count > 0:
            char = self.content[current_pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            current_pos += 1
        
        if brace_count != 0:
            return
        
        province_content = self.content[start_pos:current_pos-1]
        
        # 查找并修改人口组
        new_province_content = self._modify_population_groups(province_content)
        
        # 替换省份内容
        if new_province_content != province_content:
            self.content = self.content[:start_pos] + new_province_content + self.content[current_pos-1:]
    
    def _modify_population_groups(self, province_content: str) -> str:
        """修改省份中的人口组"""
        # 查找所有人口类型
        pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                    'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                    'bureaucrats', 'intellectuals']
        
        modified_content = province_content
        
        for pop_type in pop_types:
            # 查找该人口类型的所有实例
            pattern = f'({pop_type}=\\s*{{[^{{}}]*(?:{{[^{{}}]*}}[^{{}}]*)*}})'
            matches = list(re.finditer(pattern, modified_content, re.DOTALL))
            
            # 从后往前修改，避免位置偏移
            for match in reversed(matches):
                original_pop_block = match.group(1)
                modified_pop_block = self._modify_single_population(original_pop_block)
                
                if modified_pop_block != original_pop_block:
                    modified_content = (modified_content[:match.start()] + 
                                      modified_pop_block + 
                                      modified_content[match.end():])
                    self.modifications_count += 1
        
        return modified_content
    
    def _modify_single_population(self, pop_block: str) -> str:
        """修改单个人口组"""
        modified_block = pop_block
        
        # 1. 修改宗教为 mahayana
        culture_religion_pattern = r'([a-zA-Z_]+)=([a-zA-Z_]+)(?=\s)'
        
        def replace_religion(match):
            culture = match.group(1)
            religion = match.group(2)
            
            # 排除系统字段，只处理文化=宗教
            if culture in ['id', 'size', 'money', 'literacy', 'militancy', 'consciousness', 
                          'everyday_needs', 'luxury_needs', 'ideology', 'issues']:
                return match.group(0)  # 不修改系统字段
            
            # 只修改宗教部分，保持文化不变
            self.religion_changes += 1
            return f'{culture}=mahayana'
        
        # 查找并替换文化=宗教组合
        modified_block = re.sub(culture_religion_pattern, replace_religion, modified_block)
        
        # 2. 修改意识形态分布
        ideology_pattern = r'ideology=\s*{([^{}]*)}'
        ideology_match = re.search(ideology_pattern, modified_block, re.DOTALL)
        
        if ideology_match:
            ideology_content = ideology_match.group(1)
            new_ideology_content = self._modify_ideology_distribution(ideology_content)
            
            if new_ideology_content != ideology_content:
                # 保持原有格式：ideology= 换行 { 内容 }
                modified_block = modified_block.replace(
                    ideology_match.group(0),
                    f'ideology=\n\t\t{{\n{new_ideology_content}}}'
                )
                self.ideology_changes += 1
        
        return modified_block
    
    def _modify_ideology_distribution(self, ideology_content: str) -> str:
        """修改意识形态分布"""
        # 解析现有的意识形态分布
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
        ideology_dist = {}
        
        for id_str, value_str in ideology_pairs:
            ideology_dist[int(id_str)] = float(value_str)
        
        # 应用转换规则
        total_transferred = 0.0
        transferred_to_liberal = 0.0
        transferred_to_conservative = 0.0
        
        for old_id, new_id in self.ideology_mapping.items():
            if old_id in ideology_dist:
                value = ideology_dist[old_id]
                total_transferred += value
                
                if new_id == 6:  # Liberal = ID 6 (测试中)
                    transferred_to_liberal += value
                elif new_id == 3:  # Conservative = ID 3
                    transferred_to_conservative += value
                
                # 将原意识形态设为0
                ideology_dist[old_id] = 0.0
        
        # 增加目标意识形态的值
        if transferred_to_liberal > 0:
            ideology_dist[6] = ideology_dist.get(6, 0.0) + transferred_to_liberal  # Liberal = ID 6 (测试中)
        
        if transferred_to_conservative > 0:
            ideology_dist[3] = ideology_dist.get(3, 0.0) + transferred_to_conservative  # Conservative = ID 3
        
        # 重新构建意识形态内容，保持原有格式
        new_lines = []
        for ideology_id in sorted(ideology_dist.keys()):
            value = ideology_dist[ideology_id]
            new_lines.append(f'{ideology_id}={value:.5f}')
        
        # 保持原有的格式：没有缩进的数值行，最后有制表符缩进的结束大括号
        return '\n'.join(new_lines) + '\n\t\t'

def test_id6_liberal(source_file, test_file):
    """测试ID 6为Liberal的非交互式版本"""
    
    print("🧪 意识形态映射测试 (Liberal = ID 6)")
    print("="*50)
    
    # 复制源文件到测试文件
    print(f"复制 {source_file} 到 {test_file}")
    shutil.copy2(source_file, test_file)
    
    # 创建修改器实例
    modifier = ChinesePopulationModifier_TestID6()
    
    # 执行修改
    success = modifier.modify_chinese_populations(test_file)
    
    if success:
        print("\n✅ 测试修改成功!")
        print("📁 备份文件已创建")
        
        # 显示统计信息
        print(f"\n📊 修改统计:")
        print(f"宗教修改: {modifier.religion_changes} 处")
        print(f"意识形态修改: {modifier.ideology_changes} 处")
        print(f"总修改数: {modifier.modifications_count} 个人口组")
        
        return True
    else:
        print("\n❌ 测试修改失败!")
        return False

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python test_id6_liberal.py <源文件> [测试文件名]")
        print("示例: python test_id6_liberal.py China2245_04_06.v2 test_liberal_id6.v2")
        return
    
    source_file = sys.argv[1]
    test_file = sys.argv[2] if len(sys.argv) > 2 else "test_liberal_id6.v2"
    
    # 检查源文件是否存在
    import os
    if not os.path.exists(source_file):
        print(f"❌ 源文件不存在: {source_file}")
        return
    
    # 执行测试
    success = test_id6_liberal(source_file, test_file)
    
    if success:
        print(f"\n🎯 测试完成！请检查文件: {test_file}")
        print("💡 可以用以下命令检查结果:")
        print(f"   python check_single_file.py {test_file} 3")
    else:
        print("\n❌ 测试失败!")

if __name__ == "__main__":
    main()
