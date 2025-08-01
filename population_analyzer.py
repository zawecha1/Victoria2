#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 人口属性分析器
分析存档文件中人口的各种枚举属性，包括文化、宗教、职业、意识等
"""

import re
import json
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter

@dataclass
class PopulationGroup:
    """人口组数据结构"""
    province_id: int
    pop_type: str           # 人口类型 (farmers, clerks, officers等)
    culture: str            # 文化
    religion: str           # 宗教
    size: int               # 人口数量
    militancy: float        # 斗争性
    consciousness: float    # 意识
    literacy: float         # 识字率
    money: float           # 资金
    needs: Dict[str, float] # 需求满足度
    issues: Dict[str, str]  # 政治议题倾向
    
    def __str__(self):
        return f"{self.pop_type}({self.culture}-{self.religion}): {self.size}人"

class PopulationAnalyzer:
    """人口属性分析器"""
    
    def __init__(self):
        self.content = ""
        self.populations = []
        
        # 已知的枚举类型
        self.pop_types = set()          # 人口类型
        self.cultures = set()           # 文化
        self.religions = set()          # 宗教
        self.goods = set()              # 商品
        self.issues = set()             # 政治议题
        
        # 统计信息
        self.stats = {
            'total_populations': 0,
            'total_people': 0,
            'by_culture': defaultdict(int),
            'by_religion': defaultdict(int),
            'by_pop_type': defaultdict(int),
            'by_province': defaultdict(int)
        }
    
    def load_save_file(self, filename: str) -> bool:
        """加载存档文件"""
        try:
            # 尝试多种编码
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
    
    def analyze_populations(self) -> bool:
        """分析人口数据"""
        print("开始分析人口数据...")
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        total_provinces = len(province_matches)
        print(f"找到 {total_provinces} 个省份")
        
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 确定省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                # 查找下一个主要段落
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+20000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 10000
            
            province_content = self.content[start_pos:end_pos]
            
            # 分析该省份的人口
            self._analyze_province_populations(province_id, province_content)
            
            # 进度显示
            if (i + 1) % 200 == 0:
                print(f"已分析 {i + 1}/{total_provinces} 个省份...")
        
        print(f"人口分析完成! 共找到 {len(self.populations)} 个人口组")
        return True
    
    def _analyze_province_populations(self, province_id: int, province_content: str):
        """分析单个省份的人口"""
        # 查找人口块的新模式 - Victoria II 中人口数据的实际结构
        # 模式: pop_type={ ... culture=religion ... }
        
        # 查找所有人口类型块
        pop_type_pattern = r'(\w+)=\s*{\s*([^{}]*(?:{[^{}]*}[^{}]*)*)}'
        pop_blocks = re.findall(pop_type_pattern, province_content, re.DOTALL)
        
        for pop_type, pop_content in pop_blocks:
            # 检查是否为人口类型
            if not self._is_pop_type(pop_type):
                continue
            
            # 提取人口信息
            try:
                # 查找 size
                size_match = re.search(r'size=(\d+)', pop_content)
                size = int(size_match.group(1)) if size_match else 0
                
                if size == 0:
                    continue
                
                # 查找文化=宗教组合
                culture_religion_match = re.search(r'(\w+)=(\w+)', pop_content)
                if culture_religion_match:
                    culture = culture_religion_match.group(1)
                    religion = culture_religion_match.group(2)
                else:
                    culture = "unknown"
                    religion = "unknown"
                
                # 查找其他属性
                mil_match = re.search(r'mil=([\d.]+)', pop_content)
                militancy = float(mil_match.group(1)) if mil_match else 0.0
                
                con_match = re.search(r'con=([\d.]+)', pop_content)
                consciousness = float(con_match.group(1)) if con_match else 0.0
                
                lit_match = re.search(r'literacy=([\d.]+)', pop_content)
                literacy = float(lit_match.group(1)) if lit_match else 0.0
                
                money_match = re.search(r'money=([\d.]+)', pop_content)
                money_val = float(money_match.group(1)) if money_match else 0.0
                
                # 创建人口组对象
                pop_group = PopulationGroup(
                    province_id=province_id,
                    pop_type=pop_type,
                    culture=culture,
                    religion=religion,
                    size=size,
                    militancy=militancy,
                    consciousness=consciousness,
                    literacy=literacy,
                    money=money_val,
                    needs={},  # 可以进一步扩展
                    issues={}  # 可以进一步扩展
                )
                
                self.populations.append(pop_group)
                
                # 收集枚举值
                self.pop_types.add(pop_type)
                self.cultures.add(culture)
                self.religions.add(religion)
                
                # 更新统计
                self.stats['total_populations'] += 1
                self.stats['total_people'] += size
                self.stats['by_culture'][culture] += size
                self.stats['by_religion'][religion] += size
                self.stats['by_pop_type'][pop_type] += size
                self.stats['by_province'][province_id] += size
                
            except (ValueError, AttributeError, TypeError) as e:
                # 跳过解析错误的数据
                continue
    
    def _is_pop_type(self, type_name: str) -> bool:
        """判断是否为人口类型"""
        known_pop_types = {
            'farmers', 'labourers', 'slaves', 'clerks', 'artisans', 'craftsmen',
            'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
            'bureaucrats', 'intellectuals'
        }
        return type_name.lower() in known_pop_types
    
    def get_enumeration_summary(self) -> Dict[str, List[str]]:
        """获取所有枚举属性的汇总"""
        return {
            'pop_types': sorted(list(self.pop_types)),
            'cultures': sorted(list(self.cultures)),
            'religions': sorted(list(self.religions)),
            'goods': sorted(list(self.goods)),
            'issues': sorted(list(self.issues))
        }
    
    def get_detailed_statistics(self) -> Dict:
        """获取详细统计信息"""
        # 计算平均值
        avg_militancy = sum(p.militancy for p in self.populations) / len(self.populations) if self.populations else 0
        avg_consciousness = sum(p.consciousness for p in self.populations) / len(self.populations) if self.populations else 0
        avg_literacy = sum(p.literacy for p in self.populations) / len(self.populations) if self.populations else 0
        
        # 按文化分组的详细统计
        culture_details = {}
        for culture in self.cultures:
            culture_pops = [p for p in self.populations if p.culture == culture]
            if culture_pops:
                culture_details[culture] = {
                    'total_people': sum(p.size for p in culture_pops),
                    'total_groups': len(culture_pops),
                    'avg_militancy': sum(p.militancy for p in culture_pops) / len(culture_pops),
                    'avg_consciousness': sum(p.consciousness for p in culture_pops) / len(culture_pops),
                    'avg_literacy': sum(p.literacy for p in culture_pops) / len(culture_pops),
                    'pop_types': list(set(p.pop_type for p in culture_pops)),
                    'religions': list(set(p.religion for p in culture_pops))
                }
        
        return {
            'basic_stats': self.stats,
            'averages': {
                'militancy': avg_militancy,
                'consciousness': avg_consciousness,
                'literacy': avg_literacy
            },
            'culture_details': culture_details,
            'top_cultures': dict(Counter(self.stats['by_culture']).most_common(10)),
            'top_religions': dict(Counter(self.stats['by_religion']).most_common(10)),
            'pop_type_distribution': dict(Counter(self.stats['by_pop_type']).most_common())
        }
    
    def find_populations_by_criteria(self, **criteria) -> List[PopulationGroup]:
        """根据条件查找人口组"""
        result = []
        for pop in self.populations:
            match = True
            for key, value in criteria.items():
                if hasattr(pop, key):
                    if getattr(pop, key) != value:
                        match = False
                        break
            if match:
                result.append(pop)
        return result
    
    def export_analysis(self, output_file: str = "population_analysis.json"):
        """导出分析结果"""
        analysis_data = {
            'enumeration_summary': self.get_enumeration_summary(),
            'detailed_statistics': self.get_detailed_statistics(),
            'sample_populations': [
                {
                    'province_id': p.province_id,
                    'pop_type': p.pop_type,
                    'culture': p.culture,
                    'religion': p.religion,
                    'size': p.size,
                    'militancy': p.militancy,
                    'consciousness': p.consciousness,
                    'literacy': p.literacy,
                    'money': p.money
                }
                for p in self.populations[:100]  # 导出前100个样本
            ]
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 分析结果已导出到: {output_file}")
            return True
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False
    
    def print_summary(self):
        """打印汇总信息"""
        print(f"\n{'='*80}")
        print("Victoria II 人口属性分析汇总")
        print(f"{'='*80}")
        
        # 基本统计
        print(f"总人口组数: {self.stats['total_populations']:,}")
        print(f"总人口数量: {self.stats['total_people']:,}")
        print(f"省份数量: {len(self.stats['by_province'])}")
        
        # 枚举类型汇总
        enums = self.get_enumeration_summary()
        print(f"\n📊 枚举属性统计:")
        print(f"人口类型: {len(enums['pop_types'])} 种")
        print(f"文化类型: {len(enums['cultures'])} 种")
        print(f"宗教类型: {len(enums['religions'])} 种")
        
        # 显示具体列表
        print(f"\n👥 人口类型列表:")
        for i, pop_type in enumerate(enums['pop_types'], 1):
            count = self.stats['by_pop_type'].get(pop_type, 0)
            print(f"  {i:2d}. {pop_type:<15} ({count:,} 人)")
        
        print(f"\n🎭 文化类型 (前20):")
        top_cultures = sorted(self.stats['by_culture'].items(), key=lambda x: x[1], reverse=True)[:20]
        for i, (culture, count) in enumerate(top_cultures, 1):
            print(f"  {i:2d}. {culture:<20} ({count:,} 人)")
        
        print(f"\n⛪ 宗教类型 (前15):")
        top_religions = sorted(self.stats['by_religion'].items(), key=lambda x: x[1], reverse=True)[:15]
        for i, (religion, count) in enumerate(top_religions, 1):
            print(f"  {i:2d}. {religion:<20} ({count:,} 人)")
        
        # 平均值统计
        if self.populations:
            avg_mil = sum(p.militancy for p in self.populations) / len(self.populations)
            avg_con = sum(p.consciousness for p in self.populations) / len(self.populations)
            avg_lit = sum(p.literacy for p in self.populations) / len(self.populations)
            
            print(f"\n📈 平均属性:")
            print(f"平均斗争性: {avg_mil:.3f}")
            print(f"平均意识: {avg_con:.3f}")
            print(f"平均识字率: {avg_lit:.3f}")
        
        print(f"\n{'='*80}")

def main():
    """主函数"""
    print("Victoria II 人口属性分析器")
    print("="*50)
    
    # 获取文件名
    filename = input("请输入存档文件名 (默认: China1836_04_29.v2): ").strip()
    if not filename:
        filename = "China1836_04_29.v2"
    
    # 创建分析器并执行分析
    analyzer = PopulationAnalyzer()
    
    print(f"\n开始分析文件: {filename}")
    
    # 加载文件
    if not analyzer.load_save_file(filename):
        print("❌ 文件加载失败")
        return
    
    # 分析人口
    if not analyzer.analyze_populations():
        print("❌ 人口分析失败")
        return
    
    # 显示汇总
    analyzer.print_summary()
    
    # 询问是否导出
    export_choice = input("\n是否导出详细分析结果到JSON文件？(y/n): ").strip().lower()
    if export_choice in ['y', 'yes']:
        analyzer.export_analysis()
    
    # 交互式查询
    while True:
        print(f"\n{'='*50}")
        print("交互式查询选项:")
        print("1. 按文化查找人口")
        print("2. 按宗教查找人口")
        print("3. 按人口类型查找人口")
        print("4. 按省份查找人口")
        print("0. 退出")
        
        choice = input("请选择 (0-4): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            culture = input("请输入文化名称: ").strip()
            pops = analyzer.find_populations_by_criteria(culture=culture)
            print(f"找到 {len(pops)} 个 {culture} 文化的人口组")
            for pop in pops[:10]:  # 显示前10个
                print(f"  省份{pop.province_id}: {pop}")
        elif choice == "2":
            religion = input("请输入宗教名称: ").strip()
            pops = analyzer.find_populations_by_criteria(religion=religion)
            print(f"找到 {len(pops)} 个 {religion} 宗教的人口组")
            for pop in pops[:10]:
                print(f"  省份{pop.province_id}: {pop}")
        elif choice == "3":
            pop_type = input("请输入人口类型: ").strip()
            pops = analyzer.find_populations_by_criteria(pop_type=pop_type)
            print(f"找到 {len(pops)} 个 {pop_type} 类型的人口组")
            for pop in pops[:10]:
                print(f"  省份{pop.province_id}: {pop}")
        elif choice == "4":
            try:
                province_id = int(input("请输入省份ID: ").strip())
                pops = analyzer.find_populations_by_criteria(province_id=province_id)
                print(f"省份 {province_id} 有 {len(pops)} 个人口组")
                for pop in pops:
                    print(f"  {pop}")
            except ValueError:
                print("请输入有效的省份ID")

if __name__ == "__main__":
    main()
