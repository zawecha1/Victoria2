#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 存档数据分析工具
基于解析后的JSON数据进行深度分析
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime


class Victoria2Analyzer:
    """Victoria II存档数据分析器"""
    
    def __init__(self, json_file: str):
        self.data = None
        self.load_json(json_file)
    
    def load_json(self, json_file: str):
        """加载JSON数据"""
        if not os.path.exists(json_file):
            print(f"错误: 找不到文件 {json_file}")
            return False
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"成功加载数据文件: {json_file}")
            return True
        except Exception as e:
            print(f"加载JSON文件失败: {e}")
            return False
    
    def analyze_basic_stats(self):
        """分析基本统计信息"""
        if not self.data:
            return
        
        print("\n" + "="*60)
        print("基本统计分析")
        print("="*60)
        
        basic = self.data.get('basic_info', {})
        
        print(f"📅 游戏时间: {basic.get('date', 'Unknown')}")
        print(f"🎮 玩家国家: {basic.get('player', 'Unknown')}")
        print(f"🏛️  政府类型代码: {basic.get('government', 'Unknown')}")
        print(f"📊 总标志数: {self.data.get('flag_count', 0)}")
        print(f"🌍 总国家数: {self.data.get('country_count', 0)}")
        print(f"🗺️  总省份数: {self.data.get('provinces', {}).get('total_provinces', 0)}")
        
        # 计算游戏进行时间
        start_date = basic.get('start_date', '1836.1.1')
        current_date = basic.get('date', '1836.1.1')
        if start_date and current_date:
            try:
                start_year = int(start_date.split('.')[0])
                current_year = int(current_date.split('.')[0])
                game_years = current_year - start_year
                print(f"⏱️  游戏进行年数: {game_years} 年")
            except:
                pass
    
    def analyze_countries(self):
        """分析国家数据"""
        if not self.data or 'countries' not in self.data:
            return
        
        print("\n" + "="*60)
        print("国家经济分析")
        print("="*60)
        
        countries = self.data['countries']
        
        # 按税收基础排序
        tax_ranking = []
        research_ranking = []
        
        for tag, info in countries.items():
            tax_base = info.get('tax_base', 0)
            research_points = info.get('research_points', 0)
            
            if tax_base > 0:
                tax_ranking.append((tag, tax_base))
            if research_points > 0:
                research_ranking.append((tag, research_points))
        
        # 税收排名
        tax_ranking.sort(key=lambda x: x[1], reverse=True)
        print("\n💰 税收基础排行榜 (前10名):")
        for i, (tag, tax) in enumerate(tax_ranking[:10], 1):
            flag_count = countries[tag].get('flag_count', 0)
            tech_count = countries[tag].get('tech_count', 0)
            print(f"{i:2d}. {tag}: {tax:>10.2f} (标志:{flag_count}, 科技:{tech_count})")
        
        # 研究点数排名
        research_ranking.sort(key=lambda x: x[1], reverse=True)
        print("\n🔬 研究点数排行榜 (前10名):")
        for i, (tag, research) in enumerate(research_ranking[:10], 1):
            tax_base = countries[tag].get('tax_base', 0)
            print(f"{i:2d}. {tag}: {research:>10.2f} (税收基础:{tax_base:.2f})")
        
        # 统计分析
        if tax_ranking:
            total_tax = sum(tax for _, tax in tax_ranking)
            avg_tax = total_tax / len(tax_ranking)
            print(f"\n📈 税收统计:")
            print(f"   总税收: {total_tax:.2f}")
            print(f"   平均税收: {avg_tax:.2f}")
            print(f"   最高税收: {tax_ranking[0][1]:.2f} ({tax_ranking[0][0]})")
            
            # 计算税收集中度
            top_5_tax = sum(tax for _, tax in tax_ranking[:5])
            concentration = (top_5_tax / total_tax) * 100 if total_tax > 0 else 0
            print(f"   前5名税收占比: {concentration:.1f}%")
    
    def analyze_worldmarket(self):
        """分析世界市场"""
        if not self.data or 'worldmarket' not in self.data:
            return
        
        print("\n" + "="*60)
        print("世界市场分析")
        print("="*60)
        
        wm = self.data['worldmarket']
        
        # 分析各个商品池
        pools = {
            'worldmarket_pool': '世界市场库存',
            'price_pool': '商品价格',
            'supply_pool': '供应池'
        }
        
        for pool_name, pool_desc in pools.items():
            sample_key = f'{pool_name}_sample'
            if sample_key in wm:
                print(f"\n📦 {pool_desc}示例:")
                sample_data = wm[sample_key]
                
                # 按值排序
                sorted_items = sorted(sample_data.items(), key=lambda x: x[1], reverse=True)
                
                for commodity, value in sorted_items:
                    try:
                        print(f"   {commodity:<20}: {float(value):>10.2f}")
                    except (ValueError, TypeError):
                        print(f"   {commodity:<20}: {str(value):>10}")
                
                # 统计
                commodity_count = wm.get(f'{pool_name}_commodities', 0)
                print(f"   总商品种类: {commodity_count}")
    
    def analyze_provinces(self):
        """分析省份数据"""
        if not self.data or 'provinces' not in self.data:
            return
        
        print("\n" + "="*60)
        print("省份分析")
        print("="*60)
        
        prov_info = self.data['provinces']
        sample_provinces = prov_info.get('sample_provinces', [])
        
        if not sample_provinces:
            print("没有省份样本数据")
            return
        
        print(f"📊 省份总数: {prov_info.get('total_provinces', 0)}")
        print(f"🔍 样本省份数: {len(sample_provinces)}")
        
        # 统计拥有者
        owners = Counter()
        controllers = Counter()
        
        for prov in sample_provinces:
            owners[prov.get('owner', 'Unknown')] += 1
            controllers[prov.get('controller', 'Unknown')] += 1
        
        print(f"\n🏴 省份拥有者分布 (样本):")
        for owner, count in owners.most_common():
            print(f"   {owner}: {count} 个省份")
        
        print(f"\n⚔️ 省份控制者分布 (样本):")
        for controller, count in controllers.most_common():
            print(f"   {controller}: {count} 个省份")
        
        # 显示详细省份信息
        print(f"\n🗺️  详细省份信息:")
        for prov in sample_provinces:
            name = prov.get('name', 'Unknown')
            owner = prov.get('owner', 'Unknown')
            controller = prov.get('controller', 'Unknown')
            province_id = prov.get('id', 'Unknown')
            
            status = "正常" if owner == controller else "被占领"
            print(f"   ID {province_id:3}: {name:<20} | {owner} -> {controller} | {status}")
    
    def analyze_flags(self):
        """分析游戏标志"""
        if not self.data or 'flags' not in self.data:
            return
        
        print("\n" + "="*60)
        print("游戏标志分析")
        print("="*60)
        
        flags = self.data.get('flags', [])
        print(f"🚩 总标志数: {len(flags)}")
        
        # 分类分析标志
        categories = defaultdict(list)
        
        for flag in flags:
            flag_name = flag if isinstance(flag, str) else flag.get('name', '')
            
            # 简单的标志分类
            if 'nobel' in flag_name.lower():
                categories['诺贝尔奖'].append(flag_name)
            elif 'olympiad' in flag_name.lower():
                categories['奥运会'].append(flag_name)
            elif any(word in flag_name.lower() for word in ['war', 'revolution', 'rebellion']):
                categories['战争/革命'].append(flag_name)
            elif any(word in flag_name.lower() for word in ['canal', 'railway', 'build']):
                categories['建设工程'].append(flag_name)
            elif any(word in flag_name.lower() for word in ['discover', 'found', 'expedition']):
                categories['探索发现'].append(flag_name)
            else:
                categories['其他'].append(flag_name)
        
        print("\n📋 标志分类:")
        for category, flag_list in categories.items():
            print(f"\n   {category} ({len(flag_list)}个):")
            for flag in flag_list[:10]:  # 只显示前10个
                print(f"     • {flag}")
            if len(flag_list) > 10:
                print(f"     ... 还有{len(flag_list) - 10}个")
    
    def generate_full_report(self):
        """生成完整分析报告"""
        if not self.data:
            print("没有数据可供分析")
            return
        
        print("Victoria II 存档深度分析报告")
        print("="*80)
        
        # 执行所有分析
        self.analyze_basic_stats()
        self.analyze_countries()
        self.analyze_worldmarket()
        self.analyze_provinces()
        self.analyze_flags()
        
        print("\n" + "="*80)
        print("分析报告完成")
        print("="*80)
    
    def save_analysis_report(self, output_file: str):
        """保存分析报告到文件"""
        import sys
        from io import StringIO
        
        # 重定向输出到字符串
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            self.generate_full_report()
            report_content = captured_output.getvalue()
        finally:
            sys.stdout = old_stdout
        
        # 保存到文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"分析报告已保存到: {output_file}")
        except Exception as e:
            print(f"保存报告失败: {e}")


