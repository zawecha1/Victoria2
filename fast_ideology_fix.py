#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高效的全局意识形态修改器 - 直接使用正则表达式
"""

import re
import shutil
from datetime import datetime

class FastIdeologyFixer:
    """快速意识形态修复器"""
    
    def __init__(self):
        self.ideology_changes = 0
        # 意识形态转换映射
        self.ideology_mapping = {
            1: 3,  # Reactionary -> Conservative
            2: 6,  # Fascist -> Liberal
            4: 3,  # Socialist -> Conservative
            5: 6,  # Anarcho-Liberal -> Liberal
            7: 3   # Communist -> Conservative
        }
    
    def create_backup(self, filename: str) -> str:
        """创建备份文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename.replace('.v2', '')}_fast_ideology_backup_{timestamp}.v2"
        print(f"创建备份文件: {backup_filename}")
        shutil.copy2(filename, backup_filename)
        return backup_filename
    
    def fix_all_ideologies(self, filename: str) -> bool:
        """修复文件中的所有意识形态"""
        print(f"🚀 开始快速修复文件: {filename}")
        
        # 读取文件
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
            print(f"✅ 文件读取成功，大小: {len(content):,} 字符")
        except Exception as e:
            print(f"❌ 文件读取失败: {e}")
            return False
        
        # 创建备份
        backup_file = self.create_backup(filename)
        
        # 查找所有意识形态块
        ideology_pattern = r'ideology=\s*\{([^}]*)\}'
        
        print("🔍 查找和修改意识形态块...")
        
        def replace_ideology(match):
            ideology_content = match.group(1)
            
            # 解析意识形态数据
            ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
            ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
            
            # 检查是否有需要转换的旧意识形态
            has_old_ideologies = any(ideology_dist.get(old_id, 0) > 0 for old_id in [1, 2, 4, 5, 7])
            
            if has_old_ideologies:
                # 执行转换
                new_ideology_content = self._modify_ideology_distribution(ideology_content)
                self.ideology_changes += 1
                
                # 构建新的ideology块
                return f'ideology=\n\t\t{{\n\t\t\t{new_ideology_content}\n\t\t}}'
            else:
                # 不需要转换，返回原内容
                return match.group(0)
        
        # 执行全局替换
        modified_content = re.sub(ideology_pattern, replace_ideology, content, flags=re.DOTALL)
        
        print(f"📊 修改统计: {self.ideology_changes} 个意识形态块已转换")
        
        # 保存修改后的文件
        output_filename = filename.replace('.v2', '_ideology_fixed_fast.v2')
        try:
            with open(output_filename, 'w', encoding='utf-8-sig') as f:
                f.write(modified_content)
            print(f"✅ 修复文件保存: {output_filename}")
            return True
        except Exception as e:
            print(f"❌ 文件保存失败: {e}")
            return False
    
    def _modify_ideology_distribution(self, ideology_content: str) -> str:
        """修改意识形态分布"""
        # 解析现有的意识形态分布
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
        ideology_dist = {}
        
        # 解析所有现有的意识形态数据
        for id_str, value_str in ideology_pairs:
            ideology_dist[int(id_str)] = float(value_str)
        
        # 检查是否有需要转换的旧意识形态
        has_old_ideologies = any(ideology_dist.get(old_id, 0) > 0 for old_id in [1, 2, 4, 5, 7])
        if not has_old_ideologies:
            return ideology_content
        
        # 计算要转换的百分比
        transferred_to_liberal = 0.0      # 转移到Liberal(6)
        transferred_to_conservative = 0.0  # 转移到Conservative(3)
        
        # 根据意识形态映射规则计算转移
        for old_id, new_id in self.ideology_mapping.items():
            if old_id in ideology_dist and ideology_dist[old_id] > 0:
                value = ideology_dist[old_id]
                
                if new_id == 6:  # Liberal = ID 6
                    transferred_to_liberal += value
                elif new_id == 3:  # Conservative = ID 3
                    transferred_to_conservative += value
                
                # 将原意识形态设为0
                ideology_dist[old_id] = 0.0
        
        # 确保目标意识形态存在
        if 6 not in ideology_dist:
            ideology_dist[6] = 0.0  # Liberal
        if 3 not in ideology_dist:
            ideology_dist[3] = 0.0  # Conservative
        
        # 增加目标意识形态的百分比
        if transferred_to_liberal > 0:
            ideology_dist[6] += transferred_to_liberal
        
        if transferred_to_conservative > 0:
            ideology_dist[3] += transferred_to_conservative
        
        # 验证并归一化百分比总和
        new_total = sum(ideology_dist.values())
        if new_total > 0 and abs(new_total - 100.0) > 0.00001:
            normalization_factor = 100.0 / new_total
            for ideology_id in ideology_dist:
                if ideology_dist[ideology_id] > 0:
                    ideology_dist[ideology_id] *= normalization_factor
        
        # 重新构建意识形态内容
        new_lines = []
        for ideology_id in sorted(ideology_dist.keys()):
            value = ideology_dist[ideology_id]
            new_lines.append(f'{ideology_id}={value:.5f}')
        
        # 构建正确的格式
        formatted_content = '\n\t\t\t'.join(new_lines)
        
        return formatted_content

def main():
    """主函数"""
    fixer = FastIdeologyFixer()
    
    # 修复autosave.v2文件
    success = fixer.fix_all_ideologies('autosave.v2')
    
    if success:
        print("\n🎉 快速修复完成!")
        print("建议使用检查程序验证修复效果")
    else:
        print("\n❌ 修复失败")

if __name__ == "__main__":
    main()
