#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速国家块分析器 - 轻量级版本
"""

import re
from collections import defaultdict, Counter

class FastCountryAnalyzer:
    """快速国家块分析器"""
    
    def __init__(self):
        self.country_fields = {
            # 基本信息字段
            'primary_culture': '主要文化',
            'religion': '国教',
            'government': '政府类型',
            'plurality': '多元化程度',
            'civilized': '文明化状态',
            'capital': '首都省份ID',
            'prestige': '威望',
            'money': '国库资金',
            'badboy': '恶名度',
            'consciousness': '觉醒度',
            'literacy': '识字率',
            'ruling_party': '执政党',
            'last_election': '上次选举',
            'upper_house': '上议院',
            'lower_house': '下议院',
            'technology': '科技',
            'leadership': '领导力',
            'research_points': '研究点数',
            'war_exhaustion': '战争疲惫',
            'mobilized': '动员状态',
            'nationalvalue': '国家价值观',
            'non_state_culture_literacy': '非国家文化识字率',
            'tax_eff': '税收效率',
            'bank': '银行资金',
            'colonial_points': '殖民点数',
            'diplomatic_points': '外交点数',
            'suppression': '镇压点数',
        }
    
    def analyze_file(self, filename: str):
        """分析文件中的国家块"""
        print(f"🚀 快速分析文件: {filename}")
        
        # 读取文件
        try:
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(filename, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    print(f"✅ 文件读取成功 (编码: {encoding})，大小: {len(content):,} 字符")
                    break
                except UnicodeDecodeError:
                    continue
        except Exception as e:
            print(f"❌ 文件读取失败: {e}")
            return
        
        # 查找所有国家块
        country_blocks = self._find_country_blocks(content)
        
        if not country_blocks:
            print("❌ 未找到国家块")
            return
        
        print(f"✅ 找到 {len(country_blocks)} 个国家块")
        
        # 分析字段
        field_stats = self._analyze_fields(country_blocks)
        
        # 生成报告
        self._generate_report(field_stats, len(country_blocks))
    
    def _find_country_blocks(self, content: str) -> dict:
        """查找所有国家块"""
        print("🔍 查找国家块...")
        
        # 查找所有3字母标签的块
        pattern = r'([A-Z]{3})\s*=\s*\{'
        matches = list(re.finditer(pattern, content))
        
        country_blocks = {}
        
        for match in matches:
            tag = match.group(1)
            start_pos = match.end() - 1  # 指向开始的 {
            
            # 找到匹配的结束花括号
            end_pos = self._find_matching_brace(content, start_pos)
            
            if end_pos != -1:
                block_content = content[start_pos + 1:end_pos]
                
                # 判断是否为国家定义块（而非外交关系块）
                if self._is_country_definition(block_content):
                    country_blocks[tag] = block_content
        
        return country_blocks
    
    def _find_matching_brace(self, content: str, start_pos: int) -> int:
        """找到匹配的结束花括号"""
        if start_pos >= len(content) or content[start_pos] != '{':
            return -1
        
        brace_count = 1
        pos = start_pos + 1
        
        while pos < len(content) and brace_count > 0:
            char = content[pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            pos += 1
        
        return pos - 1 if brace_count == 0 else -1
    
    def _is_country_definition(self, block_content: str) -> bool:
        """判断是否为国家定义块"""
        # 国家定义块应该包含这些字段中的多个
        indicators = ['primary_culture', 'capital', 'government', 'technology', 
                     'money', 'prestige', 'consciousness', 'literacy']
        
        count = sum(1 for indicator in indicators if indicator in block_content)
        return count >= 3  # 至少包含3个指标
    
    def _analyze_fields(self, country_blocks: dict) -> dict:
        """分析字段统计"""
        print("📊 分析字段统计...")
        
        field_stats = defaultdict(lambda: {
            'count': 0,
            'countries': set(),
            'values': Counter(),
            'numeric_values': [],
            'examples': []
        })
        
        for country_tag, block_content in country_blocks.items():
            # 提取简单字段 (key=value)
            simple_pattern = r'(\w+)\s*=\s*([^{}\n]+?)(?=\n|\s|$)'
            matches = re.findall(simple_pattern, block_content, re.MULTILINE)
            
            for field_name, value in matches:
                field_name = field_name.strip()
                value = value.strip().strip('"')
                
                if field_name and value:
                    stats = field_stats[field_name]
                    stats['count'] += 1
                    stats['countries'].add(country_tag)
                    stats['values'][value] += 1
                    
                    # 示例值
                    if len(stats['examples']) < 5:
                        stats['examples'].append(f"{country_tag}={value}")
                    
                    # 数值统计
                    try:
                        numeric_val = float(value)
                        stats['numeric_values'].append(numeric_val)
                    except:
                        pass
            
            # 提取块字段 (key={...})
            block_pattern = r'(\w+)\s*=\s*\{'
            block_matches = re.findall(block_pattern, block_content)
            
            for field_name in block_matches:
                field_name = field_name.strip()
                if field_name:
                    stats = field_stats[field_name]
                    stats['count'] += 1
                    stats['countries'].add(country_tag)
                    stats['values']['<block>'] += 1
                    
                    if len(stats['examples']) < 5:
                        stats['examples'].append(f"{country_tag}=<block>")
        
        return dict(field_stats)
    
    def _generate_report(self, field_stats: dict, total_countries: int):
        """生成分析报告"""
        print("\n" + "=" * 80)
        print("🏛️  Victoria II 国家块字段分析报告")
        print("=" * 80)
        print(f"总国家数: {total_countries}")
        print(f"总字段数: {len(field_stats)}")
        
        # 按覆盖率排序
        sorted_fields = sorted(
            field_stats.items(),
            key=lambda x: len(x[1]['countries']),
            reverse=True
        )
        
        print(f"\n📊 字段覆盖率统计 (前20个):")
        print("-" * 80)
        print(f"{'字段名':<25} {'覆盖率':<10} {'出现次数':<10} {'描述'}")
        print("-" * 80)
        
        for i, (field_name, stats) in enumerate(sorted_fields[:20]):
            coverage = len(stats['countries']) / total_countries * 100
            description = self.country_fields.get(field_name, '未知字段')
            print(f"{field_name:<25} {coverage:>6.1f}%    {stats['count']:>6}    {description}")
        
        print(f"\n🔢 数值字段统计:")
        print("-" * 80)
        
        numeric_fields = []
        for field_name, stats in field_stats.items():
            if stats['numeric_values']:
                values = stats['numeric_values']
                numeric_fields.append({
                    'name': field_name,
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values)
                })
        
        # 按数值字段数量排序
        numeric_fields.sort(key=lambda x: x['count'], reverse=True)
        
        print(f"{'字段名':<20} {'数量':<8} {'最小值':<12} {'最大值':<12} {'平均值':<12}")
        print("-" * 80)
        
        for field in numeric_fields[:15]:
            print(f"{field['name']:<20} {field['count']:>6}   "
                  f"{field['min']:>10.3f}   {field['max']:>10.3f}   {field['avg']:>10.3f}")
        
        print(f"\n📝 常见字段值示例:")
        print("-" * 80)
        
        for field_name, stats in sorted_fields[:10]:
            if stats['examples']:
                print(f"\n{field_name} ({self.country_fields.get(field_name, '未知')}):")
                for example in stats['examples'][:3]:
                    print(f"  • {example}")
                
                # 显示最常见的值
                if stats['values'] and '<block>' not in str(stats['values'].most_common(1)[0][0]):
                    common_vals = [f"{val}({count})" for val, count in stats['values'].most_common(3)]
                    print(f"  常见值: {', '.join(common_vals)}")
        
        print("\n" + "=" * 80)

def main():
    """主函数"""
    analyzer = FastCountryAnalyzer()
    analyzer.analyze_file('autosave.v2')

if __name__ == "__main__":
    main()
