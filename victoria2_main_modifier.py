#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 主修改器 (victoria2_modifier.py)
==================================================
统一修改器，集成所有Victoria II存档修改功能

核心功能:
1. 人口斗争性修改 (militancy_modifier.py的功能)
2. 文化修改 (china_culture_modifier.py的功能)  
3. 恶名度修改 (china_infamy_modifier.py的功能)
4. 中国人口属性修改 (chinese_pop_modifier.py的功能) ⭐ 最新集成

最新更新: 2025年1月28日 - 完全集成确认的意识形态映射功能
"""

import re
import shutil
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 导入花括号解析器
from bracket_parser import Victoria2BracketParser, BracketBlock

class Victoria2Modifier:
    """Victoria II 主修改器 - 统一入口工具"""
    
    def __init__(self, file_path: str = None, debug_mode: bool = False):
        self.content = ""
        self.file_path = file_path
        self.parser = Victoria2BracketParser()  # 花括号解析器
        self.structure = None  # 花括号结构
        self.debug_mode = debug_mode  # 调试模式
        
        # 统计计数器
        self.militancy_changes = 0
        self.culture_changes = 0  
        self.infamy_changes = 0
        self.religion_changes = 0
        self.ideology_changes = 0
        self.population_count = 0
        self.date_changes = 0
        self.money_changes = 0  # 新增：金钱修改计数器
        
        # 默认存档路径 - 使用当前目录
        self.default_save_path = "."
        
        # 意识形态转换映射 (基于百分比系统，总和=100%)
        # 意识形态ID对应：
        # 1=Reactionary(反动派) 2=Fascist(法西斯) 3=Conservative(保守派)
        # 4=Socialist(社会主义) 5=Anarcho-Liberal(无政府自由派) 6=Liberal(自由派) 7=Communist(共产主义)
        self.ideology_mapping = {
            1: 3,  # Reactionary(1) -> Conservative(3) - 反动派转保守派
            2: 6,  # Fascist(2) -> Liberal(6) - 法西斯转自由派
            4: 3,  # Socialist(4) -> Conservative(3) - 社会主义转保守派
            5: 6,  # Anarcho-Liberal(5) -> Liberal(6) - 无政府自由派转自由派
            7: 3   # Communist(7) -> Conservative(3) - 共产主义转保守派
        }
        
        # 如果提供了文件路径，立即加载
        if file_path:
            self.load_file(file_path)
    
    def create_backup(self, filename: str, operation: str = "unified") -> str:
        """创建备份文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename.replace('.v2', '')}_{operation}_backup_{timestamp}.v2"
        print(f"创建备份文件: {backup_filename}")
        shutil.copy2(filename, backup_filename)
        return backup_filename
    
    def load_file(self, filename: str) -> bool:
        """加载存档文件并初始化解析器"""
        try:
            # 保存文件路径以供后续使用
            self.file_path = filename
            
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(filename, 'r', encoding=encoding, errors='ignore') as f:
                        self.content = f.read()
                    print(f"文件读取完成 (编码: {encoding})，大小: {len(self.content):,} 字符")
                    
                    # 初始化花括号解析器
                    self.parser.load_content(self.content)
                    print("🔍 正在解析文件结构...")
                    blocks = self.parser.parse_all_blocks()
                    
                    # 创建一个假的根结构来容纳所有块
                    from bracket_parser import BracketBlock
                    self.structure = BracketBlock("root", 0, len(self.content), self.content, 0)
                    self.structure.children = blocks
                    
                    print(f"📊 解析完成: 找到 {len(blocks)} 个顶级块")
                    
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
    
    # ========================================
    # 花括号结构安全修改方法
    # ========================================
    
    def find_china_country_block(self) -> Optional[BracketBlock]:
        """安全地查找真正的CHI国家定义块"""
        print("🔍 查找CHI国家定义块...")
        
        # 查找所有名为CHI的块
        chi_blocks = self.parser.find_blocks_by_name("CHI")
        print(f"找到 {len(chi_blocks)} 个CHI块")
        
        if not chi_blocks:
            print("❌ 未找到任何CHI块")
            return None
        
        # 分析每个CHI块，找出真正的国家定义块
        country_block = None
        max_complexity = 0
        
        for i, block in enumerate(chi_blocks):
            content_type = self.parser.analyze_content_type(block)
            child_count = len(block.children)
            complexity = len(block.content) + child_count * 100
            
            print(f"CHI块 {i+1}: 位置 {block.start_pos}-{block.end_pos}")
            print(f"  大小: {len(block.content):,} 字符")
            print(f"  类型: {content_type}")
            print(f"  子块数: {child_count}")
            print(f"  复杂度: {complexity}")
            
            # 检查是否包含国家特有字段
            country_indicators = [
                'primary_culture', 'capital', 'technology', 'ruling_party',
                'upper_house', 'government', 'plurality', 'badboy',
                'consciousness', 'mobilized', 'war_exhaustion'
            ]
            
            indicator_count = sum(1 for indicator in country_indicators 
                                if indicator in block.content)
            
            print(f"  国家指标数: {indicator_count}/{len(country_indicators)}")
            
            # 如果这个块有更多的国家指标或更高的复杂度，则认为是国家块
            if indicator_count > 3 or (indicator_count > 0 and complexity > max_complexity):
                max_complexity = complexity
                country_block = block
                print(f"  ✅ 识别为国家定义块")
            else:
                print(f"  ❌ 识别为外交关系或其他类型块")
        
        if country_block:
            print(f"🎯 确定CHI国家块: 位置 {country_block.start_pos}-{country_block.end_pos}")
            return country_block
        else:
            print("❌ 未找到有效的CHI国家定义块")
            return None
    
    def modify_block_content_safely(self, block: BracketBlock, 
                                   modifications: Dict[str, str]) -> bool:
        """在花括号块内安全地修改内容"""
        if not block:
            return False
        
        # 获取块的完整内容（包括花括号）
        block_start = block.start_pos
        block_end = block.end_pos + 1
        original_block_content = self.content[block_start:block_end]
        
        # 获取内部内容（不包括花括号）
        inner_content = block.content
        modified_inner_content = inner_content
        
        changes_made = False
        
        for key, value in modifications.items():
            # 检查是否已存在这个键
            existing_pattern = r'\b' + re.escape(key) + r'\s*=\s*[^{}\n]+'
            if re.search(existing_pattern, modified_inner_content):
                # 替换现有值
                new_inner_content = re.sub(
                    existing_pattern,
                    f'{key}={value}',
                    modified_inner_content
                )
                if new_inner_content != modified_inner_content:
                    modified_inner_content = new_inner_content
                    changes_made = True
                    print(f"  🔄 修改现有字段: {key}={value}")
            else:
                # 添加新字段（在开头添加）
                modified_inner_content = f'\n\t{key}={value}' + modified_inner_content
                changes_made = True
                print(f"  ➕ 添加新字段: {key}={value}")
        
        if changes_made:
            # 重构完整的块内容
            new_block_content = f'{{\n\t{modified_inner_content.strip()}\n}}'
            
            # 替换原始内容
            self.content = (self.content[:block_start] + 
                          new_block_content + 
                          self.content[block_end:])
            
            # 重新解析结构
            self.parser.load_content(self.content)
            return True
        
        return False
    
    def find_nested_block_safely(self, parent_block: BracketBlock, 
                                block_name: str) -> Optional[BracketBlock]:
        """在父块中安全地查找嵌套块"""
        for child in parent_block.children:
            if child.name == block_name:
                return child
        return None
    
    def modify_nested_block_safely(self, parent_block: BracketBlock,
                                  block_name: str, new_content: List[str]) -> bool:
        """安全地修改嵌套块（如culture块）"""
        nested_block = self.find_nested_block_safely(parent_block, block_name)
        
        if nested_block:
            # 修改现有块
            formatted_content = '\n\t\t' + '\n\t\t'.join([f'"{item}"' for item in new_content])
            new_block_content = f'{block_name}=\n\t{{\n\t\t{formatted_content}\n\t}}'
            
            # 替换嵌套块
            block_start = nested_block.start_pos
            block_end = nested_block.end_pos + 1
            
            # 找到块名称的开始位置
            name_start = block_start
            while name_start > 0 and self.content[name_start-1:name_start] != '\n':
                name_start -= 1
            
            self.content = (self.content[:name_start] + 
                          new_block_content + 
                          self.content[block_end:])
            
            # 重新解析
            self.parser.load_content(self.content)
            return True
        else:
            # 在父块中添加新的嵌套块
            formatted_content = '\n\t\t' + '\n\t\t'.join([f'"{item}"' for item in new_content])
            new_block_content = f'\n\t{block_name}=\n\t{{\n\t\t{formatted_content}\n\t}}'
            
            # 在父块内容的开头插入
            parent_start = parent_block.start_pos + 1  # 跳过开始的{
            self.content = (self.content[:parent_start] + 
                          new_block_content + 
                          self.content[parent_start:])
            
            # 重新解析
            self.parser.load_content(self.content)
            return True
    
    # ========================================
    # 功能1: 人口斗争性修改
    # ========================================
    
    def modify_militancy(self, china_militancy: float = 0.0, other_militancy: float = 10.0) -> bool:
        """修改人口斗争性 - 中国人口斗争性设为0，其他国家设为10"""
        print(f"\n⚔️ 开始修改人口斗争性 (中国: {china_militancy}, 其他: {other_militancy})")
        
        # 🔍 第一步：使用分析功能找到目标块
        print("📊 第一步：分析并定位目标块...")
        target_blocks = self.find_blocks_by_function_type('militancy')
        
        if not target_blocks:
            print("❌ 未找到任何省份块，无法执行人口斗争性修改")
            return False
        
        print(f"✅ 找到 {len(target_blocks)} 个目标省份块，验证类型一致性通过")
        
        # ✅ 使用与原始militancy_modifier.py相同的逻辑
        # 首先构建省份所有者映射
        print("🗺️ 构建省份-国家映射...")
        province_owners = self._build_province_owner_mapping()
        print(f"找到 {len(province_owners)} 个省份")
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
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
            
            province_content = self.content[start_pos:end_pos]
            owner = province_owners.get(province_id, "")
            
            # 根据国家设置斗争性
            if owner == "CHI":
                target_militancy = china_militancy
            else:
                target_militancy = other_militancy
            
            # 修改这个省份中所有人口的斗争性
            new_province_content, changes = self._modify_province_militancy_with_count(
                province_content, target_militancy
            )
            
            if changes > 0:
                # 替换省份内容
                self.content = (self.content[:start_pos] + 
                              new_province_content + 
                              self.content[end_pos:])
                
                if owner == "CHI":
                    china_changes += changes
                else:
                    other_changes += changes
            
            # 进度显示
            if (len(province_matches) - i) % 500 == 0:
                print(f"已处理 {len(province_matches) - i}/{len(province_matches)} 个省份...")
        
        print(f"✅ 中国人口斗争性修改: {china_changes} 个人口组")
        print(f"✅ 其他国家人口斗争性修改: {other_changes} 个人口组")
        self.militancy_changes = china_changes + other_changes
        
        print(f"✅ 斗争性修改完成: {self.militancy_changes} 处修改")
        return True
    
    def _build_province_owner_mapping(self) -> Dict[int, str]:
        """构建省份ID到所有者国家的映射"""
        province_owners = {}
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
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
    
    def _modify_province_militancy_with_count(self, province_content: str, target_militancy: float) -> tuple:
        """修改单个省份中所有人口的斗争性，返回内容和修改数量"""
        # 查找所有人口组的斗争性字段 (mil=数值)
        militancy_pattern = r'mil=([\d.]+)'
        changes = 0
        
        def replace_militancy(match):
            nonlocal changes
            changes += 1
            return f'mil={target_militancy:.5f}'
        
        modified_content = re.sub(militancy_pattern, replace_militancy, province_content)
        
        return modified_content, changes
    
    def _modify_province_militancy(self, province_content: str, target_militancy: float) -> str:
        """修改单个省份的人口斗争性"""
        # ✅ 修复: Victoria 2存档中斗争性字段是 'mil=' 而不是 'militancy='
        militancy_pattern = r'mil=([\d.]+)'
        changes_in_province = 0
        
        def replace_militancy(match):
            nonlocal changes_in_province
            changes_in_province += 1
            return f'mil={target_militancy:.5f}'
        
        # 使用正确的字段名 'mil=' 进行替换
        modified_content = re.sub(militancy_pattern, replace_militancy, province_content)
        
        # 更新总计数器
        self.militancy_changes += changes_in_province
        
        return modified_content
    
    # ========================================
    # 功能2: 文化修改
    # ========================================
    
    def modify_china_culture(self, primary_culture: str = "beifaren", 
                           accepted_cultures: List[str] = None) -> bool:
        """修改中国的文化设置 - 基于花括号结构的安全版本"""
        if accepted_cultures is None:
            accepted_cultures = ["nanfaren", "manchu", "yankee"]
        
        print(f"\n🏛️ 开始修改中国文化 (主文化: {primary_culture}, 接受文化: {accepted_cultures})")
        
        # 🔍 第一步：使用分析功能找到目标块
        print("📊 第一步：分析并定位目标块...")
        target_blocks = self.find_blocks_by_function_type('culture')
        
        if not target_blocks:
            print("❌ 未找到CHI国家定义块，无法执行文化修改")
            return False
        
        # 如果找到多个CHI块，选择最大最复杂的那个（真正的国家定义块）
        if len(target_blocks) > 1:
            print(f"  📋 找到多个CHI块，选择最适合的...")
            china_block = max(target_blocks, key=lambda b: len(b.content) + len(b.children) * 100)
            print(f"  🎯 选择最大的CHI块: {len(china_block.content):,} 字符")
        else:
            china_block = target_blocks[0]
            
        print(f"✅ 找到CHI国家定义块，验证类型一致性通过")
        
        print(f"📍 CHI国家块分析:")
        print(f"  位置: {china_block.start_pos}-{china_block.end_pos}")
        print(f"  大小: {len(china_block.content):,} 字符")
        print(f"  子块数量: {len(china_block.children)}")
        
        # 检查当前文化设置
        current_primary = re.search(r'primary_culture\s*=\s*"?([^"\s]+)"?', china_block.content)
        
        # 查找culture子块
        culture_block = self.find_nested_block_safely(china_block, "culture")
        current_accepted = []
        if culture_block:
            # 解析当前接受文化 - 修复版：只匹配独立的文化项
            lines = culture_block.content.split('\n')
            raw_matches = []  # 用于调试
            for line in lines:
                line = line.strip()
                # 收集所有引号内容用于调试
                if '"' in line:
                    raw_matches.extend(re.findall(r'"([^"]+)"', line))
                
                # 只匹配形如 "culture_name" 的行（独立的文化项，不包含等号）
                if re.match(r'^"[^"]+"\s*$', line) and '=' not in line:
                    match = re.search(r'"([^"]+)"', line)
                    if match:
                        culture_name = match.group(1)
                        # 过滤掉明显不是文化的项目
                        if culture_name != "noculture" and not culture_name.startswith("no"):
                            current_accepted.append(culture_name)
            
            # 调试输出
            if self.debug_mode and raw_matches != current_accepted:
                print(f"  🔍 文化解析调试:")
                print(f"    原始匹配: {raw_matches}")
                print(f"    过滤后: {current_accepted}")
                filtered_out = [item for item in raw_matches if item not in current_accepted]
                if filtered_out:
                    print(f"    已过滤: {filtered_out}")
        else:
            if self.debug_mode:
                print(f"  ⚠️ 未找到culture子块")
        
        print(f"📊 当前文化配置:")
        print(f"  主文化: {current_primary.group(1) if current_primary else '未设置'}")
        print(f"  接受文化: {current_accepted if current_accepted else '未设置'}")
        
        changes_made = False
        
        # 1. 修改主文化
        if not current_primary or current_primary.group(1) != primary_culture:
            modifications = {"primary_culture": f'"{primary_culture}"'}
            if self.modify_block_content_safely(china_block, modifications):
                print(f"✅ 主文化修改: {current_primary.group(1) if current_primary else '无'} → {primary_culture}")
                changes_made = True
                # 注意：块对象本身不需要重新获取，因为我们只是修改了内容
        else:
            print(f"ℹ️ 主文化已经是 {primary_culture}，无需修改")
        
        # 2. 修改接受文化  
        # 确保china_block不为None
        if china_block is None:
            print("❌ CHI国家块为空，无法修改接受文化")
            return False
            
        if set(current_accepted) != set(accepted_cultures):
            if self.modify_nested_block_safely(china_block, "culture", accepted_cultures):
                print(f"✅ 接受文化修改: {current_accepted} → {accepted_cultures}")
                changes_made = True
        else:
            print(f"ℹ️ 接受文化已经是 {accepted_cultures}，无需修改")
        
        if changes_made:
            self.culture_changes += 1
            print(f"🎉 中国文化修改完成")
        else:
            print(f"ℹ️ 文化设置已经是目标值，无需修改")
        
        return True
    
    # ========================================
    # 功能3: 恶名度修改
    # ========================================
    
    def modify_china_infamy(self, target_infamy: float = 0.0) -> bool:
        """修改中国的恶名度 - 基于花括号结构的安全版本"""
        print(f"\n😈 开始修改中国恶名度 (目标值: {target_infamy})")
        
        # 🔍 第一步：使用分析功能找到目标块
        print("📊 第一步：分析并定位目标块...")
        target_blocks = self.find_blocks_by_function_type('infamy')
        
        if not target_blocks:
            print("❌ 未找到CHI国家定义块，无法执行恶名度修改")
            return False
        
        # 如果找到多个CHI块，选择最大最复杂的那个（真正的国家定义块）
        if len(target_blocks) > 1:
            print(f"  📋 找到多个CHI块，选择最适合的...")
            china_block = max(target_blocks, key=lambda b: len(b.content) + len(b.children) * 100)
            print(f"  🎯 选择最大的CHI块: {len(china_block.content):,} 字符")
        else:
            china_block = target_blocks[0]
            
        print(f"✅ 找到CHI国家定义块，验证类型一致性通过")
        
        print(f"📍 CHI国家块分析:")
        print(f"  位置: {china_block.start_pos}-{china_block.end_pos}")
        print(f"  大小: {len(china_block.content):,} 字符")
        
        # 查找当前badboy值
        current_badboy_match = re.search(r'badboy\s*=\s*([\d.]+)', china_block.content)
        current_badboy = float(current_badboy_match.group(1)) if current_badboy_match else None
        
        print(f"📊 当前恶名度值: {current_badboy if current_badboy is not None else '未设置'}")
        
        # 检查是否需要修改
        if current_badboy is not None and abs(current_badboy - target_infamy) < 0.001:
            print(f"ℹ️ 恶名度已经是目标值 {target_infamy}，无需修改")
            return True
        
        # 修改恶名度
        modifications = {"badboy": f"{target_infamy:.3f}"}
        if self.modify_block_content_safely(china_block, modifications):
            print(f"✅ 恶名度修改: {current_badboy if current_badboy is not None else '无'} → {target_infamy:.3f}")
            self.infamy_changes += 1
            print(f"🎉 中国恶名度修改完成")
            return True
        else:
            print(f"❌ 恶名度修改失败")
            return False
    
    # ========================================
    # 功能5: 游戏日期修改
    # ========================================
    
    def modify_game_date(self, target_date: str = "1836.1.1") -> bool:
        """修改游戏中的所有日期为指定日期 - 优化版本"""
        print(f"\n📅 开始修改游戏日期 (目标日期: {target_date})")
        
        # 验证目标日期格式
        target_pattern = r'^(\d{4})\.(\d{1,2})\.(\d{1,2})$'
        if not re.match(target_pattern, target_date):
            print(f"❌ 目标日期格式无效: {target_date}")
            print("正确格式: YYYY.M.D (例如: 1836.1.1)")
            return False
        
        # 🚀 优化：使用单次正则替换，避免字符串重复拆分
        date_pattern = r'(?<![a-zA-Z0-9_])(\d{4})\.(\d{1,2})\.(\d{1,2})(?![a-zA-Z0-9_])'
        
        # 先分析要修改的日期（用于统计和显示）
        print("🔍 分析日期分布...")
        matches = list(re.finditer(date_pattern, self.content))
        
        if not matches:
            print("❌ 未找到任何日期格式")
            return False
        
        print(f"🔍 找到 {len(matches)} 个日期需要修改")
        
        # 🚀 优化：快速统计日期类型（仅采样前100个以提高速度）
        sample_size = min(100, len(matches))
        date_types = {}
        
        for i, match in enumerate(matches[:sample_size]):
            original_date = match.group(0)
            start_pos = max(0, match.start() - 20)
            end_pos = min(len(self.content), match.end() + 20)
            context = self.content[start_pos:end_pos]
            
            # 快速分析日期类型
            if 'date=' in context or 'start_date=' in context:
                date_type = "游戏开始日期"
            elif 'last_election=' in context:
                date_type = "选举日期" 
            elif 'birth_date=' in context:
                date_type = "出生日期"
            elif 'end_date=' in context:
                date_type = "结束日期"
            else:
                date_type = "其他日期"
            
            if date_type not in date_types:
                date_types[date_type] = []
            date_types[date_type].append(original_date)
        
        # 显示采样的日期类型统计
        print(f"📊 日期类型分析 (采样前{sample_size}个):")
        for date_type, dates in date_types.items():
            unique_dates = list(set(dates))
            estimated_total = len(dates) * len(matches) // sample_size
            print(f"  • {date_type}: ~{estimated_total} 处 (示例: {unique_dates[:2]})")
        
        # 🚀 关键优化：使用单次正则替换代替逐个替换
        print("⚡ 执行高速批量替换...")
        
        def replace_date(match):
            """替换函数"""
            self.date_changes += 1
            return target_date
        
        # 单次正则替换 - O(n) 时间复杂度
        start_time = __import__('time').time()
        modified_content = re.sub(date_pattern, replace_date, self.content)
        end_time = __import__('time').time()
        
        # 更新内容
        self.content = modified_content
        
        print(f"✅ 日期修改完成: {self.date_changes} 处修改")
        print(f"⚡ 处理时间: {end_time - start_time:.2f} 秒")
        print(f"🎯 所有日期已修改为: {target_date}")
        
        return True
    
    def modify_game_date_selective(self, target_date: str = "1836.1.1", 
                                 date_types: List[str] = None) -> bool:
        """选择性修改特定类型的日期"""
        if date_types is None:
            date_types = ["游戏开始日期", "选举日期", "结束日期"]  # 默认不修改出生日期
        
        print(f"\n📅 开始选择性修改游戏日期 (目标日期: {target_date})")
        print(f"修改类型: {date_types}")
        
        # 验证目标日期格式
        target_pattern = r'^(\d{4})\.(\d{1,2})\.(\d{1,2})$'
        if not re.match(target_pattern, target_date):
            print(f"❌ 目标日期格式无效: {target_date}")
            return False
        
        # 使用正则表达式查找所有日期
        date_pattern = r'(?<![a-zA-Z0-9_])(\d{4})\.(\d{1,2})\.(\d{1,2})(?![a-zA-Z0-9_])'
        matches = list(re.finditer(date_pattern, self.content))
        
        if not matches:
            print("❌ 未找到任何日期格式")
            return False
        
        # 筛选需要修改的日期
        matches_to_modify = []
        for match in matches:
            start_pos = max(0, match.start() - 30)
            end_pos = min(len(self.content), match.end() + 10)
            context = self.content[start_pos:end_pos]
            
            # 判断日期类型 - 更精确的匹配
            should_modify = False
            date_type = "其他日期"
            
            # 查找最近的等号前的字段名
            before_date = self.content[max(0, match.start() - 30):match.start()]
            
            if 'birth_date=' in before_date:
                date_type = "出生日期"
                if "出生日期" in date_types:
                    should_modify = True
            elif 'last_election=' in before_date:
                date_type = "选举日期"
                if "选举日期" in date_types:
                    should_modify = True
            elif 'end_date=' in before_date:
                date_type = "结束日期"
                if "结束日期" in date_types:
                    should_modify = True
            elif 'start_date=' in before_date or 'date=' in before_date:
                date_type = "游戏开始日期"
                if "游戏开始日期" in date_types:
                    should_modify = True
            else:
                date_type = "其他日期"
                if "其他日期" in date_types:
                    should_modify = True
            
            if should_modify:
                matches_to_modify.append(match)
                print(f"  将修改: {match.group(0)} ({date_type})")
            else:
                print(f"  跳过: {match.group(0)} ({date_type})")
        
        if not matches_to_modify:
            print("❌ 未找到符合条件的日期")
            return False
        
        print(f"🔍 找到 {len(matches_to_modify)} 个符合条件的日期需要修改")
        
        # 优化的批量替换 - 使用正则表达式一次性替换所有匹配的日期
        if matches_to_modify:
            # 创建一个集合，包含所有需要替换的起始位置
            positions_to_replace = {match.start() for match in matches_to_modify}
            
            # 使用正则表达式替换，但只替换指定位置的匹配
            def replace_func(match):
                if match.start() in positions_to_replace:
                    self.date_changes += 1
                    return target_date
                return match.group(0)
            
            self.content = re.sub(date_pattern, replace_func, self.content)
        
        print(f"✅ 选择性日期修改完成: {self.date_changes} 处修改")
        print(f"🎯 符合条件的日期已修改为: {target_date}")
        
        return True
    
    # ========================================
    # 功能4: 中国人口属性修改 (核心功能)
    # ========================================
    
    def modify_chinese_population(self, max_provinces: int = None) -> bool:
        """修改中国人口的宗教和意识形态属性 - 增强版：处理全球所有省份"""
        print(f"\n🙏 开始修改全球中国人口属性 (宗教→mahayana, 意识形态→温和派)")
        print("- 意识形态调整 (✅ 已确认映射):")
        print("  • Reactionary(1) + Socialist(4) + Communist(7) → Conservative(3)")
        print("  • Fascist(2) + Anarcho-Liberal(5) → Liberal(6)")
        
        # 使用全球人口修改方法，处理所有省份中的所有人口
        print("🌍 使用全球方法确保所有人口都被修改...")
        return self._modify_all_population_ideology_global(max_provinces)
        print(f"📝 共收集到 {len(all_modifications)} 个需要修改的人口块")
        
        # 安全地进行所有替换
        for mod in all_modifications:
            self.content = (self.content[:mod['start_pos']] + 
                           mod['new_content'] + 
                           self.content[mod['end_pos'] + 1:])
            self.population_count += 1
        
        print(f"✅ 中国人口属性修改完成:")
        print(f"宗教修改: {self.religion_changes} 处")
        print(f"意识形态修改: {self.ideology_changes} 处")
        print(f"总修改数: {self.population_count} 个人口组")
        
        return True
    
    def _modify_chinese_population_traditional(self, max_provinces: int = None) -> bool:
        """传统方法修改中国人口属性（备用方案）"""
        print("🔄 使用传统方法修改中国人口属性...")
        
        # 查找中国省份
        chinese_provinces = self.find_chinese_provinces()
        if not chinese_provinces:
            print("❌ 未找到中国省份")
            return False
        
        # 确定要处理的省份数量
        if max_provinces is None:
            max_provinces = len(chinese_provinces)
        
        provinces_to_process = chinese_provinces[:max_provinces]
        print(f"📊 处理范围：{len(provinces_to_process)}/{len(chinese_provinces)} 个中国省份")
        
        # 修改中国省份的人口
        for i, province_id in enumerate(provinces_to_process):
            self._modify_province_populations_traditional(province_id)
            
            # 进度显示
            if (i + 1) % 10 == 0 or i == len(provinces_to_process) - 1:
                print(f"已处理 {i + 1}/{len(provinces_to_process)} 个中国省份...")
        
        print(f"✅ 中国人口属性修改完成:")
        print(f"宗教修改: {self.religion_changes} 处")
        print(f"意识形态修改: {self.ideology_changes} 处")
        print(f"总修改数: {self.population_count} 个人口组")
        
        return True
    
    def _modify_province_populations_traditional(self, province_id: int):
        """传统方法修改单个省份的中国人口"""
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
        new_province_content = self._modify_population_groups_traditional(province_content)
        
        # 替换省份内容
        if new_province_content != province_content:
            self.content = self.content[:start_pos] + new_province_content + self.content[current_pos-1:]
    
    def _modify_population_groups_traditional(self, province_content: str) -> str:
        """传统方法修改省份中的人口组"""
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
                modified_pop_block = self._modify_single_population_traditional(original_pop_block)
                
                if modified_pop_block != original_pop_block:
                    modified_content = (modified_content[:match.start()] + 
                                      modified_pop_block + 
                                      modified_content[match.end():])
                    self.population_count += 1
        
        return modified_content
    
    def _modify_single_population_traditional(self, pop_block: str) -> str:
        """传统方法修改单个人口组 - 修复版：处理所有文化，安全替换"""
        modified_block = pop_block
        
        # 1. 修改宗教为 mahayana - 修复版：只匹配真正的宗教字段
        # 使用更精确的正则表达式，只匹配已知的宗教名称
        known_religions = ['catholic', 'protestant', 'orthodox', 'sunni', 'shiite', 'gelugpa', 
                          'hindu', 'sikh', 'shinto', 'mahayana', 'theravada', 'animist', 
                          'fetishist', 'jewish']
        
        # 构建精确的文化宗教模式：文化名=宗教名
        religion_alternatives = '|'.join(known_religions)
        culture_religion_pattern = rf'(\w+)=({religion_alternatives})'
        
        def replace_religion(match):
            culture = match.group(1)
            religion = match.group(2)
            self.religion_changes += 1
            return f'{culture}=mahayana'
        
        # 一次性替换所有文化宗教
        modified_block = re.sub(culture_religion_pattern, replace_religion, modified_block)
        
        # 2. 修改意识形态分布 - 修复版本（传统方法）
        ideology_pattern = r'ideology=\s*\{[^}]*\}'
        ideology_match = re.search(ideology_pattern, modified_block, re.DOTALL)
        
        if ideology_match:
            # 提取完整的ideology块
            full_ideology_block = ideology_match.group(0)
            # 提取花括号内的内容
            inner_content_match = re.search(r'ideology=\s*\{([^}]*)\}', full_ideology_block, re.DOTALL)
            
            if inner_content_match:
                ideology_content = inner_content_match.group(1)
                
                # 解析现有意识形态数据，检查是否需要转换
                ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
                ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
                
                # 检查是否有需要转换的旧意识形态
                has_old_ideologies = any(ideology_dist.get(old_id, 0) > 0 for old_id in [1, 2, 4, 5, 7])
                
                if has_old_ideologies:
                    if self.debug_mode:
                        print(f"    🔄 [传统] 发现需要转换的意识形态: {ideology_dist}")
                    
                    new_ideology_content = self._modify_ideology_distribution(ideology_content)
                    
                    # 构建新的ideology块，保持原有缩进格式
                    new_ideology_block = f'ideology=\n\t\t{{\n\t\t\t{new_ideology_content}\n\t\t}}'
                    modified_block = modified_block.replace(full_ideology_block, new_ideology_block)
                    self.ideology_changes += 1
                    
                    if self.debug_mode:
                        print(f"    ✅ [传统] 意识形态块已更新")
                else:
                    if self.debug_mode:
                        print(f"    ℹ️ [传统] 无需转换的意识形态: {ideology_dist}")
        
        return modified_block
    
    def _modify_all_population_ideology_global(self, max_provinces: int = None) -> bool:
        """全局方法修改所有省份中所有人口的意识形态 - 确保不遗漏任何人口"""
        print("🌍 开始全局意识形态修改...")
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        print(f"📊 找到 {len(province_matches)} 个省份")
        
        # 确定要处理的省份数量
        if max_provinces is None:
            max_provinces = len(province_matches)
        
        provinces_to_process = min(max_provinces, len(province_matches))
        print(f"📊 处理范围：{provinces_to_process}/{len(province_matches)} 个省份")
        
        # 从后往前处理，避免位置偏移问题
        for i in reversed(range(provinces_to_process)):
            match = province_matches[i]
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 找到省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                # 寻找下一个主要块的开始
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+50000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 20000  # 保守估计
            
            province_content = self.content[start_pos:end_pos]
            
            # 修改这个省份中的所有人口意识形态
            new_province_content = self._modify_province_all_populations(province_content)
            
            if new_province_content != province_content:
                # 替换省份内容
                self.content = (self.content[:start_pos] + 
                              new_province_content + 
                              self.content[end_pos:])
            
            # 进度显示
            processed = provinces_to_process - i
            if processed % 100 == 0 or processed == provinces_to_process:
                print(f"已处理 {processed}/{provinces_to_process} 个省份...")
        
        print(f"✅ 全局人口意识形态修改完成:")
        print(f"宗教修改: {self.religion_changes} 处")
        print(f"意识形态修改: {self.ideology_changes} 处")
        print(f"总修改数: {self.population_count} 个人口组")
        
        return True
    
    def _modify_province_all_populations(self, province_content: str) -> str:
        """修改单个省份中的所有人口意识形态"""
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
                modified_pop_block = self._modify_single_population_ideology_only(original_pop_block)
                
                if modified_pop_block != original_pop_block:
                    modified_content = (modified_content[:match.start()] + 
                                      modified_pop_block + 
                                      modified_content[match.end():])
                    self.population_count += 1
        
        return modified_content
    
    def _modify_single_population_ideology_only(self, pop_block: str) -> str:
        """只修改单个人口组的意识形态 - 不修改宗教，避免过度修改"""
        modified_block = pop_block
        
        # 只修改意识形态分布，不修改宗教
        ideology_pattern = r'ideology=\s*\{[^}]*\}'
        ideology_match = re.search(ideology_pattern, modified_block, re.DOTALL)
        
        if ideology_match:
            # 提取完整的ideology块
            full_ideology_block = ideology_match.group(0)
            # 提取花括号内的内容
            inner_content_match = re.search(r'ideology=\s*\{([^}]*)\}', full_ideology_block, re.DOTALL)
            
            if inner_content_match:
                ideology_content = inner_content_match.group(1)
                
                # 解析现有意识形态数据，检查是否需要转换
                ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
                ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
                
                # 检查是否有需要转换的旧意识形态
                has_old_ideologies = any(ideology_dist.get(old_id, 0) > 0 for old_id in [1, 2, 4, 5, 7])
                
                if has_old_ideologies:
                    if self.debug_mode:
                        print(f"    🔄 [全局] 发现需要转换的意识形态: {ideology_dist}")
                    
                    new_ideology_content = self._modify_ideology_distribution(ideology_content)
                    
                    # 构建新的ideology块，保持原有缩进格式
                    new_ideology_block = f'ideology=\n\t\t{{\n\t\t\t{new_ideology_content}\n\t\t}}'
                    modified_block = modified_block.replace(full_ideology_block, new_ideology_block)
                    self.ideology_changes += 1
                    
                    if self.debug_mode:
                        print(f"    ✅ [全局] 意识形态块已更新")
                else:
                    if self.debug_mode:
                        print(f"    ℹ️ [全局] 无需转换的意识形态: {ideology_dist}")
        
        return modified_block

    def find_chinese_provinces_structured(self) -> List[BracketBlock]:
        """基于花括号结构查找中国省份"""
        chinese_provinces = []
        
        # 已知的中国省份ID范围和特定ID
        chinese_province_ranges = [
            (1496, 1616),  # 主要中国省份
            (2562, 2648),  # 其他中国区域
        ]
        specific_chinese_provinces = [1609, 1612, 1498, 1499]
        
        # 在结构中查找省份块
        for block in self.structure.children:
            # 检查是否为数字开头的块（可能是省份）
            if re.match(r'^\d+$', block.name.strip()):
                province_id = int(block.name.strip())
                
                # 检查是否为中国省份ID范围
                is_chinese = False
                for start, end in chinese_province_ranges:
                    if start <= province_id <= end:
                        is_chinese = True
                        break
                
                if not is_chinese and province_id in specific_chinese_provinces:
                    is_chinese = True
                
                if is_chinese:
                    # 进一步检查是否包含owner=CHI
                    if 'owner="CHI"' in block.content or 'owner=CHI' in block.content:
                        chinese_provinces.append(block)
        
        print(f"📍 找到 {len(chinese_provinces)} 个中国省份 (结构化方法)")
        return chinese_provinces
    
    def _collect_province_modifications(self, province_block: BracketBlock) -> List[Dict]:
        """收集单个省份中需要修改的人口块信息，不立即执行修改"""
        # 查找省份中的人口类型块
        pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                    'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                    'bureaucrats', 'intellectuals']
        
        modifications = []
        
        for child_block in province_block.children:
            # 检查块名称是否为人口类型
            if child_block.name.strip() in pop_types:
                # 修改这个人口组的内部内容（不包含外层花括号）
                old_content = child_block.content
                new_content = self._modify_single_population_structured(old_content)
                
                if new_content != old_content:
                    # 计算内部内容的位置（跳过开始的花括号）
                    inner_start_pos = child_block.start_pos + 1  # 跳过开始的 {
                    inner_end_pos = child_block.end_pos - 1      # 跳过结束的 }
                    
                    modifications.append({
                        'start_pos': inner_start_pos,
                        'end_pos': inner_end_pos,
                        'old_content': old_content,
                        'new_content': new_content
                    })
        
        return modifications
    
    def _modify_province_populations_structured(self, province_block: BracketBlock):
        """基于花括号结构修改单个省份的中国人口 - 安全版本（已弃用，保留兼容性）"""
        # 此函数已被_collect_province_modifications替代，为了兼容性保留
        modifications = self._collect_province_modifications(province_block)
        
        # 安全地进行替换（只替换内部内容，保留外层花括号）
        for mod in modifications:
            self.content = (self.content[:mod['start_pos']] + 
                           mod['new_content'] + 
                           self.content[mod['end_pos'] + 1:])
            self.population_count += 1
    
    def _modify_single_population_structured(self, pop_block: str) -> str:
        """基于花括号结构修改单个人口组 - 修复版：处理所有文化，安全替换"""
        modified_block = pop_block
        
        # 1. 修改宗教为 mahayana - 修复版：只匹配真正的宗教字段
        # 使用更精确的正则表达式，只匹配已知的宗教名称
        known_religions = ['catholic', 'protestant', 'orthodox', 'sunni', 'shiite', 'gelugpa', 
                          'hindu', 'sikh', 'shinto', 'mahayana', 'theravada', 'animist', 
                          'fetishist', 'jewish']
        
        # 构建精确的文化宗教模式：文化名=宗教名
        religion_alternatives = '|'.join(known_religions)
        culture_religion_pattern = rf'(\w+)=({religion_alternatives})'
        
        def replace_religion(match):
            culture = match.group(1)
            religion = match.group(2)
            self.religion_changes += 1
            return f'{culture}=mahayana'
        
        # 一次性替换所有文化宗教
        modified_block = re.sub(culture_religion_pattern, replace_religion, modified_block)
        
        # 2. 修改意识形态分布 - 修复版本（结构化方法）
        ideology_pattern = r'ideology=\s*\{[^}]*\}'
        ideology_match = re.search(ideology_pattern, modified_block, re.DOTALL)
        
        if ideology_match:
            # 提取完整的ideology块
            full_ideology_block = ideology_match.group(0)
            # 提取花括号内的内容
            inner_content_match = re.search(r'ideology=\s*\{([^}]*)\}', full_ideology_block, re.DOTALL)
            
            if inner_content_match:
                ideology_content = inner_content_match.group(1)
                
                # 解析现有意识形态数据，检查是否需要转换
                ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
                ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
                
                # 检查是否有需要转换的旧意识形态
                has_old_ideologies = any(ideology_dist.get(old_id, 0) > 0 for old_id in [1, 2, 4, 5, 7])
                
                if has_old_ideologies:
                    if self.debug_mode:
                        print(f"    🔄 [结构化] 发现需要转换的意识形态: {ideology_dist}")
                    
                    new_ideology_content = self._modify_ideology_distribution(ideology_content)
                    
                    # 构建新的ideology块，保持原有缩进格式
                    new_ideology_block = f'ideology=\n\t\t{{\n\t\t\t{new_ideology_content}\n\t\t}}'
                    modified_block = modified_block.replace(full_ideology_block, new_ideology_block)
                    self.ideology_changes += 1
                    
                    if self.debug_mode:
                        print(f"    ✅ [结构化] 意识形态块已更新")
                else:
                    if self.debug_mode:
                        print(f"    ℹ️ [结构化] 无需转换的意识形态: {ideology_dist}")
        
        return modified_block
    
    def _adjust_positions_after_edit(self, edit_position: int, offset: int):
        """编辑后调整所有块的位置"""
        def adjust_block_positions(block: BracketBlock):
            if block.start_pos >= edit_position:
                block.start_pos += offset
                block.end_pos += offset
            elif block.end_pos > edit_position:
                block.end_pos += offset
            
            for child in block.children:
                adjust_block_positions(child)
        
        # 调整主结构
        adjust_block_positions(self.structure)
    
    def _modify_ideology_distribution(self, ideology_content: str) -> str:
        """修改意识形态分布 - 百分比系统版本
        
        意识形态结构：
        ideology={
            1=7.89395    # Reactionary (反动派)
            2=3.94125    # Fascist (法西斯)
            3=36.15530   # Conservative (保守派)
            4=19.19250   # Socialist (社会主义)
            5=1.22287    # Anarcho-Liberal (无政府自由派)
            6=30.37112   # Liberal (自由派)
            7=1.22287    # Communist (共产主义)
        }
        百分比总和 = 100%
        """
        # 解析现有的意识形态分布
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
        ideology_dist = {}
        
        # 解析所有现有的意识形态数据
        for id_str, value_str in ideology_pairs:
            ideology_dist[int(id_str)] = float(value_str)
        
        if self.debug_mode:
            print(f"    🔍 发现意识形态分布: {ideology_dist}")
            total_percent = sum(ideology_dist.values())
            print(f"    📊 当前百分比总和: {total_percent:.5f}")
        
        # 检查是否有需要转换的旧意识形态
        has_old_ideologies = any(ideology_dist.get(old_id, 0) > 0 for old_id in [1, 2, 4, 5, 7])
        if not has_old_ideologies:
            if self.debug_mode:
                print(f"    ℹ️ 无需转换的意识形态分布")
            return ideology_content
        
        # 计算要转换的百分比
        transferred_to_liberal = 0.0      # 转移到Liberal(6)
        transferred_to_conservative = 0.0  # 转移到Conservative(3)
        changes_made = False
        
        # 根据意识形态映射规则计算转移
        for old_id, new_id in self.ideology_mapping.items():
            if old_id in ideology_dist and ideology_dist[old_id] > 0:
                value = ideology_dist[old_id]
                if self.debug_mode:
                    print(f"    🔄 转换意识形态 {old_id} -> {new_id}, 百分比: {value:.5f}%")
                
                if new_id == 6:  # Liberal = ID 6
                    transferred_to_liberal += value
                elif new_id == 3:  # Conservative = ID 3
                    transferred_to_conservative += value
                
                # 将原意识形态设为0
                ideology_dist[old_id] = 0.0
                changes_made = True
        
        # 确保目标意识形态存在
        if 6 not in ideology_dist:
            ideology_dist[6] = 0.0  # Liberal
        if 3 not in ideology_dist:
            ideology_dist[3] = 0.0  # Conservative
        
        # 增加目标意识形态的百分比
        if transferred_to_liberal > 0:
            ideology_dist[6] += transferred_to_liberal
            if self.debug_mode:
                print(f"    ✅ Liberal(6) 增加: {transferred_to_liberal:.5f}%, 总计: {ideology_dist[6]:.5f}%")
        
        if transferred_to_conservative > 0:
            ideology_dist[3] += transferred_to_conservative
            if self.debug_mode:
                print(f"    ✅ Conservative(3) 增加: {transferred_to_conservative:.5f}%, 总计: {ideology_dist[3]:.5f}%")
        
        # 验证百分比总和仍为100
        new_total = sum(ideology_dist.values())
        if self.debug_mode:
            print(f"    📊 转换后百分比总和: {new_total:.5f}%")
        
        # 归一化百分比以确保总和为100% (处理浮点精度问题)
        if new_total > 0 and abs(new_total - 100.0) > 0.00001:
            normalization_factor = 100.0 / new_total
            for ideology_id in ideology_dist:
                if ideology_dist[ideology_id] > 0:
                    ideology_dist[ideology_id] *= normalization_factor
            
            if self.debug_mode:
                normalized_total = sum(ideology_dist.values())
                print(f"    🔧 归一化后百分比总和: {normalized_total:.5f}%")
        
        # 重新构建意识形态内容，保持Victoria II格式
        new_lines = []
        for ideology_id in sorted(ideology_dist.keys()):
            value = ideology_dist[ideology_id]
            # 保持5位小数精度，这是Victoria II的标准格式
            new_lines.append(f'{ideology_id}={value:.5f}')
        
        # 构建正确的格式：每行前有制表符缩进
        formatted_content = '\n\t\t\t'.join(new_lines)
        
        if changes_made and self.debug_mode:
            print(f"    🎯 意识形态修改完成: {len([id for id, val in ideology_dist.items() if val > 0])} 个非零值")
        
        return formatted_content
    
    # ========================================
    # 功能6: 中国人口金钱修改
    # ========================================
    
    def modify_chinese_population_money(self, chinese_money: float = 9999999999.0, non_chinese_money: float = 0.0) -> bool:
        """修改所有人口的金钱数量：中国人口设为指定金额，非中国人口清零"""
        print(f"\n💰 开始修改人口金钱")
        print(f"📋 中国人口金钱 → {chinese_money:,.0f}")
        print(f"📋 非中国人口金钱 → {non_chinese_money:,.0f}")
        print("📋 将修改 money 和 bank 字段")
        
        # 🔍 第一步：使用分析功能找到目标块
        print("📊 第一步：分析并定位目标块...")
        target_blocks = self.find_blocks_by_function_type('money')
        
        if not target_blocks:
            print("❌ 未找到包含人口的省份块，无法执行金钱修改")
            return False
        
        print(f"✅ 找到 {len(target_blocks)} 个包含人口的省份块，验证类型一致性通过")
        
        # ✅ 使用与斗争性修改相同的逻辑
        # 首先构建省份所有者映射
        print("🗺️ 构建省份-国家映射...")
        province_owners = self._build_province_owner_mapping()
        chinese_province_count = sum(1 for owner in province_owners.values() if owner == "CHI")
        total_province_count = len(province_owners)
        print(f"找到 {chinese_province_count} 个中国省份")
        print(f"找到 {total_province_count - chinese_province_count} 个非中国省份")
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        chinese_money_changes = 0
        non_chinese_money_changes = 0
        chinese_provinces_processed = 0
        non_chinese_provinces_processed = 0
        
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
            
            province_content = self.content[start_pos:end_pos]
            owner = province_owners.get(province_id, "")
            
            # 根据省份所有者决定金钱数额
            if owner == "CHI":
                # 中国省份：设为指定金额
                new_province_content, changes = self._modify_province_money(
                    province_content, chinese_money, is_chinese=True
                )
                
                if changes > 0:
                    # 替换省份内容
                    self.content = (self.content[:start_pos] + 
                                  new_province_content + 
                                  self.content[end_pos:])
                    
                    chinese_money_changes += changes
                
                chinese_provinces_processed += 1
                
                # 进度显示
                if chinese_provinces_processed % 50 == 0:
                    print(f"已处理 {chinese_provinces_processed}/{chinese_province_count} 个中国省份...")
            
            elif owner and owner != "CHI":
                # 非中国省份：金钱清零
                new_province_content, changes = self._modify_province_money(
                    province_content, non_chinese_money, is_chinese=False
                )
                
                if changes > 0:
                    # 替换省份内容
                    self.content = (self.content[:start_pos] + 
                                  new_province_content + 
                                  self.content[end_pos:])
                    
                    non_chinese_money_changes += changes
                
                non_chinese_provinces_processed += 1
                
                # 进度显示（减少频率以避免刷屏）
                if non_chinese_provinces_processed % 100 == 0:
                    print(f"已处理 {non_chinese_provinces_processed} 个非中国省份...")
        
        print(f"✅ 人口金钱修改完成:")
        print(f"  🇨🇳 中国人口: {chinese_money_changes} 个人口组 (金钱设为 {chinese_money:,.0f})")
        print(f"  🌍 非中国人口: {non_chinese_money_changes} 个人口组 (金钱清零)")
        print(f"✅ 处理省份统计:")
        print(f"  🇨🇳 中国省份: {chinese_provinces_processed} 个")
        print(f"  🌍 非中国省份: {non_chinese_provinces_processed} 个")
        
        # 更新计数器
        self.money_changes = chinese_money_changes + non_chinese_money_changes
        
        return (chinese_money_changes + non_chinese_money_changes) > 0
    
    def _modify_province_money(self, province_content: str, target_money: float, is_chinese: bool = True) -> tuple:
        """修改单个省份中所有人口的金钱，返回内容和修改数量
        
        Args:
            province_content: 省份内容
            target_money: 目标金钱数额
            is_chinese: 是否为中国省份（用于日志显示）
        
        Returns:
            tuple: (修改后的内容, 修改次数)
        """
        # 查找所有人口组的金钱字段 (money=数值 和 bank=数值)
        money_pattern = r'money=([\d.]+)'
        bank_pattern = r'bank=([\d.]+)'
        changes = 0
        
        population_type = "中国人口" if is_chinese else "非中国人口"
        
        def replace_money(match):
            nonlocal changes
            changes += 1
            return f'money={target_money:.5f}'
        
        def replace_bank(match):
            nonlocal changes
            changes += 1
            return f'bank={target_money:.5f}'
        
        # 修改money字段
        modified_content = re.sub(money_pattern, replace_money, province_content)
        # 修改bank字段
        modified_content = re.sub(bank_pattern, replace_bank, modified_content)
        
        # 如果是调试模式且有修改，显示详细信息
        if changes > 0 and self.debug_mode:
            print(f"    💰 {population_type}: 修改了 {changes} 个金钱字段 → {target_money:,.0f}")
        
        return modified_content, changes

    # ========================================
    # 验证和总结功能
    # ========================================
    
    def verify_modifications(self, filename: str):
        """验证修改结果"""
        print("\n🔍 验证修改结果...")
        
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 验证时文件读取失败: {e}")
            return
        
        # 验证中国人口宗教
        chinese_provinces = self.find_chinese_provinces()
        mahayana_count = 0
        ideology_conversion_count = 0
        
        print(f"📊 验证样本：检查前5个中国省份...")
        
        for i, province_id in enumerate(chinese_provinces[:5]):  # 检查前5个省份
            print(f"  检查省份 {province_id}...")
            province_pattern = f'^{province_id}=\\s*{{'
            province_match = re.search(province_pattern, content, re.MULTILINE)
            if province_match:
                start_pos = province_match.end()
                # 找到省份块的结束位置
                brace_count = 1
                current_pos = start_pos
                while current_pos < len(content) and brace_count > 0:
                    char = content[current_pos]
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                    current_pos += 1
                
                province_content = content[start_pos:current_pos-1]
                
                # 验证宗教修改
                culture_religion_matches = re.findall(r'(\w+)=mahayana', province_content)
                mahayana_count += len(culture_religion_matches)
                
                # 验证意识形态修改
                ideology_blocks = re.findall(r'ideology=\s*\{([^}]*)\}', province_content, re.DOTALL)
                for ideology_block in ideology_blocks:
                    # 检查是否有Conservative(3)和Liberal(6)的值大于0
                    conservative_match = re.search(r'3=([\d.]+)', ideology_block)
                    liberal_match = re.search(r'6=([\d.]+)', ideology_block)
                    
                    if conservative_match and float(conservative_match.group(1)) > 0:
                        ideology_conversion_count += 1
                        print(f"    ✅ 发现Conservative(3): {conservative_match.group(1)}")
                    if liberal_match and float(liberal_match.group(1)) > 0:
                        ideology_conversion_count += 1
                        print(f"    ✅ 发现Liberal(6): {liberal_match.group(1)}")
                    
                    # 检查旧意识形态是否已清零
                    for old_id in [1, 2, 4, 5, 7]:  # Reactionary, Fascist, Socialist, Anarcho-Liberal, Communist
                        old_match = re.search(f'{old_id}=([\\d.]+)', ideology_block)
                        if old_match and float(old_match.group(1)) > 0:
                            print(f"    ⚠️ 警告：意识形态{old_id}仍有值: {old_match.group(1)}")
        
        print(f"\n📈 验证结果:")
        print(f"✅ mahayana宗教人口组: {mahayana_count} 个")
        print(f"✅ 意识形态转换成功: {ideology_conversion_count} 处")
        print("验证完成!")
    
    def verify_ideology_modifications(self, filename: str):
        """专门验证意识形态修改结果"""
        print("\n🎭 专门验证意识形态修改...")
        
        # Load the file using the same method as the modifier
        if not hasattr(self, 'content') or not self.content:
            self.load_file(filename)
        
        chinese_provinces = self.find_chinese_provinces_structured()
        print(f"📍 检查 {min(10, len(chinese_provinces))} 个中国省份的意识形态...")
        
        total_ideology_blocks = 0
        successful_conversions = 0
        failed_conversions = 0
        
        # Define population types locally like the modification function does
        pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                    'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                    'bureaucrats', 'intellectuals']
        
        for i, province_block in enumerate(chinese_provinces[:10]):  # 检查前10个省份
            # Extract province ID from the block content
            province_id_match = re.match(r'^(\d+)=', province_block.content)
            province_id = province_id_match.group(1) if province_id_match else f"Province_{i+1}"
            print(f"\n🔍 省份 {province_id}:")
            
            # Find population groups in this province using the same method as modification
            for child_block in province_block.children:
                # Check if this child block contains population types
                if any(pop_type in child_block.content for pop_type in pop_types):
                    # Look for ideology blocks within this population group
                    ideology_pattern = r'ideology=\s*\{([^}]*)\}'
                    ideology_match = re.search(ideology_pattern, child_block.content, re.DOTALL)
                    
                    if ideology_match:
                        total_ideology_blocks += 1
                        ideology_content = ideology_match.group(1)
                        
                        # Extract ideology data
                        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
                        ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
                        
                        # Check conversion success
                        has_old_ideologies = any(ideology_dist.get(old_id, 0) > 0 for old_id in [1, 2, 4, 5, 7])
                        has_new_ideologies = ideology_dist.get(3, 0) > 0 or ideology_dist.get(6, 0) > 0
                        
                        if not has_old_ideologies and has_new_ideologies:
                            successful_conversions += 1
                            print(f"  ✅ 成功转换 - Conservative: {ideology_dist.get(3, 0):.3f}, Liberal: {ideology_dist.get(6, 0):.3f}")
                        elif has_old_ideologies:
                            failed_conversions += 1
                            old_values = {id: ideology_dist.get(id, 0) for id in [1, 2, 4, 5, 7] if ideology_dist.get(id, 0) > 0}
                            print(f"  ❌ 转换失败 - 仍有旧意识形态: {old_values}")
                            print(f"     当前值 - Conservative: {ideology_dist.get(3, 0):.3f}, Liberal: {ideology_dist.get(6, 0):.3f}")
                        elif ideology_dist:
                            print(f"  ℹ️ 无旧意识形态，现有分布: {ideology_dist}")
        
        print(f"\n📊 意识形态验证统计:")
        print(f"总意识形态块数: {total_ideology_blocks}")
        print(f"成功转换: {successful_conversions}")
        print(f"转换失败: {failed_conversions}")
        print(f"成功率: {(successful_conversions / max(1, total_ideology_blocks)) * 100:.1f}%")
        
        return successful_conversions > 0
    
    def execute_selective_modifications(self, filename: str, options: Dict[str, bool]) -> bool:
        """执行选择性修改操作 - 每个功能独立读取和保存文件"""
        print(f"\n{'='*70}")
        print("Victoria II 主修改器 - 选择性修改 (安全模式)")
        print(f"{'='*70}")
        print(f"目标文件: {filename}")
        print("选择的修改项目:")
        
        selected_count = 0
        selected_operations = []
        if options.get('militancy', False):
            print("✓ 1. 人口斗争性: 中国=0, 其他=10")
            selected_operations.append('militancy')
            selected_count += 1
        if options.get('culture', False):
            print("✓ 2. 中国文化: 主文化=beifaren, 接受=nanfaren+manchu+yankee")
            selected_operations.append('culture')
            selected_count += 1
        if options.get('infamy', False):
            print("✓ 3. 中国恶名度: 设为0")
            selected_operations.append('infamy')
            selected_count += 1
        if options.get('population', False):
            print("✓ 4. 中国人口属性: 宗教=mahayana, 意识形态=温和派")
            selected_operations.append('population')
            selected_count += 1
        if options.get('date', False):
            print("✓ 5. 游戏日期: 设为1836.1.1")
            selected_operations.append('date')
            selected_count += 1
        if options.get('money', False):
            print("✓ 6. 人口金钱: 中国=9,999,999,999, 非中国=0")
            selected_operations.append('money')
            selected_count += 1
        
        if selected_count == 0:
            print("❌ 未选择任何修改项目")
            return False
            
        print("⚡ 每个功能独立执行，确保数据安全")
        print(f"{'='*70}")
        
        # 创建备份
        operation_type = "selective" if selected_count < 6 else "unified"
        backup_filename = self.create_backup(filename, operation_type)
        
        success_count = 0
        step = 1
        
        # 1. 人口斗争性修改
        if 'militancy' in selected_operations:
            print(f"\n🔄 步骤{step}: 执行人口斗争性修改...")
            self.__init__()  # 重置计数器
            if self.load_file(filename):
                if self.modify_militancy():
                    if self.save_file(filename):
                        print(f"✅ 步骤{step}完成: 斗争性修改 {self.militancy_changes} 处")
                        success_count += 1
                    else:
                        print(f"❌ 步骤{step}失败: 文件保存失败")
                else:
                    print(f"❌ 步骤{step}失败: 斗争性修改失败")
            else:
                print(f"❌ 步骤{step}失败: 文件读取失败")
            step += 1
        
        # 2. 文化修改
        if 'culture' in selected_operations:
            print(f"\n🔄 步骤{step}: 执行中国文化修改...")
            self.__init__()  # 重置计数器
            if self.load_file(filename):
                if self.modify_china_culture():
                    if self.save_file(filename):
                        print(f"✅ 步骤{step}完成: 文化修改 {self.culture_changes} 处")
                        success_count += 1
                    else:
                        print(f"❌ 步骤{step}失败: 文件保存失败")
                else:
                    print(f"❌ 步骤{step}失败: 文化修改失败")
            else:
                print(f"❌ 步骤{step}失败: 文件读取失败")
            step += 1
        
        # 3. 恶名度修改
        if 'infamy' in selected_operations:
            print(f"\n🔄 步骤{step}: 执行中国恶名度修改...")
            self.__init__()  # 重置计数器
            if self.load_file(filename):
                if self.modify_china_infamy():
                    if self.save_file(filename):
                        print(f"✅ 步骤{step}完成: 恶名度修改 {self.infamy_changes} 处")
                        success_count += 1
                    else:
                        print(f"❌ 步骤{step}失败: 文件保存失败")
                else:
                    print(f"❌ 步骤{step}失败: 恶名度修改失败")
            else:
                print(f"❌ 步骤{step}失败: 文件读取失败")
            step += 1
        
        # 4. 中国人口属性修改
        if 'population' in selected_operations:
            print(f"\n🔄 步骤{step}: 执行中国人口属性修改...")
            self.__init__()  # 重置计数器
            if self.load_file(filename):
                if self.modify_chinese_population():
                    if self.save_file(filename):
                        print(f"✅ 步骤{step}完成: 宗教修改 {self.religion_changes} 处, 意识形态修改 {self.ideology_changes} 处")
                        success_count += 1
                    else:
                        print(f"❌ 步骤{step}失败: 文件保存失败")
                else:
                    print(f"❌ 步骤{step}失败: 人口属性修改失败")
            else:
                print(f"❌ 步骤{step}失败: 文件读取失败")
            step += 1
        
        # 5. 游戏日期修改
        if 'date' in selected_operations:
            print(f"\n🔄 步骤{step}: 执行游戏日期修改...")
            self.__init__()  # 重置计数器
            if self.load_file(filename):
                if self.modify_game_date():
                    if self.save_file(filename):
                        print(f"✅ 步骤{step}完成: 日期修改 {self.date_changes} 处")
                        success_count += 1
                    else:
                        print(f"❌ 步骤{step}失败: 文件保存失败")
                else:
                    print(f"❌ 步骤{step}失败: 日期修改失败")
            else:
                print(f"❌ 步骤{step}失败: 文件读取失败")
            step += 1
        
        # 6. 中国人口金钱修改
        if 'money' in selected_operations:
            print(f"\n🔄 步骤{step}: 执行中国人口金钱修改...")
            self.__init__()  # 重置计数器
            if self.load_file(filename):
                if self.modify_chinese_population_money():
                    if self.save_file(filename):
                        print(f"✅ 步骤{step}完成: 金钱修改 {self.money_changes} 处")
                        success_count += 1
                    else:
                        print(f"❌ 步骤{step}失败: 文件保存失败")
                else:
                    print(f"❌ 步骤{step}失败: 金钱修改失败")
            else:
                print(f"❌ 步骤{step}失败: 文件读取失败")
        
        # 最终验证
        if success_count > 0:
            print(f"\n🔍 执行最终验证...")
            self.__init__()  # 重置计数器
            if self.load_file(filename):
                if 'population' in selected_operations:
                    self.verify_modifications(filename)
                    # 专门验证意识形态修改
                    if self.verify_ideology_modifications(filename):
                        print("🎭 意识形态修改验证成功!")
                    else:
                        print("⚠️ 意识形态修改可能存在问题，请检查输出")
        
        # 显示结果
        print(f"\n{'='*70}")
        print("安全模式修改完成统计:")
        print(f"成功步骤: {success_count}/{selected_count}")
        print(f"每个功能都独立执行，确保数据安全")
        print(f"{'='*70}")
        
        print(f"\n📁 备份文件已创建: {backup_filename}")
        
        if success_count == selected_count:
            print("🎉 所有选择的修改操作成功完成!")
            print("🎮 可以继续游戏了!")
        else:
            print("⚠️ 部分操作失败，请检查输出信息")
        
        return success_count == selected_count
    
    # ========================================
    # 主执行功能
    # ========================================
    
    def execute_all_modifications(self, filename: str) -> bool:
        """执行所有修改操作 - 每个功能独立读取和保存文件"""
        print(f"\n{'='*70}")
        print("Victoria II 主修改器 - 安全模式")
        print(f"{'='*70}")
        print(f"目标文件: {filename}")
        print("修改内容:")
        print("1. 人口斗争性: 中国=0, 其他=10")
        print("2. 中国文化: 主文化=beifaren, 接受=nanfaren+manchu+yankee")
        print("3. 中国恶名度: 设为0")
        print("4. 中国人口属性: 宗教=mahayana, 意识形态=温和派")
        print("5. 游戏日期: 设为1836.1.1")
        print("6. 人口金钱: 中国=9,999,999,999, 非中国=0")
        print("⚡ 每个功能独立执行，确保数据安全")
        print(f"{'='*70}")
        
        # 创建总备份
        backup_filename = self.create_backup(filename, "unified")
        
        success_count = 0
        
        # 1. 人口斗争性修改
        print(f"\n🔄 步骤1: 执行人口斗争性修改...")
        self.__init__()  # 重置计数器
        if self.load_file(filename):
            if self.modify_militancy():
                if self.save_file(filename):
                    print(f"✅ 步骤1完成: 斗争性修改 {self.militancy_changes} 处")
                    success_count += 1
                else:
                    print(f"❌ 步骤1失败: 文件保存失败")
            else:
                print(f"❌ 步骤1失败: 斗争性修改失败")
        else:
            print(f"❌ 步骤1失败: 文件读取失败")
        
        # 2. 文化修改
        print(f"\n🔄 步骤2: 执行中国文化修改...")
        self.__init__()  # 重置计数器
        if self.load_file(filename):
            if self.modify_china_culture():
                if self.save_file(filename):
                    print(f"✅ 步骤2完成: 文化修改 {self.culture_changes} 处")
                    success_count += 1
                else:
                    print(f"❌ 步骤2失败: 文件保存失败")
            else:
                print(f"❌ 步骤2失败: 文化修改失败")
        else:
            print(f"❌ 步骤2失败: 文件读取失败")
        
        # 3. 恶名度修改
        print(f"\n🔄 步骤3: 执行中国恶名度修改...")
        self.__init__()  # 重置计数器
        if self.load_file(filename):
            if self.modify_china_infamy():
                if self.save_file(filename):
                    print(f"✅ 步骤3完成: 恶名度修改 {self.infamy_changes} 处")
                    success_count += 1
                else:
                    print(f"❌ 步骤3失败: 文件保存失败")
            else:
                print(f"❌ 步骤3失败: 恶名度修改失败")
        else:
            print(f"❌ 步骤3失败: 文件读取失败")
        
        # 4. 中国人口属性修改
        print(f"\n🔄 步骤4: 执行中国人口属性修改...")
        self.__init__()  # 重置计数器
        if self.load_file(filename):
            if self.modify_chinese_population():
                if self.save_file(filename):
                    print(f"✅ 步骤4完成: 宗教修改 {self.religion_changes} 处, 意识形态修改 {self.ideology_changes} 处")
                    success_count += 1
                else:
                    print(f"❌ 步骤4失败: 文件保存失败")
            else:
                print(f"❌ 步骤4失败: 人口属性修改失败")
        else:
            print(f"❌ 步骤4失败: 文件读取失败")
        
        # 5. 游戏日期修改
        print(f"\n🔄 步骤5: 执行游戏日期修改...")
        self.__init__()  # 重置计数器
        if self.load_file(filename):
            if self.modify_game_date():
                if self.save_file(filename):
                    print(f"✅ 步骤5完成: 日期修改 {self.date_changes} 处")
                    success_count += 1
                else:
                    print(f"❌ 步骤5失败: 文件保存失败")
            else:
                print(f"❌ 步骤5失败: 日期修改失败")
        else:
            print(f"❌ 步骤5失败: 文件读取失败")
        
        # 6. 中国人口金钱修改
        print(f"\n🔄 步骤6: 执行中国人口金钱修改...")
        self.__init__()  # 重置计数器
        if self.load_file(filename):
            if self.modify_chinese_population_money():
                if self.save_file(filename):
                    print(f"✅ 步骤6完成: 金钱修改 {self.money_changes} 处")
                    success_count += 1
                else:
                    print(f"❌ 步骤6失败: 文件保存失败")
            else:
                print(f"❌ 步骤6失败: 金钱修改失败")
        else:
            print(f"❌ 步骤6失败: 文件读取失败")
        
        # 最终验证
        print(f"\n🔍 执行最终验证...")
        self.__init__()  # 重置计数器
        if self.load_file(filename):
            self.verify_modifications(filename)
            # 专门验证意识形态修改
            if self.verify_ideology_modifications(filename):
                print("🎭 意识形态修改验证成功!")
            else:
                print("⚠️ 意识形态修改可能存在问题，请检查输出")
        
        # 显示最终结果
        print(f"\n{'='*70}")
        print("安全模式修改完成统计:")
        print(f"成功步骤: {success_count}/6")
        print(f"每个功能都独立执行，确保数据安全")
        print(f"{'='*70}")
        
        print(f"\n📁 总备份文件: {backup_filename}")
        
        if success_count == 6:
            print("🎉 所有修改操作成功完成!")
            print("🎮 可以继续游戏了!")
        else:
            print("⚠️ 部分操作失败，请检查输出信息")
        
        return success_count == 6
    
    # ========================================
    # 花括号类型分析功能
    # ========================================
    
    def find_blocks_by_function_type(self, function_type: str) -> List[BracketBlock]:
        """根据功能类型找到对应的目标块
        
        Args:
            function_type: 功能类型
                - 'militancy': 人口斗争性修改 (需要省份块)
                - 'culture': 中国文化修改 (需要国家定义块)
                - 'infamy': 中国恶名度修改 (需要国家定义块)
                - 'population': 人口属性修改 (需要省份块和人口组块)
                - 'date': 游戏日期修改 (需要根级别日期块)
                - 'money': 人口金钱修改 (需要省份块和人口组块)
        
        Returns:
            List[BracketBlock]: 匹配的块列表
        """
        if not self.structure:
            print("❌ 花括号结构未初始化，无法进行块查找")
            return []
        
        print(f"🔍 正在查找功能 '{function_type}' 对应的目标块...")
        
        target_blocks = []
        
        # 递归遍历所有块
        def traverse_blocks(block: BracketBlock):
            """递归遍历块结构"""
            # 检查当前块
            yield block
            # 递归检查子块
            if hasattr(block, 'children') and block.children:
                for child in block.children:
                    yield from traverse_blocks(child)
        
        all_blocks = list(traverse_blocks(self.structure))
        print(f"  📊 遍历找到 {len(all_blocks)} 个总块")
        
        if function_type == 'militancy':
            # 人口斗争性修改需要省份块
            print("  📍 查找目标: 省份块 (包含人口组)")
            for block in all_blocks:
                block_type = self._classify_block_type(block)
                if block_type == "省份" and block.level <= 2:
                    target_blocks.append(block)
            print(f"  ✅ 找到 {len(target_blocks)} 个省份块")
                    
        elif function_type == 'culture':
            # 中国文化修改需要CHI国家定义块
            print("  📍 查找目标: CHI国家定义块")
            for block in all_blocks:
                block_type = self._classify_block_type(block)
                if (block_type == "国家定义" and block.name == "CHI"):
                    # 进一步验证这是真正的国家定义块
                    country_indicators = [
                        'primary_culture', 'capital', 'technology', 'ruling_party',
                        'government', 'plurality', 'badboy', 'tag=CHI'
                    ]
                    indicator_count = sum(1 for indicator in country_indicators 
                                        if indicator in block.content)
                    if indicator_count >= 3:  # 至少包含3个国家指标
                        target_blocks.append(block)
            print(f"  ✅ 找到 {len(target_blocks)} 个CHI国家定义块")
                    
        elif function_type == 'infamy':
            # 中国恶名度修改需要CHI国家定义块
            print("  📍 查找目标: CHI国家定义块")
            for block in all_blocks:
                block_type = self._classify_block_type(block)
                if (block_type == "国家定义" and block.name == "CHI"):
                    # 进一步验证这是真正的国家定义块
                    country_indicators = [
                        'primary_culture', 'capital', 'technology', 'ruling_party',
                        'government', 'plurality', 'badboy', 'tag=CHI'
                    ]
                    indicator_count = sum(1 for indicator in country_indicators 
                                        if indicator in block.content)
                    if indicator_count >= 3:  # 至少包含3个国家指标
                        target_blocks.append(block)
            print(f"  ✅ 找到 {len(target_blocks)} 个CHI国家定义块")
                    
        elif function_type == 'population':
            # 人口属性修改需要包含中国人口的省份块
            print("  📍 查找目标: 包含中国人口的省份块")
            chinese_province_count = 0
            for block in all_blocks:
                block_type = self._classify_block_type(block)
                if block_type == "省份" and block.level <= 2:
                    # 检查是否包含中国文化人口
                    if any(culture in block.content.lower() for culture in ['beifaren', 'nanfaren', 'manchu', 'yankee']):
                        target_blocks.append(block)
                        chinese_province_count += 1
            print(f"  ✅ 找到 {len(target_blocks)} 个省份块 (包含中国人口: {chinese_province_count})")
                    
        elif function_type == 'date':
            # 游戏日期修改需要根级别的日期块
            print("  📍 查找目标: 根级别日期块")
            for block in all_blocks:
                if block.level == 0 and 'date=' in block.content.lower():
                    target_blocks.append(block)
            print(f"  ✅ 找到 {len(target_blocks)} 个根级别日期块")
                    
        elif function_type == 'money':
            # 人口金钱修改需要包含中国人口的省份块
            print("  📍 查找目标: 包含中国人口的省份块")
            chinese_province_count = 0
            for block in all_blocks:
                block_type = self._classify_block_type(block)
                if block_type == "省份" and block.level <= 2:
                    # 检查是否包含中国文化人口
                    if any(culture in block.content.lower() for culture in ['beifaren', 'nanfaren', 'manchu', 'yankee']):
                        target_blocks.append(block)
                        chinese_province_count += 1
            print(f"  ✅ 找到 {len(target_blocks)} 个省份块 (包含中国人口: {chinese_province_count})")
        
        else:
            print(f"  ❌ 未知的功能类型: {function_type}")
            return []
        
        # 验证块的类型一致性
        if target_blocks:
            block_types = set()
            level_distribution = {}
            
            for block in target_blocks:
                block_type = self._classify_block_type(block)
                block_types.add(block_type)
                level = block.level
                level_distribution[level] = level_distribution.get(level, 0) + 1
            
            print(f"  📊 块类型验证:")
            print(f"     类型种类: {len(block_types)} ({', '.join(block_types)})")
            print(f"     层级分布: {dict(sorted(level_distribution.items()))}")
            
            if len(block_types) == 1:
                print(f"  ✅ 类型一致性验证通过")
            else:
                print(f"  ⚠️ 发现多种块类型，请检查查找逻辑")
        
        return target_blocks
    
    def analyze_bracket_types(self) -> Dict[str, int]:
        """分析存档文件中的花括号类型和数量"""
        if not self.structure:
            print("❌ 花括号结构未初始化，无法进行分析")
            return {}
        
        print("\n" + "="*70)
        print("🔍 Victoria II 存档花括号类型分析")
        print("="*70)
        
        # 统计各种类型的块
        type_stats = {}
        level_stats = {}
        
        def analyze_block(block: BracketBlock, depth: int = 0):
            """递归分析块"""
            # 统计块类型
            block_type = self._classify_block_type(block)
            type_stats[block_type] = type_stats.get(block_type, 0) + 1
            
            # 统计层级深度
            level_stats[depth] = level_stats.get(depth, 0) + 1
            
            # 递归处理子块
            for child in block.children:
                analyze_block(child, depth + 1)
        
        # 分析所有顶级块
        for block in self.structure.children:
            analyze_block(block)
        
        # 显示分析结果
        self._display_bracket_analysis(type_stats, level_stats)
        
        return type_stats
    
    def _classify_block_type(self, block: BracketBlock) -> str:
        """分类花括号块的类型"""
        name = block.name.strip()
        content = block.content.strip()
        
        # 国家定义块 (如 CHI, ENG, FRA等)
        if re.match(r'^[A-Z]{3}$', name):
            return "国家定义"
        
        # 省份块 (纯数字)
        if re.match(r'^\d+$', name):
            return "省份"
        
        # 人口类型块
        population_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                           'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                           'bureaucrats', 'intellectuals']
        if name in population_types:
            return "人口组"
        
        # 意识形态块
        if name == "ideology":
            return "意识形态"
        
        # 文化块
        if name == "culture":
            return "文化"
        
        # 政党块
        if name == "party":
            return "政党"
        
        # 军队/舰队块
        if name in ["army", "navy", "unit"]:
            return "军事单位"
        
        # 贸易/经济块
        if name in ["trade", "market", "factory", "rgo"]:
            return "经济"
        
        # 外交块
        if name in ["diplomacy", "relation", "alliance", "war"]:
            return "外交"
        
        # 技术块
        if name in ["technology", "invention"]:
            return "科技"
        
        # 事件/决议块
        if name in ["event", "decision", "modifier"]:
            return "事件决议"
        
        # 日期块
        if re.match(r'^\d{4}\.\d{1,2}\.\d{1,2}$', name):
            return "日期"
        
        # 数值数组块
        if re.match(r'^\d+$', name) and len(content) < 100:
            return "数值数据"
        
        # 字符串/标识符块
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            return "标识符块"
        
        # 其他类型
        return "其他"
    
    def _display_bracket_analysis(self, type_stats: Dict[str, int], level_stats: Dict[int, int]):
        """显示花括号分析结果"""
        
        # 显示类型统计
        print("\n📊 花括号块类型统计:")
        print("-" * 50)
        total_blocks = sum(type_stats.values())
        
        # 按数量排序
        sorted_types = sorted(type_stats.items(), key=lambda x: x[1], reverse=True)
        
        for block_type, count in sorted_types:
            percentage = (count / total_blocks) * 100
            print(f"{block_type:12} | {count:6,} 个 | {percentage:5.1f}%")
        
        print("-" * 50)
        print(f"{'总计':12} | {total_blocks:6,} 个 | 100.0%")
        
        # 显示层级统计
        print("\n🏗️ 花括号嵌套层级统计:")
        print("-" * 40)
        
        for level in sorted(level_stats.keys()):
            count = level_stats[level]
            percentage = (count / total_blocks) * 100
            indent = "  " * level
            print(f"层级 {level:2} | {indent}{count:6,} 个 | {percentage:5.1f}%")
        
        # 显示基本信息
        print(f"\n📈 基本信息:")
        print(f"最大嵌套深度: {max(level_stats.keys()) if level_stats else 0}")
        print(f"不同类型数量: {len(type_stats)}")
        print(f"花括号块总数: {total_blocks:,}")
        
        # 计算实际花括号数量
        print(f"\n🔢 花括号数量验证:")
        open_braces = self.content.count('{')
        close_braces = self.content.count('}')
        print(f"开括号 {{: {open_braces:,}")
        print(f"闭括号 }}: {close_braces:,}")
        print(f"平衡状态: {'✅ 平衡' if open_braces == close_braces else '❌ 不平衡 (差异: ' + str(open_braces - close_braces) + ')'}")

