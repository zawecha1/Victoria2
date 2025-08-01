#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 人口枚举属性定义
基于实际存档分析的完整枚举类型定义
"""

from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass

class PopType(Enum):
    """人口类型枚举"""
    ARISTOCRATS = "aristocrats"        # 贵族
    ARTISANS = "artisans"             # 工匠
    BUREAUCRATS = "bureaucrats"        # 官僚
    CAPITALISTS = "capitalists"        # 资本家
    CLERGYMEN = "clergymen"           # 神职人员
    CLERKS = "clerks"                 # 职员
    CRAFTSMEN = "craftsmen"           # 工匠
    FARMERS = "farmers"               # 农民
    LABOURERS = "labourers"           # 工人
    OFFICERS = "officers"             # 军官
    SLAVES = "slaves"                 # 奴隶
    SOLDIERS = "soldiers"             # 士兵
    INTELLECTUALS = "intellectuals"    # 知识分子

class Culture(Enum):
    """文化枚举（基于分析发现的主要文化）"""
    # 北美文化
    YANKEE = "yankee"                 # 美国北方人
    DIXIE = "dixie"                   # 美国南方人
    NATIVE_AMERICAN_MINOR = "native_american_minor"  # 美洲原住民
    AFRO_CARIBENO = "afro_caribeno"   # 非裔加勒比人
    
    # 欧洲文化
    BRITISH = "british"               # 英国人
    RUSSIAN = "russian"               # 俄国人
    SPANISH = "spanish"               # 西班牙人
    SOUTH_ITALIAN = "south_italian"   # 南意大利人
    
    # 亚洲文化
    BEIFAREN = "beifaren"             # 北方人（中国）
    MANCHU = "manchu"                 # 满族
    AINU = "ainu"                     # 阿伊努人
    MALAY = "malay"                   # 马来人
    
    # 其他文化
    MAGHREBI = "maghrebi"             # 马格里布人
    MARATHI = "marathi"               # 马拉地人

class Religion(Enum):
    """宗教枚举"""
    PROTESTANT = "protestant"         # 新教
    CATHOLIC = "catholic"             # 天主教
    ORTHODOX = "orthodox"             # 东正教
    MAHAYANA = "mahayana"             # 大乘佛教
    HINDU = "hindu"                   # 印度教
    SUNNI = "sunni"                   # 逊尼派伊斯兰教
    ANIMIST = "animist"               # 泛灵论

class IdeologyType(Enum):
    """意识形态类型枚举（基于游戏机制）"""
    CONSERVATIVE = 1                  # 保守主义
    LIBERAL = 2                       # 自由主义
    REACTIONARY = 3                   # 反动主义
    ANARCHO_LIBERAL = 4               # 无政府自由主义
    SOCIALIST = 5                     # 社会主义
    COMMUNIST = 6                     # 共产主义
    FASCIST = 7                       # 法西斯主义

class IssueType(Enum):
    """政治议题类型枚举（基于游戏机制）"""
    # 政治改革
    VOTING_SYSTEM = (1, "选举制度")
    UPPER_HOUSE_COMPOSITION = (2, "上议院组成")
    VOTING_FRANCHISE = (3, "选举权")
    PUBLIC_MEETINGS = (4, "公共集会")
    PRESS_RIGHTS = (5, "新闻权利")
    TRADE_UNIONS = (6, "工会")
    POLITICAL_PARTIES = (7, "政党")
    
    # 社会改革
    CHILD_LABOR = (8, "童工")
    WORK_HOURS = (9, "工作时间")
    SAFETY_REGULATIONS = (10, "安全法规")
    HEALTH_CARE = (14, "医疗保健")
    SCHOOL_REFORMS = (15, "学校改革")
    SLAVERY = (16, "奴隶制")
    PENAL_SYSTEM = (17, "刑罚制度")
    
    # 经济政策
    WAGE_REFORM = (34, "工资改革")
    PENSION_REFORMS = (36, "养老金改革")

@dataclass
class PopulationAttributes:
    """人口属性数据结构"""
    province_id: int
    pop_type: PopType
    culture: Culture
    religion: Religion
    size: int
    militancy: float              # 斗争性 (0.0-10.0)
    consciousness: float          # 意识 (0.0-10.0)
    literacy: float              # 识字率 (0.0-1.0)
    money: float                 # 财富
    everyday_needs: float        # 日常需求满足度 (0.0-1.0)
    luxury_needs: float          # 奢侈需求满足度 (0.0-1.0)
    ideology_support: Dict[IdeologyType, float]  # 意识形态支持度
    issue_positions: Dict[IssueType, float]      # 政治议题立场

class PopulationEnumerator:
    """人口枚举属性工具类"""
    
    @staticmethod
    def get_all_pop_types() -> List[str]:
        """获取所有人口类型"""
        return [pop.value for pop in PopType]
    
    @staticmethod
    def get_all_cultures() -> List[str]:
        """获取所有文化类型"""
        return [culture.value for culture in Culture]
    
    @staticmethod
    def get_all_religions() -> List[str]:
        """获取所有宗教类型"""
        return [religion.value for religion in Religion]
    
    @staticmethod
    def get_ideology_names() -> Dict[int, str]:
        """获取意识形态ID对应名称"""
        return {
            1: "保守主义 (Conservative)",
            2: "自由主义 (Liberal)", 
            3: "反动主义 (Reactionary)",
            4: "无政府自由主义 (Anarcho-Liberal)",
            5: "社会主义 (Socialist)",
            6: "共产主义 (Communist)",
            7: "法西斯主义 (Fascist)"
        }
    
    @staticmethod
    def get_issue_names() -> Dict[int, str]:
        """获取政治议题ID对应名称"""
        return {
            1: "选举制度 (Voting System)",
            2: "上议院组成 (Upper House)",
            3: "选举权 (Voting Franchise)",
            4: "公共集会 (Public Meetings)",
            5: "新闻权利 (Press Rights)",
            6: "工会 (Trade Unions)",
            7: "政党 (Political Parties)",
            8: "童工 (Child Labor)",
            9: "工作时间 (Work Hours)",
            10: "安全法规 (Safety Regulations)",
            14: "医疗保健 (Health Care)",
            15: "学校改革 (School Reforms)",
            16: "奴隶制 (Slavery)",
            17: "刑罚制度 (Penal System)",
            34: "工资改革 (Wage Reform)",
            36: "养老金改革 (Pension Reforms)"
        }
    
    @staticmethod
    def get_pop_type_descriptions() -> Dict[str, str]:
        """获取人口类型描述"""
        return {
            "aristocrats": "贵族 - 土地所有者和传统统治阶级",
            "artisans": "工匠 - 手工业者和小型制造商",
            "bureaucrats": "官僚 - 政府行政人员",
            "capitalists": "资本家 - 工厂主和大型企业家",
            "clergymen": "神职人员 - 宗教机构成员",
            "clerks": "职员 - 中产阶级白领工作者",
            "craftsmen": "工匠 - 熟练技术工人",
            "farmers": "农民 - 农业生产者",
            "labourers": "工人 - 非熟练体力劳动者",
            "officers": "军官 - 军队指挥官",
            "slaves": "奴隶 - 被奴役的劳动者",
            "soldiers": "士兵 - 军队战斗人员",
            "intellectuals": "知识分子 - 教育和研究人员"
        }
    
    @staticmethod
    def get_culture_groups() -> Dict[str, List[str]]:
        """获取文化组分类"""
        return {
            "北美": ["yankee", "dixie", "native_american_minor", "afro_caribeno"],
            "欧洲": ["british", "russian", "spanish", "south_italian"],
            "东亚": ["beifaren", "manchu", "ainu"],
            "南亚": ["marathi"],
            "东南亚": ["malay"],
            "非洲": ["maghrebi"]
        }
    
    @staticmethod
    def get_religion_groups() -> Dict[str, List[str]]:
        """获取宗教组分类"""
        return {
            "基督教": ["protestant", "catholic", "orthodox"],
            "佛教": ["mahayana"],
            "伊斯兰教": ["sunni"],
            "印度教": ["hindu"],
            "其他": ["animist"]
        }
    
    def print_enumeration_reference(self):
        """打印完整的枚举参考"""
        print("=" * 80)
        print("Victoria II 人口枚举属性完整参考")
        print("=" * 80)
        
        print("\n👥 人口类型 (Pop Types):")
        descriptions = self.get_pop_type_descriptions()
        for i, pop_type in enumerate(self.get_all_pop_types(), 1):
            desc = descriptions.get(pop_type, "")
            print(f"  {i:2d}. {pop_type:<15} - {desc}")
        
        print("\n🎭 文化类型 (Cultures):")
        culture_groups = self.get_culture_groups()
        for group_name, cultures in culture_groups.items():
            print(f"  {group_name}:")
            for culture in cultures:
                print(f"    - {culture}")
        
        print("\n⛪ 宗教类型 (Religions):")
        religion_groups = self.get_religion_groups()
        for group_name, religions in religion_groups.items():
            print(f"  {group_name}:")
            for religion in religions:
                print(f"    - {religion}")
        
        print("\n💭 意识形态 (Ideologies):")
        ideologies = self.get_ideology_names()
        for id_num, name in ideologies.items():
            print(f"  {id_num}. {name}")
        
        print("\n🗳️ 政治议题 (Political Issues):")
        issues = self.get_issue_names()
        for id_num, name in issues.items():
            print(f"  {id_num:2d}. {name}")
        
        print("\n📊 属性说明:")
        print("  斗争性 (Militancy): 0.0-10.0, 越高越容易叛乱")
        print("  意识 (Consciousness): 0.0-10.0, 影响政治参与")
        print("  识字率 (Literacy): 0.0-1.0, 影响技术和文化发展")
        print("  需求满足度: 0.0-1.0, 影响人口幸福度")
        
        print("=" * 80)

def main():
    """主函数"""
    enumerator = PopulationEnumerator()
    enumerator.print_enumeration_reference()
    
    print("\n交互式查询:")
    while True:
        print("\n选择查询类型:")
        print("1. 人口类型详情")
        print("2. 文化组信息")
        print("3. 宗教组信息")
        print("4. 意识形态列表")
        print("5. 政治议题列表")
        print("0. 退出")
        
        choice = input("请选择 (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            descriptions = enumerator.get_pop_type_descriptions()
            for pop_type, desc in descriptions.items():
                print(f"• {pop_type}: {desc}")
        elif choice == "2":
            groups = enumerator.get_culture_groups()
            for group, cultures in groups.items():
                print(f"• {group}: {', '.join(cultures)}")
        elif choice == "3":
            groups = enumerator.get_religion_groups()
            for group, religions in groups.items():
                print(f"• {group}: {', '.join(religions)}")
        elif choice == "4":
            ideologies = enumerator.get_ideology_names()
            for id_num, name in ideologies.items():
                print(f"• ID {id_num}: {name}")
        elif choice == "5":
            issues = enumerator.get_issue_names()
            for id_num, name in issues.items():
                print(f"• ID {id_num}: {name}")

if __name__ == "__main__":
    main()
