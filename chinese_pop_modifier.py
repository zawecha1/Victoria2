#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 中国人口属性修改器
修改所有中国人口的宗教为 mahayana，并调整意识形态分布
"""

import re
import shutil
from datetime import datetime
from typing import Dict, List, Tuple

class ChinesePopulationModifier:
    """中国人口属性修改器"""
    
    def __init__(self):
        self.content = ""
        self.modifications_count = 0
        self.ideology_changes = 0
        self.religion_changes = 0
        
        # 意识形态映射规则 (✅ 已确认: Liberal = ID 6)
        self.ideology_mapping = {
            # 基于游戏测试确认的正确映射：
            # ID 1=Reactionary, ID 2=Fascist, ID 3=Conservative, ID 4=Socialist, ID 6=Liberal
            1: 3,  # Reactionary(1) -> Conservative(3)
            2: 6,  # Fascist(2) -> Liberal(6) ✅ 确认ID 6是Liberal
            4: 3,  # Socialist(4) -> Conservative(3)  
            5: 6,  # Anarcho-Liberal(5) -> Liberal(6) ✅ 确认ID 6是Liberal
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
        backup_filename = f"{filename.replace('.v2', '')}_chinese_pop_backup_{timestamp}.v2"
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
        print("中国人口属性修改器")
        print(f"{'='*70}")
        print(f"目标文件: {filename}")
        print("修改内容:")
        print("- 所有中国人口宗教 → mahayana")
        print("- 意识形态调整 (✅ 已确认映射):")
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
        # 查找文化=宗教模式，修改宗教部分
        # 排除id、size、money等数字字段，只匹配文化=宗教
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
                
                if new_id == 6:  # Liberal = ID 6 ✅ 已确认
                    transferred_to_liberal += value
                elif new_id == 3:  # Conservative = ID 3
                    transferred_to_conservative += value
                
                # 将原意识形态设为0
                ideology_dist[old_id] = 0.0
        
        # 增加目标意识形态的值
        if transferred_to_liberal > 0:
            ideology_dist[6] = ideology_dist.get(6, 0.0) + transferred_to_liberal  # Liberal = ID 6 ✅ 已确认
        
        if transferred_to_conservative > 0:
            ideology_dist[3] = ideology_dist.get(3, 0.0) + transferred_to_conservative  # Conservative = ID 3
        
        # 重新构建意识形态内容，保持原有格式
        new_lines = []
        for ideology_id in sorted(ideology_dist.keys()):
            value = ideology_dist[ideology_id]
            new_lines.append(f'{ideology_id}={value:.5f}')
        
        # 保持原有的格式：没有缩进的数值行，最后有制表符缩进的结束大括号
        return '\n'.join(new_lines) + '\n\t\t'
    
    def verify_modifications(self, filename: str):
        """验证修改结果"""
        print("\n验证修改结果...")
        
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 验证时文件读取失败: {e}")
            return
        
        # 统计中国人口的宗教分布
        chinese_pop_religions = {}
        
        # 查找中国省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(content))
        
        chinese_provinces = []
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+20000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 10000
            
            province_content = content[start_pos:end_pos]
            
            # 检查是否为中国拥有
            if re.search(r'owner="?CHI"?', province_content):
                chinese_provinces.append((province_id, province_content))
        
        # 分析中国省份的人口宗教
        mahayana_count = 0
        other_religion_count = 0
        
        for province_id, province_content in chinese_provinces[:5]:  # 检查前5个省份
            culture_religion_matches = re.findall(r'(\w+)=(\w+)', province_content)
            for culture, religion in culture_religion_matches:
                if not culture.isdigit() and not religion.isdigit():
                    if religion == 'mahayana':
                        mahayana_count += 1
                    else:
                        other_religion_count += 1
                        print(f"  发现非mahayana宗教: {culture}={religion} (省份{province_id})")
        
        print(f"✓ 验证样本: {mahayana_count} 个mahayana宗教人口组")
        if other_religion_count > 0:
            print(f"⚠️  仍有 {other_religion_count} 个非mahayana宗教人口组")
        else:
            print("✓ 所有检查的中国人口宗教均为mahayana")
        
        print("验证完成!")

def main():
    """主函数"""
    import sys
    
    print("Victoria II 中国人口属性修改器")
    print("="*50)
    
    # 获取文件名（支持命令行参数）
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print(f"从命令行获取文件名: {filename}")
    else:
        filename = input("请输入存档文件名 (默认: China2281_01_01.v2): ").strip()
        if not filename:
            filename = "China2281_01_01.v2"
    
    print(f"\n即将修改文件: {filename}")
    print("修改内容:")
    print("1. 所有中国人口宗教 → mahayana")
    print("2. 意识形态调整 (✅ Liberal=ID 6 已确认):")
    print("   • Reactionary(1) + Socialist(4) + Communist(7) → Conservative(3)")
    print("   • Fascist(2) + Anarcho-Liberal(5) → Liberal(6)")
    
    if len(sys.argv) > 1:
        confirm = "yes"  # 命令行模式自动确认
    else:
        confirm = input("\n确认执行修改吗？(输入 'yes' 确认): ")
    
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    # 创建修改器并执行
    modifier = ChinesePopulationModifier()
    
    success = modifier.modify_chinese_populations(filename)
    
    if success:
        print("\n✅ 中国人口属性修改成功!")
        
        # 验证修改结果
        modifier.verify_modifications(filename)
        
        print("\n📁 备份文件已创建")
        print("🎮 可以继续游戏了!")
    else:
        print("\n❌ 修改失败!")

if __name__ == "__main__":
    main()