def main():
    """主函数"""
    print("Victoria II 存档数据分析工具")
    print("="*50)
    
    # 查找JSON文件
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    if not json_files:
        print("错误: 当前目录下没有找到JSON文件")
        print("请先运行解析器生成JSON数据文件")
        return
    
    print(f"找到 {len(json_files)} 个JSON文件:")
    for i, filename in enumerate(json_files, 1):
        print(f"{i}. {filename}")
    
    # 选择文件
    if len(json_files) == 1:
        selected_file = json_files[0]
        print(f"\n自动选择: {selected_file}")
    else:
        try:
            choice = int(input(f"\n请选择要分析的文件 (1-{len(json_files)}): ")) - 1
            if 0 <= choice < len(json_files):
                selected_file = json_files[choice]
            else:
                print("无效选择")
                return
        except ValueError:
            print("无效输入")
            return
    
    # 创建分析器并运行分析
    analyzer = Victoria2Analyzer(selected_file)
    
    if analyzer.data:
        print(f"\n开始分析 {selected_file}...")
        analyzer.generate_full_report()
        
        # 询问是否保存报告
        save_report = input("\n是否保存分析报告到文件? (y/n): ").lower()
        if save_report in ['y', 'yes', '是']:
            report_file = selected_file.replace('.json', '_analysis_report.txt')
            analyzer.save_analysis_report(report_file)


if __name__ == "__main__":
    main()
