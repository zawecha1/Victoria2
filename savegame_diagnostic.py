#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存档文件诊断工具 (savegame_diagnostic.py)
======================================
诊断Victoria II存档文件问题，对比正常文件和问题文件

功能:
1. 检查文件编码和大小
2. 验证花括号平衡
3. 检查文件结构完整性
4. 对比两个存档的差异
5. 识别可能导致游戏崩溃的问题
"""

import os
import re

class SavegameDiagnostic:
    """存档诊断器"""
    
    def __init__(self):
        self.encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252']
    
    def read_file_safely(self, filename):
        """安全读取文件并确定编码"""
        if not os.path.exists(filename):
            print(f"❌ 文件不存在: {filename}")
            return None, None
        
        for encoding in self.encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    content = f.read()
                return content, encoding
            except UnicodeDecodeError:
                continue
        
        print(f"❌ 无法读取文件: {filename}")
        return None, None
    
    def check_basic_info(self, filename):
        """检查文件基本信息"""
        print(f"📁 文件: {filename}")
        
        if not os.path.exists(filename):
            print(f"❌ 文件不存在")
            return None
        
        # 文件大小
        file_size = os.path.getsize(filename)
        print(f"📦 文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
        
        # 读取内容
        content, encoding = self.read_file_safely(filename)
        if content is None:
            return None
        
        print(f"🔤 编码: {encoding}")
        print(f"📄 字符数: {len(content):,}")
        
        return content
    
    def check_bracket_balance(self, content, filename):
        """检查花括号平衡"""
        print(f"🔍 花括号检查 - {filename}:")
        
        open_count = content.count('{')
        close_count = content.count('}')
        difference = open_count - close_count
        
        print(f"   开括号 {{: {open_count:,}")
        print(f"   闭括号 }}: {close_count:,}")
        print(f"   差异: {difference}")
        
        if difference == -1:
            print(f"   ✅ 正常 (Victoria II通常是-1)")
        elif difference == 0:
            print(f"   ✅ 平衡")
        else:
            print(f"   ❌ 不平衡！可能导致游戏崩溃")
        
        return difference
    
    def check_file_structure(self, content, filename):
        """检查文件结构完整性"""
        print(f"🏗️ 结构检查 - {filename}:")
        
        issues = []
        
        # 检查基本块结构
        if not re.search(r'date=', content):
            issues.append("缺少date字段")
        
        if not re.search(r'player="[A-Z]{2,3}"', content):
            issues.append("缺少player字段")
        
        # 检查是否有国家块
        country_blocks = re.findall(r'^[A-Z]{2,3}=\s*{', content, re.MULTILINE)
        print(f"   国家块数量: {len(country_blocks)}")
        
        # 检查是否有省份块
        province_blocks = re.findall(r'^\d+=\s*{', content, re.MULTILINE)
        print(f"   省份块数量: {len(province_blocks)}")
        
        # 检查文件完整性
        if content.strip()[-1] != '}':
            issues.append("文件末尾不是闭括号")
        
        # 检查是否有损坏的字符
        if '\x00' in content:
            issues.append("包含空字符(可能文件损坏)")
        
        # 检查行结束符
        if '\r\n' in content and '\n' in content.replace('\r\n', ''):
            issues.append("混合的行结束符")
        
        if issues:
            print(f"   ❌ 发现问题:")
            for issue in issues:
                print(f"      • {issue}")
        else:
            print(f"   ✅ 结构正常")
        
        return issues
    
    def find_problematic_sections(self, content, filename):
        """查找可能有问题的部分"""
        print(f"🔍 问题部分检查 - {filename}:")
        
        problems = []
        
        # 检查不配对的引号
        quote_count = content.count('"')
        if quote_count % 2 != 0:
            problems.append(f"引号不配对 (总数: {quote_count})")
        
        # 检查异常的字符序列
        if re.search(r'}}+', content):
            matches = re.findall(r'}}+', content)
            problems.append(f"连续闭括号: {len(matches)} 处")
        
        if re.search(r'{{+', content):
            matches = re.findall(r'{{+', content)
            problems.append(f"连续开括号: {len(matches)} 处")
        
        # 检查空的块
        empty_blocks = re.findall(r'=\s*{\s*}', content)
        if empty_blocks:
            problems.append(f"空块: {len(empty_blocks)} 个")
        
        # 检查可能的编码问题
        if re.search(r'[^\x00-\x7F\u00A0-\uFFFF]', content):
            problems.append("包含异常字符")
        
        if problems:
            print(f"   ❌ 发现潜在问题:")
            for problem in problems:
                print(f"      • {problem}")
        else:
            print(f"   ✅ 未发现明显问题")
        
        return problems
    
    def compare_files(self, good_file, bad_file):
        """对比两个文件"""
        print(f"⚖️ 文件对比:")
        print(f"   正常文件: {good_file}")
        print(f"   问题文件: {bad_file}")
        
        good_content = self.read_file_safely(good_file)[0]
        bad_content = self.read_file_safely(bad_file)[0]
        
        if good_content is None or bad_content is None:
            print(f"   ❌ 无法读取文件进行对比")
            return
        
        # 大小对比
        good_size = len(good_content)
        bad_size = len(bad_content)
        size_diff = bad_size - good_size
        
        print(f"   大小对比:")
        print(f"      正常: {good_size:,} 字符")
        print(f"      问题: {bad_size:,} 字符")
        print(f"      差异: {size_diff:+,} 字符")
        
        # 花括号对比
        good_open = good_content.count('{')
        good_close = good_content.count('}')
        bad_open = bad_content.count('{')
        bad_close = bad_content.count('}')
        
        print(f"   花括号对比:")
        print(f"      正常: {{ {good_open:,}, }} {good_close:,}, 差异 {good_open-good_close}")
        print(f"      问题: {{ {bad_open:,}, }} {bad_close:,}, 差异 {bad_open-bad_close}")
        
        # 结构对比
        good_countries = len(re.findall(r'^[A-Z]{2,3}=\s*{', good_content, re.MULTILINE))
        bad_countries = len(re.findall(r'^[A-Z]{2,3}=\s*{', bad_content, re.MULTILINE))
        good_provinces = len(re.findall(r'^\d+=\s*{', good_content, re.MULTILINE))
        bad_provinces = len(re.findall(r'^\d+=\s*{', bad_content, re.MULTILINE))
        
        print(f"   结构对比:")
        print(f"      国家块: 正常 {good_countries}, 问题 {bad_countries}")
        print(f"      省份块: 正常 {good_provinces}, 问题 {bad_provinces}")
    
    def diagnose_file(self, filename):
        """诊断单个文件"""
        print(f"🔬 诊断文件: {filename}")
        print("=" * 50)
        
        # 基本信息
        content = self.check_basic_info(filename)
        if content is None:
            return False
        
        print()
        
        # 花括号检查
        bracket_diff = self.check_bracket_balance(content, filename)
        print()
        
        # 结构检查
        structure_issues = self.check_file_structure(content, filename)
        print()
        
        # 问题检查
        problems = self.find_problematic_sections(content, filename)
        print()
        
        # 总结
        if bracket_diff not in [-1, 0] or structure_issues or problems:
            print(f"❌ 文件可能有问题，建议修复")
            return False
        else:
            print(f"✅ 文件看起来正常")
            return True
    
    def full_diagnostic(self, good_file, bad_file):
        """完整诊断"""
        print("🏥 Victoria II 存档诊断报告")
        print("=" * 60)
        
        # 诊断正常文件
        print("\\n1️⃣ 诊断正常文件:")
        good_status = self.diagnose_file(good_file)
        
        print("\\n" + "=" * 60)
        
        # 诊断问题文件
        print("\\n2️⃣ 诊断问题文件:")
        bad_status = self.diagnose_file(bad_file)
        
        print("\\n" + "=" * 60)
        
        # 对比分析
        print("\\n3️⃣ 对比分析:")
        self.compare_files(good_file, bad_file)
        
        print("\\n" + "=" * 60)
        
        # 建议
        print("\\n💡 修复建议:")
        if not bad_status:
            print("   • 问题文件确实有异常")
            print("   • 建议使用正常文件替换问题文件")
            print("   • 或者尝试从备份恢复")
        
        if good_status and not bad_status:
            print("   • 可以安全地用正常文件替换问题文件")
            print("   • 命令: copy \"China1837_07_15.v2\" \"autosave.v2\"")

def main():
    """主函数"""
    diagnostic = SavegameDiagnostic()
    
    # 检查文件存在性
    good_file = "China1837_07_15.v2"  # 正常文件
    bad_file = "autosave.v2"          # 问题文件
    
    if not os.path.exists(good_file):
        print(f"❌ 正常文件不存在: {good_file}")
        return
    
    if not os.path.exists(bad_file):
        print(f"❌ 问题文件不存在: {bad_file}")
        return
    
    # 执行完整诊断
    diagnostic.full_diagnostic(good_file, bad_file)

if __name__ == "__main__":
    main()
