#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Victoria II 政党信息查看和修改工具（改进版）
"""

import re
import shutil
from pathlib import Path
from datetime import datetime


class ImprovedPoliticalModifier:
    def __init__(self, save_file_path: str):
        self.save_file_path = Path(save_file_path)
        self.backup_path = None
        self.content = ""
        
    def create_backup(self) -> str:
        """创建存档文件备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.save_file_path.stem}_backup_pol_{timestamp}{self.save_file_path.suffix}"
        self.backup_path = self.save_file_path.parent / backup_name
        
        shutil.copy2(self.save_file_path, self.backup_path)
        print(f"备份文件已创建: {self.backup_path}")
        return str(self.backup_path)
    
    def load_file(self):
        """加载存档文件"""
        with open(self.save_file_path, 'r', encoding='latin-1') as f:
            self.content = f.read()
        print(f"成功加载文件: {self.save_file_path}")
    
    def search_and_analyze_parties(self):
        """搜索并分析政党信息"""
        print("=== 搜索政党相关信息 ===\n")
        
        # 1. 查找中国的执政党ID
        chi_ruling_party = re.search(r'CHI=.*?ruling_party=(\d+)', self.content, re.DOTALL)
        if chi_ruling_party:
            party_id = chi_ruling_party.group(1)
            print(f"中国执政党ID: {party_id}")
        else:
            print("未找到中国执政党ID")
            return
        
        # 2. 在文件中搜索可能的政党定义模式
        print(f"\n=== 搜索政党ID {party_id} 的定义 ===")
        
        # 尝试不同的政党定义模式
        patterns = [
            rf'party_\d+.*?{party_id}.*?\{{[^}}]*\}}',  # party_xxx块
            rf'{party_id}=\s*\{{[^}}]*name[^}}]*\}}',   # 直接ID定义
            rf'id={party_id}[^}}]*name="([^"]*)"',      # 包含name的定义
        ]
        
        for i, pattern in enumerate(patterns):
            print(f"\n模式 {i+1}: {pattern}")
            matches = list(re.finditer(pattern, self.content, re.DOTALL | re.IGNORECASE))
            if matches:
                print(f"找到 {len(matches)} 个匹配:")
                for j, match in enumerate(matches[:3]):
                    print(f"  匹配 {j+1}: {match.group(0)[:200]}...")
            else:
                print("无匹配")
        
        # 3. 搜索文件末尾的数据库部分
        print(f"\n=== 搜索文件末尾的政党数据库 ===")
        
        # 获取文件末尾部分进行搜索
        end_content = self.content[-50000:]  # 最后50KB
        database_patterns = [
            r'parties=\s*\{.*?\}',
            r'political_parties=\s*\{.*?\}',
            r'party_database=\s*\{.*?\}',
            rf'.*{party_id}.*name="([^"]*)".*',
        ]
        
        for i, pattern in enumerate(database_patterns):
            print(f"\n数据库模式 {i+1}: {pattern}")
            matches = list(re.finditer(pattern, end_content, re.DOTALL | re.IGNORECASE))
            if matches:
                print(f"在文件末尾找到 {len(matches)} 个匹配:")
                for j, match in enumerate(matches[:2]):
                    print(f"  匹配 {j+1}: {match.group(0)[:300]}...")
            else:
                print("无匹配")
        
        # 4. 搜索religious_policy相关的设置
        print(f"\n=== 搜索宗教政策设置 ===")
        religious_patterns = [
            r'religious_policy="[^"]*"',
            r'secularized',
            r'atheism',
            r'pro_atheism',
            r'moralism',
            r'pluralism',
        ]
        
        for pattern in religious_patterns:
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE))
            if matches:
                print(f"{pattern}: 找到 {len(matches)} 个匹配")
                # 显示前几个匹配的上下文
                for i, match in enumerate(matches[:3]):
                    start = max(0, match.start() - 50)
                    end = min(len(self.content), match.end() + 50)
                    context = self.content[start:end].replace('\n', ' ').replace('\r', '')
                    print(f"  匹配 {i+1}: ...{context}...")
            else:
                print(f"{pattern}: 无匹配")
    
    def create_minimal_modification(self):
        """创建最小化的修改"""
        print(f"\n=== 执行最小化修改 ===")
        
        # 由于无法找到政党的详细定义，我们执行一个简化的修改
        # 只修改主文化（这个已经成功了）
        
        # 检查主文化是否已经修改
        if 'primary_culture="nanfaren"' in self.content:
            print("✓ 主文化已经成功修改为 nanfaren（南方人）")
        else:
            print("✗ 主文化修改失败")
        
        # 对于宗教政策，由于没有找到具体的政党定义
        # 我们可以尝试在中国数据段中添加一个宗教政策设置
        chi_match = re.search(r'(CHI=\s*\{[^}]*)(religion="[^"]*")([^}]*\})', self.content, re.DOTALL)
        if chi_match:
            before_religion = chi_match.group(1)
            religion_line = chi_match.group(2)
            after_religion = chi_match.group(3)
            
            # 在religion行之后添加宗教政策设置
            new_section = before_religion + religion_line + '\n\treligious_policy="secularized"' + after_religion
            self.content = self.content.replace(chi_match.group(0), new_section)
            print("✓ 已在中国数据中添加宗教政策设置: secularized（无神论）")
        else:
            print("✗ 无法找到中国数据段来添加宗教政策")
    
    def save_file(self):
        """保存修改后的文件"""
        with open(self.save_file_path, 'w', encoding='latin-1') as f:
            f.write(self.content)
        print(f"文件已保存: {self.save_file_path}")
    
    def run_analysis_and_modification(self):
        """运行分析和修改"""
        self.create_backup()
        self.load_file()
        self.search_and_analyze_parties()
        self.create_minimal_modification()
        self.save_file()


def main():
    save_file = "China1836_04_29.v2"
    
    try:
        modifier = ImprovedPoliticalModifier(save_file)
        modifier.run_analysis_and_modification()
        
    except Exception as e:
        print(f"修改过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
