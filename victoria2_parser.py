#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 存档文件解析器
解析 .v2 存档文件格式并转换为Python对象
"""

import re
import json
from typing import Dict, List, Any, Union, Optional
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class Flag:
    """游戏标志"""
    name: str
    value: Union[bool, str, int, float] = True


@dataclass
class Technology:
    """科技数据"""
    name: str
    level: int
    progress: float


@dataclass
class PopGroup:
    """人口群体数据"""
    id: int
    size: int
    type: str  # aristocrats, clerks, etc.
    culture: Optional[str] = None
    religion: Optional[str] = None
    money: float = 0.0
    ideology: Dict[int, float] = field(default_factory=dict)
    issues: Dict[int, float] = field(default_factory=dict)
    con: float = 0.0
    mil: float = 0.0
    literacy: float = 0.0
    life_needs: float = 0.0
    everyday_needs: float = 0.0
    luxury_needs: float = 0.0


@dataclass
class Building:
    """建筑数据"""
    type: str
    level: float


@dataclass
class Modifier:
    """省份修正"""
    modifier: str
    date: str


@dataclass
class Province:
    """省份数据"""
    id: int
    name: str
    owner: str
    controller: str
    cores: List[str] = field(default_factory=list)
    garrison: float = 0.0
    buildings: Dict[str, Building] = field(default_factory=dict)
    modifiers: List[Modifier] = field(default_factory=list)
    pops: List[PopGroup] = field(default_factory=list)


@dataclass
class Country:
    """国家数据"""
    tag: str
    tax_base: float = 0.0
    capital: Optional[int] = None
    research_points: float = 0.0
    flags: List[Flag] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    technologies: List[Technology] = field(default_factory=list)
    provinces: List[int] = field(default_factory=list)


@dataclass
class WorldMarket:
    """世界市场数据"""
    worldmarket_pool: Dict[str, float] = field(default_factory=dict)
    price_pool: Dict[str, float] = field(default_factory=dict)
    last_price_history: Dict[str, float] = field(default_factory=dict)
    supply_pool: Dict[str, float] = field(default_factory=dict)
    last_supply_pool: Dict[str, float] = field(default_factory=dict)


@dataclass
class GameData:
    """游戏存档主数据"""
    date: str
    player: str
    government: int
    automate_trade: bool
    automate_sliders: int
    rebel: int
    unit: int
    state: int
    start_date: str
    start_pop_index: int
    flags: List[Flag] = field(default_factory=list)
    worldmarket: Optional[WorldMarket] = None
    countries: Dict[str, Country] = field(default_factory=dict)
    provinces: Dict[int, Province] = field(default_factory=dict)


class Victoria2Parser:
    """Victoria II 存档文件解析器"""
    
    def __init__(self):
        self.data = None
        self.current_line = 0
        self.lines = []
    
    def parse_file(self, filename: str) -> GameData:
        """解析存档文件"""
        print(f"开始解析文件: {filename}")
        
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        # 分割行并清理
        self.lines = [line.strip() for line in content.split('\n')]
        self.current_line = 0
        
        # 创建主游戏数据对象
        game_data = GameData(
            date="", player="", government=0, automate_trade=False,
            automate_sliders=0, rebel=0, unit=0, state=0, start_date="", start_pop_index=0
        )
        
        # 解析顶级数据
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]
            
            if not line or line.startswith('#'):
                self.current_line += 1
                continue
            
            # 解析键值对
            if '=' in line and not line.endswith('='):
                key, value = self._parse_key_value(line)
                self._set_game_data_field(game_data, key, value)
            
            # 解析复杂块
            elif line.endswith('='):
                key = line[:-1]
                self.current_line += 1
                block_data = self._parse_block()
                
                if key == 'flags':
                    game_data.flags = self._parse_flags(block_data)
                elif key == 'worldmarket':
                    game_data.worldmarket = self._parse_worldmarket(block_data)
                elif key in ['REB', 'ENG', 'FRA', 'RUS', 'PRU', 'GER', 'AUS', 'CHI', 'USA', 'JAP']:
                    # 国家数据
                    country = self._parse_country(key, block_data)
                    game_data.countries[key] = country
                elif key.isdigit():
                    # 省份数据
                    province_id = int(key)
                    province = self._parse_province(province_id, block_data)
                    game_data.provinces[province_id] = province
            else:
                self.current_line += 1
        
        print(f"解析完成! 找到 {len(game_data.countries)} 个国家, {len(game_data.provinces)} 个省份")
        return game_data
    
    def _parse_key_value(self, line: str) -> tuple:
        """解析键值对"""
        if '=' not in line:
            return None, None
        
        key, value = line.split('=', 1)
        key = key.strip().strip('"')
        value = value.strip().strip('"')
        
        # 转换值类型
        if value.lower() == 'yes':
            value = True
        elif value.lower() == 'no':
            value = False
        elif self._is_numeric(value):
            if '.' in value and not self._is_date_format(value):
                value = float(value)
            elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                value = int(value)
        # 其他情况保持字符串格式（包括日期）
        
        return key, value
    
    def _is_numeric(self, value: str) -> bool:
        """检查字符串是否为数字"""
        try:
            float(value)
            return not self._is_date_format(value)  # 排除日期格式
        except ValueError:
            return False
    
    def _is_date_format(self, value: str) -> bool:
        """检查是否为日期格式 (如 2245.4.6)"""
        parts = value.split('.')
        if len(parts) == 3:
            try:
                # 检查是否为年.月.日格式
                year, month, day = parts
                return (len(year) >= 3 and year.isdigit() and 
                        len(month) <= 2 and month.isdigit() and
                        len(day) <= 2 and day.isdigit())
            except:
                return False
        return False
    
    def _parse_block(self) -> Dict[str, Any]:
        """解析代码块"""
        if self.current_line >= len(self.lines) or self.lines[self.current_line] != '{':
            return {}
        
        self.current_line += 1  # 跳过 '{'
        block_data = {}
        
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]
            
            if line == '}':
                self.current_line += 1
                break
            
            if not line or line.startswith('#'):
                self.current_line += 1
                continue
            
            # 简单键值对
            if '=' in line and not line.endswith('='):
                key, value = self._parse_key_value(line)
                if key:
                    if key in block_data:
                        # 如果键已存在，转换为列表
                        if not isinstance(block_data[key], list):
                            block_data[key] = [block_data[key]]
                        block_data[key].append(value)
                    else:
                        block_data[key] = value
            
            # 嵌套块
            elif line.endswith('='):
                key = line[:-1].strip()
                self.current_line += 1
                nested_block = self._parse_block()
                if key in block_data:
                    if not isinstance(block_data[key], list):
                        block_data[key] = [block_data[key]]
                    block_data[key].append(nested_block)
                else:
                    block_data[key] = nested_block
            
            # 列表项
            else:
                if 'items' not in block_data:
                    block_data['items'] = []
                block_data['items'].append(line)
            
            self.current_line += 1
        
        return block_data
    
    def _set_game_data_field(self, game_data: GameData, key: str, value: Any):
        """设置游戏数据字段"""
        if hasattr(game_data, key):
            setattr(game_data, key, value)
    
    def _parse_flags(self, block_data: Dict) -> List[Flag]:
        """解析标志"""
        flags = []
        for key, value in block_data.items():
            if key != 'items':
                flags.append(Flag(name=key, value=value))
        return flags
    
    def _parse_worldmarket(self, block_data: Dict) -> WorldMarket:
        """解析世界市场"""
        worldmarket = WorldMarket()
        
        for key, value in block_data.items():
            if isinstance(value, dict):
                if key == 'worldmarket_pool':
                    worldmarket.worldmarket_pool = value
                elif key == 'price_pool':
                    worldmarket.price_pool = value
                elif key == 'last_price_history':
                    worldmarket.last_price_history = value
                elif key == 'supply_pool':
                    worldmarket.supply_pool = value
                elif key == 'last_supply_pool':
                    worldmarket.last_supply_pool = value
        
        return worldmarket
    
    def _parse_country(self, tag: str, block_data: Dict) -> Country:
        """解析国家数据"""
        country = Country(tag=tag)
        
        for key, value in block_data.items():
            if key == 'tax_base':
                country.tax_base = float(value)
            elif key == 'capital':
                country.capital = int(value)
            elif key == 'research_points':
                country.research_points = float(value)
            elif key == 'flags' and isinstance(value, dict):
                country.flags = self._parse_flags(value)
            elif key == 'variables' and isinstance(value, dict):
                country.variables = value
            elif key == 'technology' and isinstance(value, dict):
                country.technologies = self._parse_technologies(value)
        
        return country
    
    def _parse_technologies(self, tech_data: Dict) -> List[Technology]:
        """解析科技数据"""
        technologies = []
        for tech_name, tech_info in tech_data.items():
            if isinstance(tech_info, dict) and '1' in tech_info:
                level = 1 if tech_info['1'] else 0
                progress = float(tech_info.get('0.000', 0.0))
                technologies.append(Technology(name=tech_name, level=level, progress=progress))
        return technologies
    
    def _parse_province(self, province_id: int, block_data: Dict) -> Province:
        """解析省份数据"""
        province = Province(id=province_id, name="", owner="", controller="")
        
        for key, value in block_data.items():
            if key == 'name':
                province.name = str(value)
            elif key == 'owner':
                province.owner = str(value)
            elif key == 'controller':
                province.controller = str(value)
            elif key == 'core':
                if isinstance(value, list):
                    province.cores = value
                else:
                    province.cores = [value]
            elif key == 'garrison':
                province.garrison = float(value)
            elif key in ['fort', 'naval_base', 'railroad'] and isinstance(value, dict):
                # 建筑数据，通常包含多个级别
                if 'items' in value and value['items']:
                    levels = [float(x) for x in value['items'] if x.replace('.', '').isdigit()]
                    if levels:
                        province.buildings[key] = Building(type=key, level=max(levels))
            elif key == 'modifier' and isinstance(value, (list, dict)):
                # 修正数据
                modifiers = value if isinstance(value, list) else [value]
                for mod in modifiers:
                    if isinstance(mod, dict) and 'modifier' in mod:
                        province.modifiers.append(Modifier(
                            modifier=mod['modifier'],
                            date=mod.get('date', '')
                        ))
        
        return province
    
    def save_to_json(self, game_data: GameData, output_file: str):
        """保存数据到JSON文件"""
        
        def default_serializer(obj):
            """自定义JSON序列化器"""
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        print(f"保存数据到 {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, default=default_serializer, indent=2, ensure_ascii=False)
        print("保存完成!")
    
    def print_summary(self, game_data: GameData):
        """打印游戏数据摘要"""
        print("\n=== Victoria II 存档数据摘要 ===")
        print(f"游戏日期: {game_data.date}")
        print(f"玩家国家: {game_data.player}")
        print(f"政府类型: {game_data.government}")
        print(f"开始日期: {game_data.start_date}")
        print(f"总标志数: {len(game_data.flags)}")
        print(f"总国家数: {len(game_data.countries)}")
        print(f"总省份数: {len(game_data.provinces)}")
        
        if game_data.worldmarket:
            print(f"世界市场商品种类: {len(game_data.worldmarket.worldmarket_pool)}")
        
        # 显示部分国家信息
        print("\n主要国家:")
        for tag, country in list(game_data.countries.items())[:10]:
            print(f"  {tag}: 税收基础={country.tax_base:.2f}, 研究点数={country.research_points:.2f}")
        
        # 显示部分省份信息
        print("\n部分省份:")
        for pid, province in list(game_data.provinces.items())[:5]:
            print(f"  {pid} ({province.name}): 拥有者={province.owner}, 控制者={province.controller}")


def main():
    """主函数"""
    # 使用示例
    parser = Victoria2Parser()
    
    # 解析存档文件
    input_file = r"c:\Users\zhangwc6\Documents\Paradox Interactive\Victoria II\save games\China2245_04_06.v2"
    
    try:
        game_data = parser.parse_file(input_file)
        
        # 显示摘要
        parser.print_summary(game_data)
        
        # 保存为JSON
        output_file = input_file.replace('.v2', '_parsed.json')
        parser.save_to_json(game_data, output_file)
        
        return game_data
        
    except Exception as e:
        print(f"解析错误: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