def get_save_files_list():
    """获取存档文件列表"""
    import os
    import glob
    
    # 使用当前目录
    save_path = "."
    try:
        # 保存当前工作目录
        original_cwd = os.getcwd()
        
        # 切换到存档目录（如果需要）
        if save_path != ".":
            os.chdir(save_path)
        
        save_files = glob.glob("*.v2")
        save_files.sort(key=os.path.getmtime, reverse=True)  # 按修改时间排序
        
        # 恢复原始工作目录
        if save_path != ".":
            os.chdir(original_cwd)
            
        return save_files
    except Exception as e:
        print(f"❌ 无法访问存档目录: {e}")
        return []

def show_modification_menu():
    """显示修改选项菜单"""
    print("\n" + "="*50)
    print("请选择要执行的修改操作:")
    print("="*50)
    print("1. 人口斗争性修改 (中国=0, 其他=10)")
    print("2. 中国文化修改 (主文化=beifaren, 接受=nanfaren+manchu+yankee)")
    print("3. 中国恶名度修改 (设为0)")
    print("4. 中国人口属性修改 (宗教=mahayana, 意识形态=温和派)")
    print("5. 游戏日期修改 (设为1836.1.1)")
    print("6. 人口金钱修改 (中国=9,999,999,999, 非中国=0)")
    print("7. 执行全部修改 (推荐)")
    print("8. 分析存档括号类型 (仅分析，不修改)")
    print("0. 退出程序")
    print("="*50)

