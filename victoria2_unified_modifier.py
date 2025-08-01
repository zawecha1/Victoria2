#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 统一修改器 (主工具)
==================================================
集成所有Victoria II存档修改功能的统一入口工具

功能列表:
1. 人口斗争性修改 - 中国人口斗争性设为0，其他国家设为10
2. 文化修改 - 设置中国主文化和接受文化
3. 恶名度修改 - 设置中国恶名度为0
4. 中国人口属性修改 - 宗教改为mahayana，意识形态调整为温和派

最新更新: 2025年1月27日 - 集成确认的意识形态ID映射 (Liberal = ID 6)
"""

import re
import shutil
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Victoria II 意识形态ID映射 (已确认)
IDEOLOGY_MAPPING = {
    1: "Reactionary",
    2: "Fascist", 
    3: "Conservative",
    4: "Socialist",
    5: "Anarcho-Liberal",
    6: "Liberal",        # ✅ 游戏测试确认
    7: "Communist"
}

class Victoria2UnifiedModifier:
    """Victoria II 统一修改器 - 所有功能的主入口"""
    
    def __init__(self):
        self.content = ""
        self.modifications_log = []
        
        # 统计计数器
        self.militancy_changes = 0
        self.culture_changes = 0
        self.infamy_changes = 0
        self.religion_changes = 0
        self.ideology_changes = 0
        self.population_modifications = 0
        
        # 中国人口意识形态转换规则 (✅ 已确认映射)
        self.ideology_conversion_map = {
            1: 3,  # Reactionary(1) -> Conservative(3)
            2: 6,  # Fascist(2) -> Liberal(6) ✅ 确认ID 6是Liberal
            4: 3,  # Socialist(4) -> Conservative(3)  
            5: 6,  # Anarcho-Liberal(5) -> Liberal(6) ✅ 确认ID 6是Liberal
            7: 3   # Communist(7) -> Conservative(3)
        }
    
    def create_backup(self, filename: str, operation: str = "unified") -> str:
        """创建备份文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename.replace('.v2', '')}_{operation}_backup_{timestamp}.v2"
        print(f"📁 创建备份文件: {backup_filename}")
        shutil.copy2(filename, backup_filename)
        return backup_filename
    
    def load_file(self, filename: str) -> bool:
        """加载存档文件"""
        try:
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(filename, 'r', encoding=encoding, errors='ignore') as f:
                        self.content = f.read()
                    print(f"📖 文件读取完成 (编码: {encoding})，大小: {len(self.content):,} 字符")
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
            print(f"💾 文件保存完成: {filename}")
            return True
        except Exception as e:
            print(f"❌ 文件保存失败: {e}")
            return False
    
    def find_chinese_provinces(self) -> List[int]:
        """查找中国拥有的省份"""
        chinese_provinces = []
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        print("🔍 查找中国省份...")
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
        
        print(f"✅ 找到 {len(chinese_provinces)} 个中国省份")
        return chinese_provinces
    
    # ========================================
    # 功能1: 人口斗争性修改
    # ========================================
    
    def modify_population_militancy(self, china_militancy: float = 0.0, other_militancy: float = 10.0) -> bool:
        """修改人口斗争性"""
        print(f"\\n⚔️ 开始修改人口斗争性 (中国: {china_militancy}, 其他: {other_militancy})")
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\\d+)=\\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        # 首先找到中国省份
        chinese_provinces = set(self.find_chinese_provinces())
        
        total_provinces = len(province_matches)
        processed = 0
        
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 确定省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                end_pos = len(self.content)
            
            province_content = self.content[start_pos:end_pos]
            
            # 确定目标斗争性值
            target_militancy = china_militancy if province_id in chinese_provinces else other_militancy
            
            # 修改省份中的人口斗争性
            new_province_content = self._modify_province_militancy(province_content, target_militancy)
            
            if new_province_content != province_content:
                self.content = self.content[:start_pos] + new_province_content + self.content[end_pos:]
                # 重新计算后续省份的位置偏移
                offset = len(new_province_content) - len(province_content)
                for j in range(i + 1, len(province_matches)):
                    province_matches[j] = type(province_matches[j])(
                        province_matches[j].pattern,
                        province_matches[j].string,
                        province_matches[j].start() + offset,
                        province_matches[j].end() + offset
                    )
            
            processed += 1
            if processed % 100 == 0:
                print(f"   处理进度: {processed}/{total_provinces} 个省份...")
        
        print(f"✅ 斗争性修改完成: {self.militancy_changes} 处修改")
        return True
    
    def _modify_province_militancy(self, province_content: str, target_militancy: float) -> str:
        """修改单个省份的人口斗争性"""
        # 查找所有人口类型的斗争性
        pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                    'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                    'bureaucrats', 'intellectuals']
        
        modified_content = province_content
        
        for pop_type in pop_types:
            # 查找该人口类型的所有实例
            pattern = f'({pop_type}=\\s*{{[^{{}}]*}})'
            matches = list(re.finditer(pattern, modified_content, re.DOTALL))
            
            for match in reversed(matches):  # 从后往前修改避免位置偏移
                pop_block = match.group(1)
                new_pop_block = re.sub(
                    r'militancy=([\\d.]+)',
                    f'militancy={target_militancy:.5f}',
                    pop_block
                )
                
                if new_pop_block != pop_block:
                    modified_content = (modified_content[:match.start()] + 
                                      new_pop_block + 
                                      modified_content[match.end():])
                    self.militancy_changes += 1
        
        return modified_content
    
    # ========================================
    # 功能2: 文化修改
    # ========================================
    
    def modify_china_culture(self, primary_culture: str = "beifaren", 
                           accepted_cultures: List[str] = None) -> bool:
        """修改中国的文化设置"""
        if accepted_cultures is None:
            accepted_cultures = ["nanfaren", "manchu"]
        
        print(f"\\n🏛️ 开始修改中国文化 (主文化: {primary_culture}, 接受文化: {accepted_cultures})")
        
        # 查找中国国家配置
        china_pattern = r'(CHI=\\s*{[^{}]*(?:{[^{}]*}[^{}]*)*})'
        china_match = re.search(china_pattern, self.content, re.DOTALL)
        
        if not china_match:
            print("❌ 未找到中国国家配置")
            return False
        
        china_block = china_match.group(1)
        new_china_block = china_block
        
        # 修改主文化
        new_china_block = re.sub(
            r'primary_culture="?[\\w_]+"?',
            f'primary_culture="{primary_culture}"',
            new_china_block
        )
        
        # 构建接受文化字符串
        accepted_cultures_str = '\\n\\t\\t'.join([f'"{culture}"' for culture in accepted_cultures])
        
        # 修改接受文化
        if re.search(r'accepted_culture=', new_china_block):
            # 替换现有的接受文化
            new_china_block = re.sub(
                r'accepted_culture="?[\\w_]+"?',
                f'accepted_culture=\\n\\t\\t{accepted_cultures_str}',
                new_china_block
            )
        else:
            # 添加接受文化（在主文化之后）
            new_china_block = re.sub(
                r'(primary_culture="?[\\w_]+"?)',
                f'\\1\\n\\taccepted_culture=\\n\\t\\t{accepted_cultures_str}',
                new_china_block
            )
        
        if new_china_block != china_block:
            self.content = self.content.replace(china_block, new_china_block)
            self.culture_changes += 1
            print(f"✅ 中国文化修改完成")
        
        return True
    
    # ========================================
    # 功能3: 恶名度修改  
    # ========================================
    
    def modify_china_infamy(self, target_infamy: float = 0.0) -> bool:
        """修改中国的恶名度"""
        print(f"\\n😈 开始修改中国恶名度 (目标值: {target_infamy})")
        
        # 查找中国国家配置
        china_pattern = r'(CHI=\\s*{[^{}]*(?:{[^{}]*}[^{}]*)*})'
        china_match = re.search(china_pattern, self.content, re.DOTALL)
        
        if not china_match:
            print("❌ 未找到中国国家配置")
            return False
        
        china_block = china_match.group(1)
        new_china_block = china_block
        
        # 修改恶名度
        if re.search(r'badboy=', new_china_block):
            new_china_block = re.sub(
                r'badboy=[\\d.]+',
                f'badboy={target_infamy:.3f}',
                new_china_block
            )
        else:
            # 如果没有badboy字段，添加一个
            new_china_block = re.sub(
                r'(CHI=\\s*{)',
                f'\\1\\n\\tbadboy={target_infamy:.3f}',
                new_china_block
            )
        
        if new_china_block != china_block:
            self.content = self.content.replace(china_block, new_china_block)
            self.infamy_changes += 1
            print(f"✅ 中国恶名度修改完成: {target_infamy}")
        
        return True
    
    # ========================================
    # 功能4: 中国人口属性修改 (最新功能)
    # ========================================
    
    def modify_chinese_population_attributes(self) -> bool:
        """修改中国人口的宗教和意识形态属性"""
        print(f"\\n🙏 开始修改中国人口属性 (宗教→mahayana, 意识形态→温和派)")
        
        # 查找中国省份
        chinese_provinces = self.find_chinese_provinces()
        if not chinese_provinces:
            print("❌ 未找到中国省份")
            return False
        
        # 修改中国省份的人口
        for i, province_id in enumerate(chinese_provinces):
            self._modify_province_population_attributes(province_id)
            
            # 进度显示
            if (i + 1) % 20 == 0:
                print(f"   处理进度: {i + 1}/{len(chinese_provinces)} 个中国省份...")
        
        print(f"✅ 中国人口属性修改完成:")
        print(f"   宗教修改: {self.religion_changes} 处")
        print(f"   意识形态修改: {self.ideology_changes} 处")
        print(f"   总人口组修改: {self.population_modifications} 个")
        
        return True
    
    def _modify_province_population_attributes(self, province_id: int):
        """修改单个省份的中国人口属性"""
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
        new_province_content = self._modify_population_groups_in_province(province_content)
        
        # 替换省份内容
        if new_province_content != province_content:
            self.content = self.content[:start_pos] + new_province_content + self.content[current_pos-1:]
    
    def _modify_population_groups_in_province(self, province_content: str) -> str:
        """修改省份中的人口组属性"""
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
                modified_pop_block = self._modify_single_population_attributes(original_pop_block)
                
                if modified_pop_block != original_pop_block:
                    modified_content = (modified_content[:match.start()] + 
                                      modified_pop_block + 
                                      modified_content[match.end():])
                    self.population_modifications += 1
        
        return modified_content
    
    def _modify_single_population_attributes(self, pop_block: str) -> str:
        """修改单个人口组的属性"""
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
        """修改意识形态分布 (转换为温和派)"""
        # 解析现有的意识形态分布
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
        ideology_dist = {}
        
        for id_str, value_str in ideology_pairs:
            ideology_dist[int(id_str)] = float(value_str)
        
        # 应用转换规则
        transferred_to_liberal = 0.0
        transferred_to_conservative = 0.0
        
        for old_id, new_id in self.ideology_conversion_map.items():
            if old_id in ideology_dist:
                value = ideology_dist[old_id]
                
                if new_id == 6:  # Liberal = ID 6 ✅ 已确认
                    transferred_to_liberal += value
                elif new_id == 3:  # Conservative = ID 3
                    transferred_to_conservative += value
                
                # 将原意识形态设为0
                ideology_dist[old_id] = 0.0
        
        # 增加目标意识形态的值
        if transferred_to_liberal > 0:
            ideology_dist[6] = ideology_dist.get(6, 0.0) + transferred_to_liberal  # Liberal = ID 6
        
        if transferred_to_conservative > 0:
            ideology_dist[3] = ideology_dist.get(3, 0.0) + transferred_to_conservative  # Conservative = ID 3
        
        # 重新构建意识形态内容，保持原有格式
        new_lines = []
        for ideology_id in sorted(ideology_dist.keys()):
            value = ideology_dist[ideology_id]
            new_lines.append(f'{ideology_id}={value:.5f}')
        
        return '\n'.join(new_lines) + '\n\t\t'
    
    # ========================================
    # 主执行流程
    # ========================================
    
    def execute_all_modifications(self, filename: str, options: Dict[str, any] = None) -> bool:
        """执行所有修改操作"""
        if options is None:
            options = {
                'militancy': True,
                'culture': True, 
                'infamy': True,
                'population': True
            }
        
        print(f"\\n🚀 开始执行Victoria II存档全面修改")
        print(f"📁 目标文件: {filename}")
        print("="*70)
        
        # 创建备份
        backup_filename = self.create_backup(filename, "unified")
        
        # 读取文件
        if not self.load_file(filename):
            return False
        
        success_count = 0
        total_operations = sum(options.values())
        
        try:
            # 1. 人口斗争性修改
            if options.get('militancy', False):
                print(f"\\n📋 操作 1/{total_operations}: 人口斗争性修改")
                if self.modify_population_militancy(china_militancy=0.0, other_militancy=10.0):
                    success_count += 1
                    self.modifications_log.append("✅ 人口斗争性修改成功")
                else:
                    self.modifications_log.append("❌ 人口斗争性修改失败")
            
            # 2. 文化修改
            if options.get('culture', False):
                print(f"\\n📋 操作 {success_count + 1}/{total_operations}: 中国文化修改")
                if self.modify_china_culture(primary_culture="beifaren", 
                                           accepted_cultures=["nanfaren", "manchu"]):
                    success_count += 1
                    self.modifications_log.append("✅ 中国文化修改成功")
                else:
                    self.modifications_log.append("❌ 中国文化修改失败")
            
            # 3. 恶名度修改
            if options.get('infamy', False):
                print(f"\\n📋 操作 {success_count + 1}/{total_operations}: 中国恶名度修改")
                if self.modify_china_infamy(target_infamy=0.0):
                    success_count += 1
                    self.modifications_log.append("✅ 中国恶名度修改成功")
                else:
                    self.modifications_log.append("❌ 中国恶名度修改失败")
            
            # 4. 中国人口属性修改 (最新功能)
            if options.get('population', False):
                print(f"\\n📋 操作 {success_count + 1}/{total_operations}: 中国人口属性修改")
                if self.modify_chinese_population_attributes():
                    success_count += 1
                    self.modifications_log.append("✅ 中国人口属性修改成功")
                else:
                    self.modifications_log.append("❌ 中国人口属性修改失败")
            
            # 保存文件
            if not self.save_file(filename):
                print("❌ 文件保存失败")
                return False
            
            # 显示最终结果
            self._display_final_results(success_count, total_operations, backup_filename)
            
            return success_count == total_operations
            
        except Exception as e:
            print(f"❌ 修改过程中发生错误: {e}")
            # 恢复备份
            shutil.copy2(backup_filename, filename)
            print("📁 已恢复备份文件")
            return False
    
    def _display_final_results(self, success_count: int, total_operations: int, backup_filename: str):
        """显示最终结果"""
        print("\\n" + "="*70)
        print("🎯 Victoria II 统一修改器 - 执行完成")
        print("="*70)
        
        print(f"📊 操作统计:")
        print(f"   成功操作: {success_count}/{total_operations}")
        print(f"   斗争性修改: {self.militancy_changes} 处")
        print(f"   文化修改: {self.culture_changes} 处") 
        print(f"   恶名度修改: {self.infamy_changes} 处")
        print(f"   宗教修改: {self.religion_changes} 处")
        print(f"   意识形态修改: {self.ideology_changes} 处")
        print(f"   人口组修改: {self.population_modifications} 个")
        
        print(f"\\n📋 操作日志:")
        for log_entry in self.modifications_log:
            print(f"   {log_entry}")
        
        print(f"\\n📁 备份文件: {backup_filename}")
        
        if success_count == total_operations:
            print("\\n🎉 所有修改操作成功完成！")
            print("🎮 现在可以在Victoria II中加载修改后的存档了！")
        else:
            print(f"\\n⚠️  部分操作失败，请检查日志信息")

