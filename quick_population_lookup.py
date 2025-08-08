"""
Victoria II 人口属性快速查询工具
快速查询和分析特定人口属性的工具
"""

import re
import json
from collections import Counter
from typing import Dict, List, Any, Optional

class QuickPopulationLookup:
    def __init__(self, save_file: str):
        """初始化快速查询工具"""
        self.save_file = save_file
        self.content = ""
        
        # 属性说明
        self.attribute_help = {
            'size': '人口数量',
            'culture': '文化',
            'religion': '宗教',
            'mil': '斗争性(0-10)',
            'con': '意识(0-10)',
            'money': '金钱',
            'bank': '银行存款',
            'literacy': '识字率(0-1)',
            'luxury_needs': '奢侈品需求(0-1)',
            'everyday_needs': '日常需求(0-1)',
            'life_needs': '生存需求(0-1)'
        }
        
        self.pop_types = [
            'farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
            'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
            'bureaucrats', 'intellectuals'
        ]
        
        self.load_file()
    
    def load_file(self):
        """加载存档文件"""
        try:
            with open(self.save_file, 'r', encoding='utf-8-sig', errors='ignore') as f:
                self.content = f.read()
            print(f"✅ 文件加载成功: {self.save_file}")
        except Exception as e:
            print(f"❌ 文件加载失败: {e}")
            raise
    
    def find_population_by_criteria(self, pop_type: Optional[str] = None, 
                                   culture: Optional[str] = None,
                                   religion: Optional[str] = None,
                                   province_id: Optional[str] = None,
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """根据条件查找人口"""
        results = []
        
        # 确定搜索范围
        if province_id:
            # 搜索特定省份
            province_pattern = f'^{province_id}=\\s*{{([^{{}}]*(?:{{[^{{}}]*}}[^{{}}]*)*)}}'
            province_match = re.search(province_pattern, self.content, re.MULTILINE | re.DOTALL)
            if not province_match:
                print(f"❌ 未找到省份 {province_id}")
                return results
            search_content = province_match.group(1)
            print(f"🔍 在省份 {province_id} 中搜索...")
        else:
            search_content = self.content
            print("🔍 在整个存档中搜索...")
        
        # 搜索人口类型
        search_pop_types = [pop_type] if pop_type else self.pop_types
        
        for search_pop_type in search_pop_types:
            pattern = f'({search_pop_type}=\\s*{{[^{{}}]*(?:{{[^{{}}]*}}[^{{}}]*)*}})'
            matches = re.finditer(pattern, search_content, re.DOTALL)
            
            for match in matches:
                pop_block = match.group(1)
                
                # 提取基本信息
                pop_info = self.extract_basic_info(pop_block)
                pop_info['pop_type'] = search_pop_type
                
                # 如果指定了省份ID，添加到结果中
                if province_id:
                    pop_info['province_id'] = province_id
                else:
                    # 尝试找到省份ID
                    pop_info['province_id'] = self.find_province_for_position(match.start())
                
                # 应用筛选条件
                if culture and pop_info.get('culture') != culture:
                    continue
                if religion and pop_info.get('religion') != religion:
                    continue
                
                results.append(pop_info)
                
                if len(results) >= limit:
                    break
            
            if len(results) >= limit:
                break
        
        return results
    
    def extract_basic_info(self, pop_block: str) -> Dict[str, Any]:
        """提取人口块的基本信息"""
        info = {}
        
        # 提取数值属性
        numeric_patterns = {
            'size': r'size\s*=\s*([\d.]+)',
            'mil': r'mil\s*=\s*([\d.]+)',
            'con': r'con\s*=\s*([\d.]+)',
            'money': r'money\s*=\s*([\d.]+)',
            'bank': r'bank\s*=\s*([\d.]+)',
            'literacy': r'literacy\s*=\s*([\d.]+)',
            'luxury_needs': r'luxury_needs\s*=\s*([\d.]+)',
            'everyday_needs': r'everyday_needs\s*=\s*([\d.]+)',
            'life_needs': r'life_needs\s*=\s*([\d.]+)'
        }
        
        for attr_name, pattern in numeric_patterns.items():
            match = re.search(pattern, pop_block)
            if match:
                try:
                    info[attr_name] = float(match.group(1))
                except ValueError:
                    info[attr_name] = match.group(1)
        
        # 提取文化和宗教
        culture_religion_matches = re.findall(r'(\w+)\s*=\s*(\w+)', pop_block)
        for culture, religion in culture_religion_matches:
            if culture not in numeric_patterns and not religion.replace('.', '').isdigit():
                if 'culture' not in info:
                    info['culture'] = culture
                if 'religion' not in info:
                    info['religion'] = religion
                break
        
        return info
    
    def find_province_for_position(self, position: int) -> str:
        """根据位置查找对应的省份ID"""
        # 向前搜索最近的省份定义
        before_content = self.content[:position]
        province_matches = list(re.finditer(r'^(\d+)=\s*{', before_content, re.MULTILINE))
        if province_matches:
            return province_matches[-1].group(1)
        return "unknown"
    
    def get_attribute_statistics(self, attribute: str, pop_type: Optional[str] = None) -> Dict[str, Any]:
        """获取特定属性的统计信息"""
        print(f"📊 正在分析属性: {attribute}")
        
        if attribute in ['culture', 'religion']:
            return self.get_categorical_stats(attribute, pop_type)
        else:
            return self.get_numeric_stats(attribute, pop_type)
    
    def get_numeric_stats(self, attribute: str, pop_type: Optional[str] = None) -> Dict[str, Any]:
        """获取数值属性的统计信息"""
        values = []
        
        search_pop_types = [pop_type] if pop_type else self.pop_types
        
        for search_pop_type in search_pop_types:
            pattern = f'{search_pop_type}=\\s*{{[^{{}}]*(?:{{[^{{}}]*}}[^{{}}]*)*}}'
            matches = re.finditer(pattern, self.content, re.DOTALL)
            
            for match in matches:
                pop_block = match.group(0)
                attr_match = re.search(f'{attribute}\\s*=\\s*([\\d.]+)', pop_block)
                if attr_match:
                    try:
                        values.append(float(attr_match.group(1)))
                    except ValueError:
                        pass
        
        if not values:
            return {'error': f'未找到属性 {attribute} 的数据'}
        
        values.sort()
        return {
            'attribute': attribute,
            'pop_type': pop_type or '所有类型',
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'average': sum(values) / len(values),
            'median': values[len(values) // 2],
            'unique_values': len(set(values))
        }
    
    def get_categorical_stats(self, attribute: str, pop_type: Optional[str] = None) -> Dict[str, Any]:
        """获取分类属性的统计信息"""
        values = []
        
        search_pop_types = [pop_type] if pop_type else self.pop_types
        
        for search_pop_type in search_pop_types:
            pattern = f'{search_pop_type}=\\s*{{[^{{}}]*(?:{{[^{{}}]*}}[^{{}}]*)*}}'
            matches = re.finditer(pattern, self.content, re.DOTALL)
            
            for match in matches:
                pop_block = match.group(0)
                # 查找文化=宗教形式
                culture_religion_matches = re.findall(r'(\\w+)\\s*=\\s*(\\w+)', pop_block)
                for item1, item2 in culture_religion_matches:
                    if not item2.replace('.', '').isdigit():
                        if attribute == 'culture':
                            values.append(item1)
                        elif attribute == 'religion':
                            values.append(item2)
                        break
        
        if not values:
            return {'error': f'未找到属性 {attribute} 的数据'}
        
        counter = Counter(values)
        return {
            'attribute': attribute,
            'pop_type': pop_type or '所有类型',
            'count': len(values),
            'unique_values': len(counter),
            'most_common': counter.most_common(10),
            'distribution': dict(counter)
        }
    
    def search_by_value(self, attribute: str, value: Any, pop_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """根据属性值搜索人口"""
        results = []
        search_pop_types = [pop_type] if pop_type else self.pop_types
        
        print(f"🔍 搜索 {attribute}={value} 的人口...")
        
        for search_pop_type in search_pop_types:
            pattern = f'({search_pop_type}=\\s*{{[^{{}}]*(?:{{[^{{}}]*}}[^{{}}]*)*}})'
            matches = re.finditer(pattern, self.content, re.DOTALL)
            
            for match in matches:
                pop_block = match.group(1)
                
                # 检查是否包含指定的属性值
                if attribute in ['culture', 'religion']:
                    # 文本属性搜索
                    if attribute == 'culture':
                        culture_match = re.search(f'{value}\\s*=\\s*\\w+', pop_block)
                        if not culture_match:
                            continue
                    elif attribute == 'religion':
                        religion_match = re.search(f'\\w+\\s*=\\s*{value}', pop_block)
                        if not religion_match:
                            continue
                else:
                    # 数值属性搜索
                    attr_match = re.search(f'{attribute}\\s*=\\s*{value}', pop_block)
                    if not attr_match:
                        continue
                
                # 提取信息
                pop_info = self.extract_basic_info(pop_block)
                pop_info['pop_type'] = search_pop_type
                pop_info['province_id'] = self.find_province_for_position(match.start())
                
                results.append(pop_info)
                
                if len(results) >= limit:
                    break
            
            if len(results) >= limit:
                break
        
        return results

def print_population_info(populations: List[Dict[str, Any]]):
    """打印人口信息"""
    if not populations:
        print("❌ 未找到匹配的人口")
        return
    
    print(f"\n📋 找到 {len(populations)} 个人口组:")
    print("-" * 80)
    
    for i, pop in enumerate(populations, 1):
        print(f"{i:2d}. 省份{pop.get('province_id', '?')} - {pop.get('pop_type', '?')} "
              f"({pop.get('culture', '?')}-{pop.get('religion', '?')})")
        print(f"     人口: {pop.get('size', 0):,.0f}  "
              f"金钱: {pop.get('money', 0):,.0f}  "
              f"识字率: {pop.get('literacy', 0):.3f}")
        if 'mil' in pop:
            print(f"     斗争性: {pop.get('mil', 0):.1f}  "
                  f"意识: {pop.get('con', 0):.1f}")
        print()

def print_statistics(stats: Dict[str, Any]):
    """打印统计信息"""
    if 'error' in stats:
        print(f"❌ {stats['error']}")
        return
    
    print(f"\n📊 {stats['attribute']} 统计信息 ({stats['pop_type']}):")
    print("-" * 50)
    
    if 'average' in stats:
        # 数值统计
        print(f"数据点数量: {stats['count']:,}")
        print(f"取值范围: {stats['min']:.3f} - {stats['max']:.3f}")
        print(f"平均值: {stats['average']:.3f}")
        print(f"中位数: {stats['median']:.3f}")
        print(f"唯一值数量: {stats['unique_values']:,}")
    else:
        # 分类统计
        print(f"数据点数量: {stats['count']:,}")
        print(f"唯一值数量: {stats['unique_values']:,}")
        print(f"最常见的值:")
        for value, count in stats['most_common']:
            percentage = (count / stats['count']) * 100
            print(f"  {value}: {count:,} ({percentage:.1f}%)")

def main():
    """主函数 - 交互式查询界面"""
    import sys
    
    if len(sys.argv) != 2:
        print("用法: python quick_population_lookup.py <存档文件.v2>")
        return
    
    save_file = sys.argv[1]
    
    try:
        lookup = QuickPopulationLookup(save_file)
        
        print("\n🔧 Victoria II 人口属性快速查询工具")
        print("=" * 50)
        
        while True:
            print("\n📋 可用选项:")
            print("1. 按条件查找人口")
            print("2. 按属性值搜索")
            print("3. 查看属性统计")
            print("4. 显示属性帮助")
            print("5. 退出")
            
            choice = input("\n请选择操作 (1-5): ").strip()
            
            if choice == "1":
                print("\n🔍 按条件查找人口")
                pop_type = input("人口类型 (可选, 如: farmers): ").strip() or None
                culture = input("文化 (可选, 如: beifaren): ").strip() or None
                religion = input("宗教 (可选, 如: mahayana): ").strip() or None
                province_id = input("省份ID (可选, 如: 1612): ").strip() or None
                limit = int(input("显示数量限制 (默认10): ").strip() or "10")
                
                populations = lookup.find_population_by_criteria(
                    pop_type=pop_type, culture=culture, religion=religion,
                    province_id=province_id, limit=limit
                )
                print_population_info(populations)
            
            elif choice == "2":
                print("\n🔍 按属性值搜索")
                attribute = input("属性名 (如: money, culture): ").strip()
                value = input("属性值 (如: 9999999999, beifaren): ").strip()
                pop_type = input("人口类型 (可选): ").strip() or None
                limit = int(input("显示数量限制 (默认10): ").strip() or "10")
                
                # 尝试转换为数值
                try:
                    value = float(value)
                except ValueError:
                    pass  # 保持字符串
                
                populations = lookup.search_by_value(attribute, value, pop_type, limit)
                print_population_info(populations)
            
            elif choice == "3":
                print("\n📊 查看属性统计")
                attribute = input("属性名 (如: money, literacy, culture): ").strip()
                pop_type = input("人口类型 (可选): ").strip() or None
                
                stats = lookup.get_attribute_statistics(attribute, pop_type)
                print_statistics(stats)
            
            elif choice == "4":
                print("\n📖 属性帮助:")
                print("-" * 30)
                for attr, desc in lookup.attribute_help.items():
                    print(f"{attr:15}: {desc}")
                print(f"\n🧑‍🤝‍🧑 人口类型: {', '.join(lookup.pop_types)}")
            
            elif choice == "5":
                print("👋 再见！")
                break
            
            else:
                print("❌ 无效选择，请输入 1-5")
    
    except Exception as e:
        print(f"❌ 程序执行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
