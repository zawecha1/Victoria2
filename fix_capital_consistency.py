#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首都一致性修复工具
修复重分配后的首都问题
"""

import re
import os
import json
from datetime import datetime
from typing import Dict, List

class CapitalConsistencyFixer:
    """首都一致性修复器"""
    
    def __init__(self, filename: str):
        self.filename = filename
        if not os.path.exists(filename):
            raise FileNotFoundError(f"文件不存在: {filename}")
        
        with open(filename, 'r', encoding='latin1') as f:
            self.content = f.read()
            
        self.original_content = self.content
    
    def identify_capital_problems(self) -> Dict:
        """识别首都问题"""
        print("🔍 识别首都一致性问题...")
        
        # 获取所有省份归属
        provinces_data = {}
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+20000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 10000
            
            province_content = self.content[start_pos:end_pos]
            
            # 提取拥有者
            owner_match = re.search(r'owner="?([A-Z]{2,3})"?', province_content)
            if owner_match:
                provinces_data[province_id] = {
                    'owner': owner_match.group(1),
                    'name': self._extract_province_name(province_content)
                }
        
        # 检查所有国家的首都
        country_pattern = re.compile(r'^([A-Z]{2,3})=\s*{', re.MULTILINE)
        country_matches = list(country_pattern.finditer(self.content))
        
        problems = []
        country_to_provinces = {}
        
        for i, match in enumerate(country_matches):
            country_tag = match.group(1)
            start_pos = match.end()
            
            if i + 1 < len(country_matches):
                end_pos = country_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+50000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = len(self.content)
            
            country_content = self.content[start_pos:end_pos]
            
            # 查找首都
            capital_match = re.search(r'capital=(\d+)', country_content)
            if capital_match:
                capital_id = int(capital_match.group(1))
                
                # 找到该国拥有的所有省份
                owned_provinces = [pid for pid, data in provinces_data.items() 
                                 if data['owner'] == country_tag]
                country_to_provinces[country_tag] = owned_provinces
                
                # 检查首都是否在拥有的省份中
                if capital_id not in owned_provinces:
                    current_owner = provinces_data.get(capital_id, {}).get('owner', 'UNKNOWN')
                    problems.append({
                        'country': country_tag,
                        'capital_id': capital_id,
                        'capital_name': provinces_data.get(capital_id, {}).get('name', 'Unknown'),
                        'current_owner': current_owner,
                        'owned_provinces': owned_provinces,
                        'country_start': match.start(),
                        'country_end': end_pos
                    })
        
        print(f"🚨 发现 {len(problems)} 个首都一致性问题")
        return {
            'problems': problems,
            'provinces_data': provinces_data,
            'country_to_provinces': country_to_provinces
        }
    
    def _extract_province_name(self, province_content: str) -> str:
        """提取省份名称"""
        name_match = re.search(r'name="([^"]+)"', province_content)
        return name_match.group(1) if name_match else 'Unknown'
    
    def fix_capitals(self, analysis_result: Dict) -> Dict:
        """修复首都问题"""
        print("🔧 修复首都一致性问题...")
        
        problems = analysis_result['problems']
        country_to_provinces = analysis_result['country_to_provinces']
        provinces_data = analysis_result['provinces_data']
        
        fixes_made = []
        modified_content = self.content
        
        # 按position从后往前处理，避免位置偏移
        problems.sort(key=lambda x: x['country_start'], reverse=True)
        
        for problem in problems:
            country_tag = problem['country']
            old_capital = problem['capital_id']
            owned_provinces = problem['owned_provinces']
            
            if not owned_provinces:
                print(f"⚠️ {country_tag}: 无省份，无法修复首都")
                fixes_made.append({
                    'country': country_tag,
                    'status': 'failed',
                    'reason': 'no_provinces',
                    'old_capital': old_capital
                })
                continue
            
            # 选择新首都（第一个拥有的省份）
            new_capital = owned_provinces[0]
            new_capital_name = provinces_data.get(new_capital, {}).get('name', 'Unknown')
            
            # 在国家块中查找并替换首都
            country_start = problem['country_start']
            country_end = problem['country_end']
            country_content = modified_content[country_start:country_end]
            
            # 替换首都ID
            old_capital_pattern = f'capital={old_capital}'
            new_capital_pattern = f'capital={new_capital}'
            
            if old_capital_pattern in country_content:
                country_content = country_content.replace(old_capital_pattern, new_capital_pattern)
                modified_content = modified_content[:country_start] + country_content + modified_content[country_end:]
                
                print(f"✅ {country_tag}: {old_capital} -> {new_capital} ({new_capital_name})")
                fixes_made.append({
                    'country': country_tag,
                    'status': 'success',
                    'old_capital': old_capital,
                    'new_capital': new_capital,
                    'new_capital_name': new_capital_name
                })
            else:
                print(f"❌ {country_tag}: 未找到首都声明")
                fixes_made.append({
                    'country': country_tag,
                    'status': 'failed',
                    'reason': 'capital_declaration_not_found',
                    'old_capital': old_capital
                })
        
        self.content = modified_content
        
        return {
            'fixes_made': fixes_made,
            'total_problems': len(problems),
            'successful_fixes': len([f for f in fixes_made if f['status'] == 'success']),
            'failed_fixes': len([f for f in fixes_made if f['status'] == 'failed'])
        }
    
    def validate_fixes(self) -> Dict:
        """验证修复结果"""
        print("🔍 验证修复结果...")
        
        # 重新检查是否还有问题
        new_analysis = self.identify_capital_problems()
        remaining_problems = len(new_analysis['problems'])
        
        if remaining_problems == 0:
            print("✅ 所有首都问题已修复")
            return {'success': True, 'remaining_problems': 0}
        else:
            print(f"⚠️ 仍有 {remaining_problems} 个首都问题")
            return {'success': False, 'remaining_problems': remaining_problems, 'problems': new_analysis['problems']}
    
    def check_bracket_balance(self) -> bool:
        """检查花括号平衡"""
        open_count = self.content.count('{')
        close_count = self.content.count('}')
        difference = open_count - close_count
        
        print(f"🔍 花括号检查: 开={open_count}, 闭={close_count}, 差异={difference}")
        
        # Victoria II 通常期望 -1 的差异
        return difference == -1
    
    def save_fixes(self, backup_suffix: str = None) -> bool:
        """保存修复后的文件"""
        if backup_suffix is None:
            backup_suffix = f"before_capital_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建备份
        backup_filename = f"{self.filename}.{backup_suffix}.backup"
        try:
            with open(backup_filename, 'w', encoding='latin1') as f:
                f.write(self.original_content)
            print(f"💾 备份创建: {backup_filename}")
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return False
        
        # 保存修复后的文件
        try:
            with open(self.filename, 'w', encoding='latin1') as f:
                f.write(self.content)
            print(f"💾 修复文件已保存: {self.filename}")
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False

def fix_capital_consistency(filename: str = 'autosave.v2') -> bool:
    """修复首都一致性问题的主函数"""
    print("🔧 Victoria II 首都一致性修复工具")
    print("=" * 50)
    
    if not os.path.exists(filename):
        print(f"❌ 文件不存在: {filename}")
        return False
    
    try:
        # 创建修复器
        fixer = CapitalConsistencyFixer(filename)
        
        # 1. 识别问题
        print("\\n1️⃣ 识别首都问题...")
        analysis = fixer.identify_capital_problems()
        
        if not analysis['problems']:
            print("✅ 未发现首都一致性问题")
            return True
        
        # 显示问题详情
        print(f"\\n📋 首都问题详情:")
        for i, problem in enumerate(analysis['problems'][:10], 1):
            print(f"   {i:2d}. {problem['country']}: 首都 {problem['capital_id']} ({problem['capital_name']}) 现属于 {problem['current_owner']}")
        
        if len(analysis['problems']) > 10:
            print(f"   ... 还有 {len(analysis['problems']) - 10} 个问题")
        
        # 2. 执行修复
        print("\\n2️⃣ 执行修复...")
        fix_result = fixer.fix_capitals(analysis)
        
        print(f"\\n📊 修复结果:")
        print(f"   总问题: {fix_result['total_problems']}")
        print(f"   成功修复: {fix_result['successful_fixes']}")
        print(f"   修复失败: {fix_result['failed_fixes']}")
        
        # 3. 验证修复
        print("\\n3️⃣ 验证修复结果...")
        validation = fixer.validate_fixes()
        
        # 4. 检查文件完整性
        print("\\n4️⃣ 检查文件完整性...")
        if not fixer.check_bracket_balance():
            print("❌ 花括号平衡检查失败")
            return False
        
        # 5. 保存文件
        if validation['success']:
            print("\\n5️⃣ 保存修复后的文件...")
            if fixer.save_fixes():
                print("🎉 首都一致性修复完成！")
                return True
            else:
                print("❌ 保存文件失败")
                return False
        else:
            print("❌ 验证失败，未保存文件")
            return False
        
    except Exception as e:
        print(f"❌ 修复过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🏛️ 开始修复首都一致性问题...")
    
    success = fix_capital_consistency('autosave.v2')
    
    if success:
        print("\\n🎮 修复完成！现在可以尝试在游戏中加载 autosave.v2")
    else:
        print("\\n❌ 修复失败，建议使用备份文件 China1837_07_15.v2")

if __name__ == "__main__":
    main()