def display_menu():
    """显示功能菜单"""
    print("\\n🛠️ Victoria II 统一修改器 - 功能菜单")
    print("="*50)
    print("1. 💀 人口斗争性修改 (中国=0, 其他=10)")
    print("2. 🏛️ 中国文化修改 (主文化=beifaren, 接受=nanfaren+manchu)")
    print("3. 😈 中国恶名度修改 (设为0)")
    print("4. 🙏 中国人口属性修改 (宗教=mahayana, 意识形态=温和派)")
    print("5. 🚀 执行全部修改")
    print("6. ❓ 显示意识形态映射信息")
    print("0. 🚪 退出")
    print("="*50)

def display_ideology_info():
    """显示意识形态映射信息"""
    print("\\n🎯 Victoria II 意识形态ID映射 (游戏测试确认)")
    print("="*60)
    for id_num, name in IDEOLOGY_MAPPING.items():
        status = "✅ 确认" if id_num in [1, 2, 3, 4, 6] else "🔍 推测"
        print(f"  ID {id_num}: {name:<15} {status}")
    
    print("\\n🔄 中国人口意识形态转换规则:")
    conversion_rules = {
        "Reactionary": "Conservative",
        "Fascist": "Liberal", 
        "Socialist": "Conservative",
        "Anarcho-Liberal": "Liberal",
        "Communist": "Conservative"
    }
    for old, new in conversion_rules.items():
        print(f"  {old:<15} → {new}")
    
    print("\\n🎮 最终效果: 中国人口只有Conservative和Liberal两种温和意识形态")