def get_user_selection():
    """获取用户选择的修改项目"""
    options = {
        'militancy': False,
        'culture': False,
        'infamy': False,
        'population': False,
        'date': False,
        'money': False,
        'analyze_only': False  # 新增分析模式标识
    }
    
    while True:
        try:
            choice = input("请输入选项 (多选用逗号分隔，如: 1,3,4): ").strip()
            
            if choice == '0':
                return None
            elif choice == '7':
                # 全部修改
                return {
                    'militancy': True,
                    'culture': True,
                    'infamy': True,
                    'population': True,
                    'date': True,
                    'money': True,
                    'analyze_only': False
                }
            elif choice == '8':
                # 仅分析括号类型
                return {
                    'militancy': False,
                    'culture': False,
                    'infamy': False,
                    'population': False,
                    'date': False,
                    'money': False,
                    'analyze_only': True
                }
            else:
                # 解析选择
                choices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
                
                if not choices:
                    print("❌ 无效选择，请重新输入")
                    continue
                
                for num in choices:
                    if num == 1:
                        options['militancy'] = True
                    elif num == 2:
                        options['culture'] = True
                    elif num == 3:
                        options['infamy'] = True
                    elif num == 4:
                        options['population'] = True
                    elif num == 5:
                        options['date'] = True
                    elif num == 6:
                        options['money'] = True
                    elif num == 8:
                        options['analyze_only'] = True
                    else:
                        print(f"❌ 无效选项: {num}")
                        continue
                
                if any(options.values()):
                    return options
                else:
                    print("❌ 未选择任何有效选项，请重新输入")
                    
        except ValueError:
            print("❌ 输入格式错误，请输入数字")
        except KeyboardInterrupt:
            print("\n程序已取消")
            return None

