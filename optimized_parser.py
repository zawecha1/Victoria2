#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的Victoria II存档解析器
专注于性能和稳定性
"""

import re
import json
from typing import Dict, List, Any, Union
from dataclasses import dataclass, field


@dataclass
class GameData:
    """游戏存档主数据"""
    date: str = ""
    player: str = ""
    government: int = 0
    automate_trade: bool = False
    automate_sliders: int = 0
    rebel: int = 0
    unit: int = 0
    state: int = 0
    start_date: str = ""
    start_pop_index: int = 0
    flags: List[str] = field(default_factory=list)
    countries: Dict[str, Dict] = field(default_factory=dict)
    provinces: Dict[str, Dict] = field(default_factory=dict)
    worldmarket: Dict[str, Any] = field(default_factory=dict)


class OptimizedVictoria2Parser:
    """优化的Victoria II存档解析器"""
    
    def __init__(self):
        self.content = ""
        # 预编译正则表达式以提高性能
        self.date_pattern = re.compile(r'^\d{3,4}\.\d{1,2}\.\d{1,2}$')
        self.number_pattern = re.compile(r'^-?\d+\.?\d*$')
        self.country_pattern = re.compile(r'^([A-Z]{3})=\s*{', re.MULTILINE)
        
    def parse_file(self, filename: str) -> GameData:
        """解析存档文件"""
        print(f"开始解析文件: {filename}")
        
        # 读取文件
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                self.content = f.read()
        except Exception as e:
            print(f"文件读取错误: {e}")
            return GameData()
        
        print(f"文件大小: {len(self.content):,} 字符")
        
        # 创建游戏数据对象
        game_data = GameData()
        
        # 提取基本信息
        print("提取基本信息...")
        self._extract_basic_info(game_data)
        
        # 提取标志
        print("提取游戏标志...")
        self._extract_flags(game_data)
        
        # 提取国家信息（解析所有国家）
        print("提取国家信息...")
        self._extract_countries(game_data, limit=None)
        
        # 提取省份信息（样本）
        print("提取省份样本...")
        self._extract_provinces_sample(game_data, limit=10)
        
        # 提取世界市场信息
        print("提取世界市场信息...")
        self._extract_worldmarket(game_data)
        
        print("解析完成!")
        return game_data
    
    def _extract_basic_info(self, game_data: GameData):
        """提取基本游戏信息"""
        patterns = {
            'date': r'date="([^"]+)"',
            'player': r'player="([^"]+)"',
            'government': r'government=(\d+)',
            'automate_trade': r'automate_trade=(\w+)',
            'automate_sliders': r'automate_sliders=(\d+)',
            'rebel': r'rebel=(\d+)',
            'unit': r'unit=(\d+)',
            'state': r'state=(\d+)',
            'start_date': r'start_date="([^"]+)"',
            'start_pop_index': r'start_pop_index=(\d+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, self.content)
            if match:
                value = match.group(1)
                
                # 类型转换
                if key in ['government', 'automate_sliders', 'rebel', 'unit', 'state', 'start_pop_index']:
                    setattr(game_data, key, int(value))
                elif key == 'automate_trade':
                    setattr(game_data, key, value == 'yes')
                else:
                    setattr(game_data, key, value)
    
    def _extract_flags(self, game_data: GameData):
        """提取游戏标志"""
        # 查找第一个flags块
        flag_match = re.search(r'flags=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', self.content, re.DOTALL)
        if flag_match:
            flag_content = flag_match.group(1)
            # 提取所有 name=yes 格式的标志
            flags = re.findall(r'(\w+)=yes', flag_content)
            game_data.flags = flags
    
    def _extract_countries(self, game_data: GameData, limit: int = None):
        """提取国家信息"""
        matches = list(self.country_pattern.finditer(self.content))
        print(f"找到 {len(matches)} 个国家")
        
        # 如果没有限制，处理所有国家
        if limit is None:
            limit = len(matches)
        
        for i, match in enumerate(matches[:limit]):
            if i >= limit:
                break
                
            tag = match.group(1)
            start_pos = match.end()
            
            # 找到对应的结束位置（简化版本，适用于大多数情况）
            end_pos = self.content.find('\n}', start_pos)
            if end_pos == -1:
                continue
                
            country_content = self.content[start_pos:end_pos]
            country_info = self._parse_country_info(country_content)
            if country_info:
                game_data.countries[tag] = country_info
            
            # 显示进度
            if (i + 1) % 50 == 0:
                print(f"已处理 {i + 1}/{len(matches)} 个国家...")
    
    def _parse_country_info(self, content: str) -> Dict:
        """解析国家信息"""
        info = {}
        
        # 提取数值信息
        patterns = {
            'tax_base': r'tax_base=([\d.]+)',
            'capital': r'capital=(\d+)',
            'research_points': r'research_points=([\d.]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1)
                try:
                    if '.' in value:
                        info[key] = float(value)
                    else:
                        info[key] = int(value)
                except ValueError:
                    pass
        
        # 计算科技和标志数量
        info['technology_count'] = len(re.findall(r'\w+={1 0\.000}', content))
        info['flag_count'] = len(re.findall(r'\w+=yes', content))
        
        return info
    
    def _extract_provinces_sample(self, game_data: GameData, limit: int = 10):
        """提取省份样本"""
        # 查找省份模式 (数字ID)
        province_pattern = re.compile(r'^(\d+)=\s*\{', re.MULTILINE)
        matches = list(province_pattern.finditer(self.content))
        
        provinces = {}
        
        for i, match in enumerate(matches[:limit]):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 找到下一个省份或结束位置
            next_match = matches[i + 1] if i + 1 < len(matches) else None
            if next_match:
                end_pos = next_match.start()
            else:
                end_pos = start_pos + 10000  # 限制搜索范围
                
            province_content = self.content[start_pos:end_pos]
            province_info = self._parse_province_info(province_content)
            province_info['id'] = province_id
            provinces[str(province_id)] = province_info
        
        game_data.provinces = {
            'total_provinces': len(matches),
            'sample_provinces': list(provinces.values())
        }
    
    def _parse_province_info(self, content: str) -> Dict:
        """解析省份信息"""
        info = {}
        
        # 提取基本信息
        patterns = {
            'name': r'name="([^"]+)"',
            'owner': r'owner="([^"]+)"',
            'controller': r'controller="([^"]+)"'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                info[key] = match.group(1)
        
        return info
    
    def _extract_worldmarket(self, game_data: GameData):
        """提取世界市场信息"""
        wm_match = re.search(r'worldmarket=\s*\{', self.content)
        if not wm_match:
            return
        
        start_pos = wm_match.end()
        # 查找世界市场块的结束（简化处理）
        end_pos = self.content.find('\noverseas_penalty=', start_pos)
        if end_pos == -1:
            end_pos = start_pos + 50000  # 限制搜索范围
        
        wm_content = self.content[start_pos:end_pos]
        
        # 提取各个池的商品数量
        pools = ['worldmarket_pool', 'price_pool', 'supply_pool']
        wm_info = {}
        
        for pool_name in pools:
            pool_match = re.search(f'{pool_name}=\\s*\\{{([^}}]+)\\}}', wm_content)
            if pool_match:
                pool_content = pool_match.group(1)
                commodities = re.findall(r'(\w+)=([\d.]+)', pool_content)
                wm_info[f'{pool_name}_commodities'] = len(commodities)
                wm_info[f'{pool_name}_sample'] = dict(commodities[:5])
        
        game_data.worldmarket = wm_info
    
    def save_to_json(self, game_data: GameData, output_file: str):
        """保存到JSON文件"""
        def default_serializer(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        print(f"保存数据到 {output_file}")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, default=default_serializer, indent=2, ensure_ascii=False)
            print("保存完成!")
        except Exception as e:
            print(f"保存失败: {e}")
    
    def print_summary(self, game_data: GameData):
        """打印摘要"""
        print("\n" + "="*60)
        print("Victoria II 存档解析摘要")
        print("="*60)
        
        print(f"📅 游戏日期: {game_data.date}")
        print(f"🎮 玩家: {game_data.player}")
        print(f"🏛️  政府类型: {game_data.government}")
        print(f"📊 开始日期: {game_data.start_date}")
        print(f"🚩 游戏标志: {len(game_data.flags)}")
        print(f"🌍 国家数量: {len(game_data.countries)}")
        
        if 'total_provinces' in game_data.provinces:
            print(f"🗺️  省份总数: {game_data.provinces['total_provinces']}")
        
        # 显示所有国家信息
        if game_data.countries:
            print(f"\n" + "="*80)
            print("📈 所有国家详细信息")
            print("="*80)
            
            # 按研究点数排序
            sorted_countries = sorted(
                game_data.countries.items(),
                key=lambda x: x[1].get('research_points', 0),
                reverse=True
            )
            
            print(f"{'排名':<4} {'国家':<4} {'研究点数':<12} {'税收基础':<12} {'首都ID':<8} {'科技数':<8} {'标志数':<8}")
            print("-" * 80)
            
            for i, (tag, info) in enumerate(sorted_countries, 1):
                tax = info.get('tax_base', 0)
                research = info.get('research_points', 0)
                capital = info.get('capital', 0)
                tech_count = info.get('technology_count', 0)
                flag_count = info.get('flag_count', 0)
                
                print(f"{i:<4} {tag:<4} {research:<12.1f} {tax:<12.1f} {capital:<8} {tech_count:<8} {flag_count:<8}")
        
        print("\n" + "="*60)


def main():
    """主函数"""
    print("优化版 Victoria II 存档解析器")
    print("="*50)
    
    # 文件路径
    input_file = "China2245_04_06.v2"
    
    if not input_file:
        print("错误: 找不到存档文件")
        return
    
    # 创建解析器
    parser = OptimizedVictoria2Parser()
    
    try:
        # 解析文件
        game_data = parser.parse_file(input_file)
        
        # 显示摘要
        parser.print_summary(game_data)
        
        # 保存结果
        output_file = "china_optimized_parsed.json"
        parser.save_to_json(game_data, output_file)
        
        print(f"\n✅ 解析完成! 结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 解析错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