def main():
    """主函数 - 交互式菜单"""
    print("🎮 Victoria II 统一修改器 v2.0")
    print("包含所有修改功能的统一入口工具")
    print("最新更新: 2025年1月27日 - 集成确认的意识形态映射")
    
    # 获取文件名
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print(f"\\n📁 从命令行获取文件名: {filename}")
    else:
        filename = input("\\n📁 请输入存档文件名: ").strip()
        if not filename:
            print("❌ 未提供文件名，退出程序")
            return
    
    modifier = Victoria2UnifiedModifier()
    
    while True:
        display_menu()
        choice = input("\\n请选择操作 (0-6): ").strip()
        
        if choice == '0':
            print("👋 感谢使用Victoria II统一修改器！")
            break
        elif choice == '1':
            print("\\n💀 执行人口斗争性修改...")
            modifier.load_file(filename)
            if modifier.modify_population_militancy():
                modifier.save_file(filename)
        elif choice == '2':
            print("\\n🏛️ 执行中国文化修改...")
            modifier.load_file(filename)
            if modifier.modify_china_culture():
                modifier.save_file(filename)
        elif choice == '3':
            print("\\n😈 执行中国恶名度修改...")
            modifier.load_file(filename)
            if modifier.modify_china_infamy():
                modifier.save_file(filename)
        elif choice == '4':
            print("\\n🙏 执行中国人口属性修改...")
            modifier.load_file(filename)
            if modifier.modify_chinese_population_attributes():
                modifier.save_file(filename)
        elif choice == '5':
            print("\\n🚀 执行全部修改...")
            options = {
                'militancy': True,
                'culture': True,
                'infamy': True, 
                'population': True
            }
            modifier.execute_all_modifications(filename, options)
        elif choice == '6':
            display_ideology_info()
        else:
            print("❌ 无效选择，请重新输入")
        
        if choice in ['1', '2', '3', '4', '5']:
            input("\\n按Enter键继续...")

if __name__ == "__main__":
    main()
