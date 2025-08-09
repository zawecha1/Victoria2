#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 国家块分析器
专门用于查找和分析所有国家块的字段含义和取值范围
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter
from bracket_parser import Victoria2BracketParser, BracketBlock

class Victoria2CountryAnalyzer:
    """Victoria II 国家块分析器"""
    
    def __init__(self, file_path: str = None, debug_mode: bool = False):
        self.content = ""
        self.file_path = file_path
        self.parser = Victoria2BracketParser()
        self.structure = None
        self.debug_mode = debug_mode
        
        # 分析结果存储
        self.country_blocks = []  # 所有国家块
        self.field_analysis = defaultdict(dict)  # 字段分析结果
        self.country_tags = set()  # 所有国家标签
        
        # 已知的国家字段定义
        self.known_country_fields = {
            # 基本信息
            'primary_culture': '主要文化',
            'religion': '国教',
            'government': '政府类型',
            'plurality': '多元化程度',
            'nationalvalue': '国家价值观',
            'literacy': '识字率',
            'non_state_culture_literacy': '非国家文化识字率',
            'civilized': '文明化状态',
            'prestige': '威望',
            'ruling_party': '执政党',
            'last_election': '上次选举日期',
            'upper_house': '上议院构成',
            'lower_house': '下议院构成',
            'active_party': '活跃政党',
            'national_focus': '国家焦点',
            
            # 地理和领土
            'capital': '首都省份ID',
            'original_capital': '原始首都',
            'state': '州',
            'province': '省份',
            'core': '核心省份',
            
            # 军事
            'army': '陆军',
            'navy': '海军',
            'leader': '将领',
            'mobilized': '动员状态',
            'war_exhaustion': '战争疲惫度',
            'war': '战争状态',
            'truce': '停战协议',
            'military_access': '军事通行权',
            'guarantee': '保护协议',
            'sphere_member': '势力范围成员',
            'vassal': '附庸国',
            'substate': '附属国',
            'union': '联邦',
            
            # 经济
            'money': '国库资金',
            'bank': '银行资金',
            'debt': '债务',
            'tax_eff': '税收效率',
            'loan': '贷款',
            'expenditure': '支出',
            'poor_tax': '穷人税',
            'middle_tax': '中产税',
            'rich_tax': '富人税',
            'education_spending': '教育支出',
            'crime_fighting': '治安支出',
            'social_spending': '社会支出',
            'military_spending': '军事支出',
            'leadership': '领导力',
            'research_points': '研究点数',
            
            # 科技
            'technology': '科技',
            'schools': '学派',
            'invention': '发明',
            
            # 外交
            'relation': '外交关系',
            'influence': '影响力',
            'opinion': '好感度',
            'alliance': '同盟',
            'casus_belli': '开战理由',
            'rival': '宿敌',
            'friendly': '友好关系',
            'colonial_points': '殖民点数',
            
            # 政治和社会
            'consciousness': '觉醒度',
            'badboy': '恶名度/好战度',
            'suppression': '镇压点数',
            'diplomatic_points': '外交点数',
            'research_points': '研究点数',
            'colonial_points': '殖民点数',
            'naval_plans': '海军计划',
            'army_plans': '陆军计划',
            
            # 人口相关
            'pop': '人口',
            'culture': '文化',
            'accepted_culture': '被接受文化',
            'primary_culture': '主要文化',
            
            # 历史和事件
            'history': '历史记录',
            'decision': '决议',
            'flag': '标志变量',
            'modifier': '修正',
            'timed_modifier': '定时修正',
            
            # 贸易
            'trade': '贸易',
            'factory': '工厂',
            'building': '建筑',
            'railroad': '铁路',
            'fort': '要塞',
            'naval_base': '海军基地',
            
            # 其他
            'tag': '国家标签',
            'overlord': '宗主国',
            'great_wars_enabled': '大战启用',
            'ai': 'AI设置',
            'human': '人类玩家',
        }
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, filename: str) -> bool:
        """加载存档文件并初始化解析器"""
        try:
            self.file_path = filename
            
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(filename, 'r', encoding=encoding, errors='ignore') as f:
                        self.content = f.read()
                    print(f"✅ 文件读取成功 (编码: {encoding})，大小: {len(self.content):,} 字符")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print("❌ 所有编码尝试失败")
                return False
            
            # 初始化解析器
            print("🔍 正在解析文件结构...")
            self.parser.load_content(self.content)
            # 解析顶级块
            self.structure = self._parse_top_level_blocks()
            print(f"✅ 文件结构解析完成")
            
            return True
        except Exception as e:
            print(f"❌ 文件读取失败: {e}")
            return False
    
    def _parse_top_level_blocks(self) -> BracketBlock:
        """解析顶级块结构"""
        # 创建虚拟根块
        root_block = BracketBlock("ROOT", 0, len(self.content), self.content, 0)
        
        # 查找所有顶级块（格式: name={...}）
        pattern = r'(\w+)\s*=\s*\{'
        matches = list(re.finditer(pattern, self.content))
        
        print(f"🔍 找到 {len(matches)} 个潜在的顶级块...")
        
        for match in matches:
            name = match.group(1)
            start_pos = match.end() - 1  # 指向开始的 {
            
            # 找到匹配的结束花括号
            end_pos = self.parser.find_matching_brace(start_pos)
            
            if end_pos != -1:
                # 提取块内容（不包含花括号）
                content = self.content[start_pos + 1:end_pos]
                
                # 创建块对象
                block = BracketBlock(name, start_pos, end_pos, content, 1)
                root_block.children.append(block)
        
        print(f"✅ 解析了 {len(root_block.children)} 个顶级块")
        return root_block
    
    def find_all_country_blocks(self) -> List[BracketBlock]:
        """查找所有国家块"""
        print("\n🔍 查找所有国家块...")
        
        if not self.structure:
            print("❌ 文件结构未初始化")
            return []
        
        country_blocks = []
        
        # 遍历所有顶级块
        for block in self.structure.children:
            # 检查是否为国家标签（3个大写字母）
            if re.match(r'^[A-Z]{3}$', block.name.strip()):
                # 进一步验证这是国家定义块而不是外交关系块
                if self._is_country_definition_block(block):
                    country_blocks.append(block)
                    self.country_tags.add(block.name.strip())
        
        self.country_blocks = country_blocks
        print(f"✅ 找到 {len(country_blocks)} 个国家定义块")
        print(f"📋 国家标签: {sorted(list(self.country_tags))[:10]}{'...' if len(self.country_tags) > 10 else ''}")
        
        return country_blocks
    
    def _is_country_definition_block(self, block: BracketBlock) -> bool:
        """判断块是否为国家定义块（而非外交关系块）"""
        content = block.content.lower()
        
        # 国家定义块的特征字段
        country_indicators = [
            'primary_culture', 'capital', 'government', 'civilized',
            'technology', 'ruling_party', 'upper_house', 'plurality',
            'prestige', 'money', 'leadership', 'consciousness'
        ]
        
        # 外交关系块的特征字段
        diplomatic_indicators = [
            'relation', 'influence', 'opinion', 'alliance',
            'truce', 'military_access', 'guarantee'
        ]
        
        # 计算特征字段出现次数
        country_score = sum(1 for indicator in country_indicators if indicator in content)
        diplomatic_score = sum(1 for indicator in diplomatic_indicators if indicator in content)
        
        # 国家定义块应该有更多的国家特征字段，且块较大
        is_country_block = (
            country_score >= 3 and  # 至少3个国家特征
            (country_score > diplomatic_score or len(block.content) > 1000)  # 国家特征更多或块较大
        )
        
        if self.debug_mode:
            print(f"块 {block.name}: 国家特征={country_score}, 外交特征={diplomatic_score}, "
                  f"大小={len(block.content)}, 判定={'国家块' if is_country_block else '外交块'}")
        
        return is_country_block
    
    def analyze_country_fields(self) -> Dict[str, Any]:
        """分析所有国家块的字段"""
        print("\n📊 开始分析国家块字段...")
        
        if not self.country_blocks:
            self.find_all_country_blocks()
        
        if not self.country_blocks:
            print("❌ 未找到国家块")
            return {}
        
        # 统计所有字段
        field_stats = defaultdict(lambda: {
            'count': 0,
            'countries': set(),
            'values': Counter(),
            'value_examples': [],
            'numeric_values': [],
            'string_values': [],
            'block_values': [],
            'description': ''
        })
        
        # 分析每个国家块
        for i, country_block in enumerate(self.country_blocks):
            country_tag = country_block.name.strip()
            
            # 提取所有字段
            fields = self._extract_fields_from_block(country_block)
            
            for field_name, field_info in fields.items():
                stats = field_stats[field_name]
                stats['count'] += field_info['count']
                stats['countries'].add(country_tag)
                
                # 分类存储值
                for value in field_info['values']:
                    stats['values'][value] += 1
                    
                    # 分类存储示例值
                    if len(stats['value_examples']) < 10:
                        stats['value_examples'].append(f"{country_tag}={value}")
                    
                    # 按类型分类
                    if self._is_numeric_value(value):
                        try:
                            numeric_val = float(value)
                            stats['numeric_values'].append(numeric_val)
                        except:
                            pass
                    elif self._is_block_value(value):
                        stats['block_values'].append(value)
                    else:
                        stats['string_values'].append(value)
            
            # 进度显示
            if (i + 1) % 50 == 0 or i == len(self.country_blocks) - 1:
                print(f"已分析 {i + 1}/{len(self.country_blocks)} 个国家块...")
        
        # 处理统计结果
        processed_stats = {}
        for field_name, stats in field_stats.items():
            processed_stats[field_name] = {
                'description': self.known_country_fields.get(field_name, '未知字段'),
                'total_occurrences': stats['count'],
                'country_count': len(stats['countries']),
                'coverage_percentage': len(stats['countries']) / len(self.country_blocks) * 100,
                'most_common_values': stats['values'].most_common(5),
                'value_examples': stats['value_examples'][:5],
                'value_types': {
                    'numeric_count': len(stats['numeric_values']),
                    'string_count': len(stats['string_values']),
                    'block_count': len(stats['block_values'])
                }
            }
            
            # 数值类型的统计
            if stats['numeric_values']:
                numeric_vals = stats['numeric_values']
                processed_stats[field_name]['numeric_stats'] = {
                    'min': min(numeric_vals),
                    'max': max(numeric_vals),
                    'avg': sum(numeric_vals) / len(numeric_vals),
                    'range': f"{min(numeric_vals):.3f} - {max(numeric_vals):.3f}"
                }
        
        self.field_analysis = processed_stats
        print(f"✅ 字段分析完成，共分析 {len(processed_stats)} 个不同字段")
        
        return processed_stats
    
    def _extract_fields_from_block(self, block: BracketBlock) -> Dict[str, Dict]:
        """从块中提取所有字段"""
        content = block.content
        fields = defaultdict(lambda: {'count': 0, 'values': []})
        
        # 匹配简单字段 (key=value)
        simple_pattern = r'(\w+)\s*=\s*([^{}\n]+?)(?=\n|\s|$)'
        simple_matches = re.findall(simple_pattern, content, re.MULTILINE)
        
        for field_name, value in simple_matches:
            field_name = field_name.strip()
            value = value.strip().strip('"')
            if value and field_name:
                fields[field_name]['count'] += 1
                fields[field_name]['values'].append(value)
        
        # 匹配块字段 (key={ ... })
        block_pattern = r'(\w+)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        block_matches = re.findall(block_pattern, content, re.DOTALL)
        
        for field_name, block_content in block_matches:
            field_name = field_name.strip()
            if field_name:
                fields[field_name]['count'] += 1
                # 对于块内容，我们存储块的摘要
                summary = self._summarize_block_content(block_content)
                fields[field_name]['values'].append(f"{{block: {summary}}}")
        
        return dict(fields)
    
    def _summarize_block_content(self, block_content: str) -> str:
        """总结块内容"""
        content = block_content.strip()
        if len(content) <= 50:
            return content.replace('\n', ' ').replace('\t', ' ')
        
        # 提取关键信息
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if len(lines) <= 3:
            return ' | '.join(lines)
        
        return f"{lines[0]} | ... | {lines[-1]} ({len(lines)} items)"
    
    def _is_numeric_value(self, value: str) -> bool:
        """判断值是否为数值"""
        try:
            float(value)
            return True
        except:
            return False
    
    def _is_block_value(self, value: str) -> bool:
        """判断值是否为块值"""
        return value.startswith('{')
    
    def generate_analysis_report(self, output_file: str = None) -> str:
        """生成分析报告"""
        if not self.field_analysis:
            self.analyze_country_fields()
        
        report = []
        report.append("=" * 80)
        report.append("Victoria II 国家块字段分析报告")
        report.append("=" * 80)
        report.append(f"分析时间: {self._get_current_time()}")
        report.append(f"源文件: {self.file_path}")
        report.append(f"总国家数: {len(self.country_blocks)}")
        report.append(f"总字段数: {len(self.field_analysis)}")
        report.append("")
        
        # 按覆盖率排序字段
        sorted_fields = sorted(
            self.field_analysis.items(),
            key=lambda x: x[1]['coverage_percentage'],
            reverse=True
        )
        
        report.append("字段分析详情 (按覆盖率排序):")
        report.append("-" * 80)
        
        for field_name, stats in sorted_fields:
            report.append(f"\n【字段】{field_name}")
            report.append(f"  描述: {stats['description']}")
            report.append(f"  出现次数: {stats['total_occurrences']}")
            report.append(f"  涉及国家: {stats['country_count']}/{len(self.country_blocks)} ({stats['coverage_percentage']:.1f}%)")
            
            # 值类型统计
            types = stats['value_types']
            type_info = []
            if types['numeric_count'] > 0:
                type_info.append(f"数值: {types['numeric_count']}")
            if types['string_count'] > 0:
                type_info.append(f"字符串: {types['string_count']}")
            if types['block_count'] > 0:
                type_info.append(f"块: {types['block_count']}")
            report.append(f"  值类型: {', '.join(type_info)}")
            
            # 数值范围
            if 'numeric_stats' in stats:
                ns = stats['numeric_stats']
                report.append(f"  数值范围: {ns['range']} (平均: {ns['avg']:.3f})")
            
            # 常见值
            if stats['most_common_values']:
                common_vals = [f"{val}({count})" for val, count in stats['most_common_values']]
                report.append(f"  常见值: {', '.join(common_vals)}")
            
            # 示例
            if stats['value_examples']:
                report.append(f"  示例: {', '.join(stats['value_examples'])}")
        
        # 字段分类总结
        report.append("\n" + "=" * 80)
        report.append("字段分类总结:")
        report.append("-" * 80)
        
        categories = self._categorize_fields()
        for category, fields in categories.items():
            report.append(f"\n【{category}】({len(fields)} 个字段)")
            for field in sorted(fields):
                coverage = self.field_analysis[field]['coverage_percentage']
                report.append(f"  • {field}: {coverage:.1f}% 覆盖率")
        
        report_text = '\n'.join(report)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                print(f"✅ 分析报告已保存: {output_file}")
            except Exception as e:
                print(f"❌ 报告保存失败: {e}")
        
        return report_text
    
    def _categorize_fields(self) -> Dict[str, List[str]]:
        """将字段按类别分组"""
        categories = {
            '基本信息': [],
            '政治制度': [],
            '经济财政': [],
            '军事外交': [],
            '科技文化': [],
            '地理领土': [],
            '人口文化': [],
            '历史事件': [],
            '未分类': []
        }
        
        # 字段分类规则
        classification_rules = {
            '基本信息': ['tag', 'capital', 'original_capital', 'civilized', 'human', 'ai'],
            '政治制度': ['government', 'ruling_party', 'last_election', 'upper_house', 'lower_house', 
                        'active_party', 'plurality', 'nationalvalue', 'consciousness', 'suppression'],
            '经济财政': ['money', 'bank', 'debt', 'tax_eff', 'loan', 'expenditure', 'poor_tax', 
                        'middle_tax', 'rich_tax', 'education_spending', 'crime_fighting', 
                        'social_spending', 'military_spending', 'trade', 'factory', 'building'],
            '军事外交': ['army', 'navy', 'leader', 'mobilized', 'war_exhaustion', 'war', 'truce',
                        'military_access', 'guarantee', 'alliance', 'relation', 'influence', 
                        'opinion', 'casus_belli', 'rival', 'friendly', 'badboy', 'prestige'],
            '科技文化': ['technology', 'schools', 'invention', 'research_points', 'leadership',
                        'literacy', 'non_state_culture_literacy'],
            '地理领土': ['state', 'province', 'core', 'railroad', 'fort', 'naval_base',
                        'colonial_points', 'sphere_member', 'vassal', 'substate', 'union', 'overlord'],
            '人口文化': ['pop', 'culture', 'accepted_culture', 'primary_culture', 'religion'],
            '历史事件': ['history', 'decision', 'flag', 'modifier', 'timed_modifier', 'national_focus']
        }
        
        # 分类字段
        for field_name in self.field_analysis.keys():
            categorized = False
            for category, field_list in classification_rules.items():
                if any(keyword in field_name.lower() for keyword in field_list):
                    categories[category].append(field_name)
                    categorized = True
                    break
            
            if not categorized:
                categories['未分类'].append(field_name)
        
        # 移除空分类
        return {k: v for k, v in categories.items() if v}
    
    def save_analysis_to_json(self, output_file: str = None) -> str:
        """将分析结果保存为JSON格式"""
        if not output_file:
            output_file = f"country_analysis_{self._get_timestamp()}.json"
        
        # 准备JSON数据
        json_data = {
            'metadata': {
                'analysis_time': self._get_current_time(),
                'source_file': self.file_path,
                'total_countries': len(self.country_blocks),
                'total_fields': len(self.field_analysis),
                'country_tags': sorted(list(self.country_tags))
            },
            'field_analysis': {}
        }
        
        # 转换数据为JSON可序列化格式
        for field_name, stats in self.field_analysis.items():
            json_data['field_analysis'][field_name] = {
                'description': stats['description'],
                'total_occurrences': stats['total_occurrences'],
                'country_count': stats['country_count'],
                'coverage_percentage': round(stats['coverage_percentage'], 2),
                'most_common_values': stats['most_common_values'],
                'value_examples': stats['value_examples'],
                'value_types': stats['value_types']
            }
            
            if 'numeric_stats' in stats:
                json_data['field_analysis'][field_name]['numeric_stats'] = {
                    'min': stats['numeric_stats']['min'],
                    'max': stats['numeric_stats']['max'],
                    'avg': round(stats['numeric_stats']['avg'], 3),
                    'range': stats['numeric_stats']['range']
                }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON分析结果已保存: {output_file}")
            return output_file
        except Exception as e:
            print(f"❌ JSON保存失败: {e}")
            return ""
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def print_summary(self):
        """打印分析摘要"""
        if not self.field_analysis:
            self.analyze_country_fields()
        
        print("\n" + "=" * 60)
        print("🏛️  Victoria II 国家块分析摘要")
        print("=" * 60)
        print(f"📊 总国家数: {len(self.country_blocks)}")
        print(f"📋 总字段数: {len(self.field_analysis)}")
        print(f"🏷️  国家标签: {len(self.country_tags)} 个")
        
        # 显示覆盖率最高的字段
        sorted_fields = sorted(
            self.field_analysis.items(),
            key=lambda x: x[1]['coverage_percentage'],
            reverse=True
        )
        
        print(f"\n🔝 覆盖率最高的10个字段:")
        for i, (field_name, stats) in enumerate(sorted_fields[:10]):
            print(f"  {i+1:2d}. {field_name:20s} {stats['coverage_percentage']:6.1f}% ({stats['description']})")
        
        # 显示字段分类统计
        categories = self._categorize_fields()
        print(f"\n📂 字段分类统计:")
        for category, fields in categories.items():
            print(f"  • {category:12s}: {len(fields):3d} 个字段")
        
        print("=" * 60)

def main():
    """示例用法"""
    print("🚀 Victoria II 国家块分析器")
    
    # 创建分析器实例
    analyzer = Victoria2CountryAnalyzer(debug_mode=False)
    
    # 加载文件
    filename = 'autosave.v2'  # 或其他存档文件
    if not analyzer.load_file(filename):
        print("❌ 文件加载失败")
        return
    
    # 查找所有国家块
    country_blocks = analyzer.find_all_country_blocks()
    
    if not country_blocks:
        print("❌ 未找到国家块")
        return
    
    # 分析字段
    field_analysis = analyzer.analyze_country_fields()
    
    # 打印摘要
    analyzer.print_summary()
    
    # 生成详细报告
    report_file = f"country_analysis_report_{analyzer._get_timestamp()}.txt"
    analyzer.generate_analysis_report(report_file)
    
    # 保存JSON数据
    json_file = f"country_analysis_data_{analyzer._get_timestamp()}.json"
    analyzer.save_analysis_to_json(json_file)
    
    print(f"\n✅ 分析完成!")
    print(f"📄 详细报告: {report_file}")
    print(f"📊 JSON数据: {json_file}")

if __name__ == "__main__":
    main()
