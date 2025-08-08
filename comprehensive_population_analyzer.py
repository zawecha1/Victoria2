"""
Victoria II 存档人口属性详细分析器
全面分析存档文件中人口块的各种属性，包括它们的含义、取值范围和分布情况
"""

import re
import json
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import statistics

class ComprehensivePopulationAnalyzer:
    def __init__(self, save_file: str):
        """初始化分析器"""
        self.save_file = save_file
        self.content = ""
        self.pop_attributes = defaultdict(list)
        self.pop_types = []
        self.attribute_stats = defaultdict(dict)
        
        # Victoria II 已知的人口类型
        self.known_pop_types = [
            'farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
            'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
            'bureaucrats', 'intellectuals'
        ]
        
        # 已知的属性类型和含义
        self.attribute_meanings = {
            'size': '人口数量 - 该人口组的总人数',
            'culture': '文化 - 人口的文化归属',
            'religion': '宗教 - 人口的宗教信仰',
            'location': '位置 - 人口所在的省份ID',
            'mil': '斗争性 - 人口的革命倾向（0-10）',
            'con': '意识 - 人口的政治意识（0-10）',
            'money': '金钱 - 人口拥有的财富',
            'bank': '银行存款 - 人口的银行储蓄',
            'literacy': '识字率 - 人口的教育水平（0-1）',
            'ideology': '意识形态 - 人口的政治倾向分布',
            'issues': '政策态度 - 人口对各项政策的态度',
            'unemployment': '失业 - 失业人口数量',
            'luxury_needs': '奢侈品需求 - 奢侈品消费情况（0-1）',
            'everyday_needs': '日常需求 - 基本生活需求满足度（0-1）',
            'life_needs': '生存需求 - 基本生存需求满足度（0-1）'
        }
        
        self.load_file()
    
    def load_file(self):
        """加载存档文件"""
        try:
            with open(self.save_file, 'r', encoding='utf-8-sig', errors='ignore') as f:
                self.content = f.read()
            print(f"✅ 文件加载成功: {self.save_file}")
            print(f"📊 文件大小: {len(self.content):,} 字符")
        except Exception as e:
            print(f"❌ 文件加载失败: {e}")
            raise
    
    def find_all_population_blocks(self) -> List[Tuple[str, str, str]]:
        """查找所有人口块
        
        Returns:
            List[Tuple[str, str, str]]: [(人口类型, 人口块内容, 省份ID), ...]
        """
        population_blocks = []
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        print(f"🔍 找到 {len(province_matches)} 个省份，开始分析人口块...")
        
        for i, province_match in enumerate(province_matches):
            province_id = province_match.group(1)
            start_pos = province_match.end()
            
            # 找到省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                # 查找下一个顶级块
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+10000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 5000
            
            province_content = self.content[start_pos:end_pos]
            
            # 在省份内查找所有人口类型
            for pop_type in self.known_pop_types:
                # 查找该人口类型的所有实例
                pattern = f'({pop_type}=\\s*{{[^{{}}]*(?:{{[^{{}}]*}}[^{{}}]*)*}})'
                matches = list(re.finditer(pattern, province_content, re.DOTALL))
                
                for match in matches:
                    pop_block = match.group(1)
                    population_blocks.append((pop_type, pop_block, province_id))
            
            # 进度显示
            if (i + 1) % 500 == 0:
                print(f"已处理 {i + 1}/{len(province_matches)} 个省份...")
        
        print(f"✅ 总计找到 {len(population_blocks)} 个人口块")
        return population_blocks
    
    def extract_attributes_from_block(self, pop_block: str) -> Dict[str, Any]:
        """从人口块中提取所有属性
        
        Args:
            pop_block: 人口块内容
            
        Returns:
            Dict[str, Any]: 属性字典
        """
        attributes = {}
        
        # 提取基本数值属性
        numeric_patterns = {
            'size': r'size\s*=\s*([\d.]+)',
            'mil': r'mil\s*=\s*([\d.]+)',
            'con': r'con\s*=\s*([\d.]+)', 
            'money': r'money\s*=\s*([\d.]+)',
            'bank': r'bank\s*=\s*([\d.]+)',
            'literacy': r'literacy\s*=\s*([\d.]+)',
            'unemployment': r'unemployment\s*=\s*([\d.]+)',
            'luxury_needs': r'luxury_needs\s*=\s*([\d.]+)',
            'everyday_needs': r'everyday_needs\s*=\s*([\d.]+)',
            'life_needs': r'life_needs\s*=\s*([\d.]+)'
        }
        
        for attr_name, pattern in numeric_patterns.items():
            match = re.search(pattern, pop_block)
            if match:
                try:
                    attributes[attr_name] = float(match.group(1))
                except ValueError:
                    attributes[attr_name] = match.group(1)
        
        # 提取文本属性
        text_patterns = {
            'culture': r'(\w+)\s*=\s*(\w+)',  # 文化=宗教形式
            'religion': r'(\w+)\s*=\s*(\w+)'   # 同上，需要进一步解析
        }
        
        # 提取文化和宗教（特殊处理）
        culture_religion_matches = re.findall(r'(\w+)\s*=\s*(\w+)', pop_block)
        cultures = []
        religions = set()
        
        for culture, religion in culture_religion_matches:
            # 跳过数值属性
            if culture in numeric_patterns or religion.replace('.', '').isdigit():
                continue
            cultures.append(culture)
            religions.add(religion)
        
        if cultures:
            attributes['cultures'] = cultures
        if religions:
            attributes['religions'] = list(religions)
        
        # 提取意识形态块
        ideology_match = re.search(r'ideology\s*=\s*{([^}]*)}', pop_block, re.DOTALL)
        if ideology_match:
            ideology_content = ideology_match.group(1)
            ideology_values = {}
            for id_value_match in re.finditer(r'(\d+)\s*=\s*([\d.]+)', ideology_content):
                ideology_id = int(id_value_match.group(1))
                ideology_value = float(id_value_match.group(2))
                ideology_values[ideology_id] = ideology_value
            if ideology_values:
                attributes['ideology'] = ideology_values
        
        # 提取政策态度块
        issues_match = re.search(r'issues\s*=\s*{([^}]*)}', pop_block, re.DOTALL)
        if issues_match:
            issues_content = issues_match.group(1)
            issues_values = {}
            for id_value_match in re.finditer(r'(\d+)\s*=\s*([\d.]+)', issues_content):
                issue_id = int(id_value_match.group(1))
                issue_value = float(id_value_match.group(2))
                issues_values[issue_id] = issue_value
            if issues_values:
                attributes['issues'] = issues_values
        
        return attributes
    
    def analyze_all_populations(self) -> Dict[str, Any]:
        """分析所有人口属性"""
        print("\n🔬 开始全面分析人口属性...")
        
        # 获取所有人口块
        population_blocks = self.find_all_population_blocks()
        
        if not population_blocks:
            print("❌ 未找到任何人口块")
            return {}
        
        # 按人口类型分组统计
        pop_type_stats = defaultdict(lambda: {
            'count': 0,
            'attributes': defaultdict(list)
        })
        
        # 全局属性统计
        global_stats = defaultdict(list)
        
        print("\n📊 正在分析人口属性...")
        for i, (pop_type, pop_block, province_id) in enumerate(population_blocks):
            attributes = self.extract_attributes_from_block(pop_block)
            
            # 更新人口类型统计
            pop_type_stats[pop_type]['count'] += 1
            
            # 记录属性值
            for attr_name, attr_value in attributes.items():
                if isinstance(attr_value, (int, float)):
                    pop_type_stats[pop_type]['attributes'][attr_name].append(attr_value)
                    global_stats[attr_name].append(attr_value)
                elif isinstance(attr_value, list):
                    pop_type_stats[pop_type]['attributes'][attr_name].extend(attr_value)
                    global_stats[attr_name].extend(attr_value)
                elif isinstance(attr_value, dict):
                    # 对于字典类型（如意识形态），记录所有的值
                    for key, value in attr_value.items():
                        global_stats[f'{attr_name}_{key}'].append(value)
            
            # 进度显示
            if (i + 1) % 1000 == 0:
                print(f"已分析 {i + 1}/{len(population_blocks)} 个人口块...")
        
        # 计算统计数据
        analysis_result = {
            'total_population_blocks': len(population_blocks),
            'pop_type_distribution': {},
            'attribute_analysis': {},
            'global_statistics': {}
        }
        
        # 人口类型分布
        for pop_type, stats in pop_type_stats.items():
            analysis_result['pop_type_distribution'][pop_type] = stats['count']
        
        # 属性分析
        for attr_name, values in global_stats.items():
            if not values:
                continue
                
            if all(isinstance(v, (int, float)) for v in values):
                # 数值属性分析
                analysis_result['attribute_analysis'][attr_name] = {
                    'type': 'numeric',
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'unique_values': len(set(values))
                }
                
                # 如果值较少，显示分布
                if len(set(values)) <= 20:
                    analysis_result['attribute_analysis'][attr_name]['distribution'] = dict(Counter(values))
            
            else:
                # 文本/分类属性分析
                value_counts = Counter(values)
                analysis_result['attribute_analysis'][attr_name] = {
                    'type': 'categorical',
                    'count': len(values),
                    'unique_values': len(value_counts),
                    'most_common': value_counts.most_common(10)
                }
        
        return analysis_result
    
    def print_analysis_report(self, analysis_result: Dict[str, Any]):
        """打印分析报告"""
        print("\n" + "="*80)
        print("📋 Victoria II 人口属性详细分析报告")
        print("="*80)
        
        # 基本统计
        print(f"\n📊 基本统计:")
        print(f"  总人口块数: {analysis_result['total_population_blocks']:,}")
        
        # 人口类型分布
        print(f"\n👥 人口类型分布:")
        pop_dist = analysis_result['pop_type_distribution']
        sorted_pops = sorted(pop_dist.items(), key=lambda x: x[1], reverse=True)
        for pop_type, count in sorted_pops:
            percentage = (count / analysis_result['total_population_blocks']) * 100
            print(f"  {pop_type:12}: {count:6,} ({percentage:5.1f}%)")
        
        # 属性详细分析
        print(f"\n🔍 属性详细分析:")
        for attr_name, attr_stats in analysis_result['attribute_analysis'].items():
            meaning = self.attribute_meanings.get(attr_name, "未知属性")
            print(f"\n  📋 {attr_name} - {meaning}")
            print(f"     类型: {attr_stats['type']}")
            print(f"     出现次数: {attr_stats['count']:,}")
            
            if attr_stats['type'] == 'numeric':
                print(f"     取值范围: {attr_stats['min']:.3f} - {attr_stats['max']:.3f}")
                print(f"     平均值: {attr_stats['mean']:.3f}")
                print(f"     中位数: {attr_stats['median']:.3f}")
                print(f"     唯一值数量: {attr_stats['unique_values']}")
                
                # 显示分布（如果值较少）
                if 'distribution' in attr_stats:
                    print(f"     值分布:")
                    for value, count in sorted(attr_stats['distribution'].items()):
                        percentage = (count / attr_stats['count']) * 100
                        print(f"       {value}: {count:,} ({percentage:.1f}%)")
            
            elif attr_stats['type'] == 'categorical':
                print(f"     唯一值数量: {attr_stats['unique_values']}")
                print(f"     最常见的值:")
                for value, count in attr_stats['most_common']:
                    percentage = (count / attr_stats['count']) * 100
                    print(f"       {value}: {count:,} ({percentage:.1f}%)")
        
        print(f"\n" + "="*80)
    
    def save_analysis_to_file(self, analysis_result: Dict[str, Any], output_file: str = "population_analysis.json"):
        """保存分析结果到文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 分析结果已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) != 2:
        print("用法: python comprehensive_population_analyzer.py <存档文件.v2>")
        print("示例: python comprehensive_population_analyzer.py ChinaUseIt.v2")
        return
    
    save_file = sys.argv[1]
    
    try:
        # 创建分析器
        analyzer = ComprehensivePopulationAnalyzer(save_file)
        
        # 执行分析
        result = analyzer.analyze_all_populations()
        
        if result:
            # 打印报告
            analyzer.print_analysis_report(result)
            
            # 保存结果
            output_file = f"{save_file}_comprehensive_analysis.json"
            analyzer.save_analysis_to_file(result, output_file)
            
            print(f"\n🎉 分析完成！")
            print(f"📄 详细数据已保存到: {output_file}")
        else:
            print("❌ 分析失败，未找到人口数据")
    
    except Exception as e:
        print(f"❌ 程序执行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