def main():
    """主函数"""
    print("Victoria II 主修改器 v2.1")
    print("集成所有修改功能的统一入口工具")
    print("支持默认路径和选择性修改")
    print("="*50)
    
    # 获取文件名
    if len(sys.argv) > 1:
        # 过滤掉选项参数，只保留文件名
        filename = None
        for arg in sys.argv[1:]:
            if not arg.startswith('-'):
                filename = arg
                break
        
        if not filename:
            print("❌ 未提供文件名")
            return
            
        print(f"从命令行获取文件名: {filename}")
        
        # 检查是否为帮助命令
        if filename in ['--help', '-h', 'help']:
            print("\n使用方法:")
            print("python victoria2_main_modifier.py <存档文件名> [选项]")
            print("python victoria2_main_modifier.py  # 交互式模式")
            print("\n选项:")
            print("--debug, -d      启用调试模式，显示详细的修改过程")
            print("--analyze, -a    仅分析括号类型，不执行修改")
            print("\n功能说明:")
            print("1. 人口斗争性: 中国=0, 其他=10")
            print("2. 中国文化: 主文化=beifaren, 接受=nanfaren+manchu+yankee")
            print("3. 中国恶名度: 设为0")
            print("4. 中国人口属性: 宗教=mahayana, 意识形态=温和派")
            print("5. 游戏日期: 设为1836.1.1")
            print("6. 人口金钱修改: 中国=9,999,999,999, 非中国=0")
            print("7. 支持选择性修改和全部修改")
            print("8. 分析存档括号类型")
            print("\n意识形态映射 (已确认 Liberal=ID 6):")
            print("• Reactionary(1) + Socialist(4) + Communist(7) → Conservative(3)")
            print("• Fascist(2) + Anarcho-Liberal(5) → Liberal(6)")
            print("\n示例:")
            print("python victoria2_main_modifier.py mysave.v2 --debug")
            print("python victoria2_main_modifier.py mysave.v2 --analyze")
            return
        
        # 检查文件是否存在
        import os
        if not os.path.isfile(filename):
            print(f"❌ 文件不存在: {filename}")
            return
        
        # 检查是否为分析模式
        if '--analyze' in sys.argv or '-a' in sys.argv:
            # 命令行分析模式
            print("\n📊 分析模式：将分析存档文件的括号结构...")
            
            # 创建修改器并执行分析
            modifier = Victoria2Modifier(debug_mode=False)
            try:
                # 解析文件
                modifier.load_file(filename)
                
                # 执行括号分析
                modifier.analyze_bracket_types()
                
                print("\n✅ 分析完成")
            except Exception as e:
                print(f"❌ 分析过程中出现错误: {e}")
            return
            
        # 命令行模式：执行全部修改
        options = {
            'militancy': True,
            'culture': True,
            'infamy': True,
            'population': True,
            'date': True,
            'money': True,
            'analyze_only': False
        }
    else:
        # 交互式模式
        print("\n🎮 交互式模式")
        
        # 显示可用的存档文件
        save_files = get_save_files_list()
        if save_files:
            print(f"\n📁 在默认存档目录找到 {len(save_files)} 个存档文件:")
            for i, file in enumerate(save_files[:10], 1):  # 显示最近的10个文件
                print(f"{i:2d}. {file}")
            if len(save_files) > 10:
                print(f"    ... 还有 {len(save_files) - 10} 个文件")
        
        # 获取文件名
        while True:
            user_input = input("\n请输入存档文件名 (或文件编号): ").strip()
            if not user_input:
                print("❌ 未提供文件名，退出程序")
                return
            
            # 检查是否为数字编号
            if user_input.isdigit() and save_files:
                file_num = int(user_input)
                if 1 <= file_num <= len(save_files):
                    filename = save_files[file_num - 1]
                    print(f"选择文件: {filename}")
                    break
                else:
                    print(f"❌ 编号超出范围，请输入 1-{len(save_files)}")
                    continue
            else:
                filename = user_input
                if not filename.endswith('.v2'):
                    filename += '.v2'
                
                # 检查文件是否存在
                import os
                if os.path.isfile(filename):
                    break
                else:
                    print(f"❌ 文件不存在: {filename}")
                    continue
        
        # 显示修改选项菜单
        show_modification_menu()
        options = get_user_selection()
        
        if options is None:
            print("操作已取消")
            return
    
    # 处理分析模式
    if options.get('analyze_only', False):
        print("\n📊 将分析存档文件的括号结构...")
        
        # 创建修改器并执行分析
        modifier = Victoria2Modifier(debug_mode=False)
        try:
            # 解析文件
            modifier.load_file(filename)
            
            # 执行括号分析
            modifier.analyze_bracket_types()
            
            print("\n✅ 分析完成")
        except Exception as e:
            print(f"❌ 分析过程中出现错误: {e}")
        return
    
    # 确认执行
    print(f"\n即将修改文件: {filename}")
    print("选择的修改内容:")
    
    modification_list = []
    if options.get('population', False):
        modification_list.extend([
            "1. 所有中国人口宗教 → mahayana",
            "2. 意识形态调整 (✅ Liberal=ID 6 已确认):",
            "   • Reactionary(1) + Socialist(4) + Communist(7) → Conservative(3)",
            "   • Fascist(2) + Anarcho-Liberal(5) → Liberal(6)"
        ])
    if options.get('militancy', False):
        modification_list.append("3. 人口斗争性: 中国=0, 其他=10")
    if options.get('culture', False):
        modification_list.append("4. 中国文化: 主文化=beifaren, 接受=nanfaren+manchu+yankee")
    if options.get('infamy', False):
        modification_list.append("5. 中国恶名度: 设为0")
    if options.get('date', False):
        modification_list.append("6. 游戏日期: 设为1836.1.1")
    if options.get('money', False):
        modification_list.append("7. 人口金钱: 中国=9,999,999,999, 非中国=0")
    
    for item in modification_list:
        print(item)
    
    # 命令行模式自动确认，交互式模式需要确认
    if len(sys.argv) > 1:
        confirm = "yes"  # 命令行模式自动确认
    else:
        confirm = input("\n确认执行修改吗？(直接回车确认，输入 'no' 取消): ").strip()
        if confirm == "":
            confirm = "yes"  # 回车默认为yes
    
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    # 检查是否启用调试模式
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    if debug_mode:
        print("🐛 调试模式已启用 - 将显示详细的修改过程")
    
    # 创建修改器并执行
    modifier = Victoria2Modifier(debug_mode=debug_mode)
    
    # 根据选择执行相应的修改
    modification_options = {k: v for k, v in options.items() if k != 'analyze_only'}
    if all(modification_options.values()):
        # 全部修改
        modifier.execute_all_modifications(filename)
    else:
        # 选择性修改
        modifier.execute_selective_modifications(filename, options)

if __name__ == "__main__":
    main()
