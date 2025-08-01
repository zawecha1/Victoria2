#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Victoria II存档解析器
适用于基本的数据提取和分析
"""

import re
import json
from typing import Dict, List, Any, Union


class SimpleVictoria2Parser:
    """简化的Victoria II存档解析器"""
    
    def __init__(self):
        self.content = ""
        self.lines = []
    
    def load_file(self, filename: str):
        """加载存档文件"""
        print(f"加载文件: {filename}")
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                self.content = f.read()
            self.lines = self.content.split('\n')
            print(f"文件加载成功，共 {len(self.lines)} 行")
        except Exception as e:
            print(f"文件加载失败: {e}")
            return False
        return True
    
    def extract_basic_info(self) -> Dict[str, Any]:
        """提取基本游戏信息"""
        info = {}
        
        # 使用正则表达式提取基本信息
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
                # 转换数据类型
                if key in ['government', 'automate_sliders', 'rebel', 'unit', 'state', 'start_pop_index']:
                    info[key] = int(value)
                elif key == 'automate_trade':
                    info[key] = value == 'yes'
                else:
                    info[key] = value
        
        return info
    
    def extract_flags(self) -> List[str]:
        """提取游戏标志"""
        flags = []
        
        # 查找flags块
        flag_match = re.search(r'flags=\s*\{([^}]+)\}', self.content, re.DOTALL)
        if flag_match:
            flag_content = flag_match.group(1)
            # 提取所有标志
            flag_patterns = re.findall(r'(\w+)=yes', flag_content)
            flags.extend(flag_patterns)
        
        return flags
    
    def extract_countries(self) -> Dict[str, Dict]:
        """提取国家信息"""
        countries = {}
        
        # 查找国家代码模式 (3个大写字母)
        country_pattern = r'([A-Z]{3})=\s*\{'
        matches = re.finditer(country_pattern, self.content)
        
        for match in matches:
            tag = match.group(1)
            start_pos = match.end()
            
            # 找到对应的结束括号
            brace_count = 1
            pos = start_pos
            while pos < len(self.content) and brace_count > 0:
                if self.content[pos] == '{':
                    brace_count += 1
                elif self.content[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            if brace_count == 0:
                country_content = self.content[start_pos:pos-1]
                countries[tag] = self._parse_country_content(country_content)
        
        return countries
    
    def _parse_country_content(self, content: str) -> Dict:
        """解析国家内容"""
        country_info = {}
        
        # 提取基本数值
        patterns = {
            'tax_base': r'tax_base=([\d.]+)',
            'capital': r'capital=(\d+)',
            'research_points': r'research_points=([\d.]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1)
                # 确保只转换纯数字，不转换日期格式
                if self._is_pure_number(value):
                    if '.' in value:
                        country_info[key] = float(value)
                    else:
                        country_info[key] = int(value)
        
        # 计算科技数量
        tech_count = len(re.findall(r'\w+={1 0\.000}', content))
        country_info['technology_count'] = tech_count
        
        # 计算标志数量
        flag_count = len(re.findall(r'\w+=yes', content))
        country_info['flag_count'] = flag_count
        
        return country_info
    
    def _is_pure_number(self, value: str) -> bool:
        """检查是否为纯数字（排除日期格式）"""
        try:
            float(value)
            # 检查是否为日期格式
            parts = value.split('.')
            if len(parts) == 3:
                year, month, day = parts
                if (len(year) >= 3 and year.isdigit() and 
                    len(month) <= 2 and month.isdigit() and
                    len(day) <= 2 and day.isdigit()):
                    return False  # 这是日期格式，不是数字
            return True
        except ValueError:
            return False
    
    def extract_worldmarket_summary(self) -> Dict[str, Any]:
        """提取世界市场摘要"""
        worldmarket = {}
        
        # 查找worldmarket块
        wm_match = re.search(r'worldmarket=\s*\{(.*?)\}(?=\s*[a-zA-Z_]+=)', self.content, re.DOTALL)
        if wm_match:
            wm_content = wm_match.group(1)
            
            # 提取商品池
            pools = ['worldmarket_pool', 'price_pool', 'supply_pool']
            for pool_name in pools:
                pool_pattern = f'{pool_name}=\\s*\\{{([^}}]+)\\}}'
                pool_match = re.search(pool_pattern, wm_content)
                if pool_match:
                    pool_content = pool_match.group(1)
                    # 计算商品数量
                    commodity_count = len(re.findall(r'\w+=([\d.]+)', pool_content))
                    worldmarket[f'{pool_name}_commodities'] = commodity_count
                    
                    # 提取前几个商品作为示例
                    commodities = re.findall(r'(\w+)=([\d.]+)', pool_content)[:5]
                    worldmarket[f'{pool_name}_sample'] = {name: float(value) for name, value in commodities}
        
        return worldmarket
    
    def extract_province_summary(self) -> Dict[str, Any]:
        """提取省份摘要信息"""
        province_info = {}
        
        # 计算省份总数
        province_pattern = r'^\s*(\d+)=\s*\{'
        province_matches = re.findall(province_pattern, self.content, re.MULTILINE)
        province_info['total_provinces'] = len(province_matches)
        
        # 提取部分省份的详细信息
        province_details = []
        for i, match in enumerate(province_matches[:10]):  # 只处理前10个省份
            province_id = int(match)
            
            # 查找这个省份的内容
            prov_pattern = f'^\\s*{province_id}=\\s*\\{{(.*?)^\\s*\\}}'
            prov_match = re.search(prov_pattern, self.content, re.MULTILINE | re.DOTALL)
            if prov_match:
                prov_content = prov_match.group(1)
                
                # 提取基本信息
                name_match = re.search(r'name="([^"]+)"', prov_content)
                owner_match = re.search(r'owner="([^"]+)"', prov_content)
                controller_match = re.search(r'controller="([^"]+)"', prov_content)
                
                province_detail = {
                    'id': province_id,
                    'name': name_match.group(1) if name_match else 'Unknown',
                    'owner': owner_match.group(1) if owner_match else 'Unknown',
                    'controller': controller_match.group(1) if controller_match else 'Unknown'
                }
                province_details.append(province_detail)
        
        province_info['sample_provinces'] = province_details
        return province_info
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成完整的存档摘要"""
        print("开始分析存档文件...")
        
        summary = {}
        
        # 基本信息
        print("- 提取基本信息...")
        summary['basic_info'] = self.extract_basic_info()
        
        # 游戏标志
        print("- 提取游戏标志...")
        summary['flags'] = self.extract_flags()
        summary['flag_count'] = len(summary['flags'])
        
        # 国家信息
        print("- 提取国家信息...")
        summary['countries'] = self.extract_countries()
        summary['country_count'] = len(summary['countries'])
        
        # 世界市场
        print("- 提取世界市场信息...")
        summary['worldmarket'] = self.extract_worldmarket_summary()
        
        # 省份信息
        print("- 提取省份信息...")
        summary['provinces'] = self.extract_province_summary()
        
        print("分析完成！")
        return summary
    
    def save_summary(self, summary: Dict, filename: str):
        """保存摘要到JSON文件"""
        print(f"保存摘要到 {filename}...")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print("保存成功！")
        except Exception as e:
            print(f"保存失败: {e}")
    
    def print_summary(self, summary: Dict):
        """打印摘要信息"""
        print("\n" + "="*50)
        print("Victoria II 存档文件分析摘要")
        print("="*50)
        
        # 基本信息
        basic = summary.get('basic_info', {})
        print(f"\n【基本信息】")
        print(f"游戏日期: {basic.get('date', 'Unknown')}")
        print(f"玩家国家: {basic.get('player', 'Unknown')}")
        print(f"政府类型: {basic.get('government', 'Unknown')}")
        print(f"开始日期: {basic.get('start_date', 'Unknown')}")
        
        # 统计信息
        print(f"\n【统计信息】")
        print(f"游戏标志总数: {summary.get('flag_count', 0)}")
        print(f"国家总数: {summary.get('country_count', 0)}")
        print(f"省份总数: {summary.get('provinces', {}).get('total_provinces', 0)}")
        
        # 主要国家
        countries = summary.get('countries', {})
        if countries:
            print(f"\n【主要国家】(前10个)")
            for i, (tag, info) in enumerate(list(countries.items())[:10]):
                tax = info.get('tax_base', 0)
                research = info.get('research_points', 0)
                print(f"{i+1:2d}. {tag}: 税收基础={tax:.2f}, 研究点数={research:.2f}")
        
        # 部分省份
        provinces = summary.get('provinces', {}).get('sample_provinces', [])
        if provinces:
            print(f"\n【部分省份】")
            for prov in provinces:
                print(f"ID {prov['id']:3d}: {prov['name']} (拥有者: {prov['owner']}, 控制者: {prov['controller']})")
        
        # 世界市场
        wm = summary.get('worldmarket', {})
        if wm:
            print(f"\n【世界市场】")
            for pool_name in ['worldmarket_pool', 'price_pool', 'supply_pool']:
                count = wm.get(f'{pool_name}_commodities', 0)
                if count > 0:
                    print(f"{pool_name}: {count} 种商品")
        
        print("\n" + "="*50)


def main():
    """主函数"""
    print("Victoria II 存档文件解析器")
    print("="*40)
    
    # 文件路径
    save_file = "China2245_04_06.v2"
    
    # 创建解析器
    parser = SimpleVictoria2Parser()
    
    # 加载文件
    if not parser.load_file(save_file):
        print("无法加载存档文件！")
        return
    
    # 生成摘要
    summary = parser.generate_summary()
    
    # 显示摘要
    parser.print_summary(summary)
    
    # 保存摘要
    output_file = "victoria2_analysis.json"
    parser.save_summary(summary, output_file)
    
    print(f"\n详细分析结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
