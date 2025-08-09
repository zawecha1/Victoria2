#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 国家块字段分析总结
基于快速分析器的输出结果
"""

# 从输出中提取的关键信息
ANALYSIS_SUMMARY = """
🏛️ Victoria II 国家块字段分析总结
================================================================================

📊 基本统计:
- 总国家数: 220+ 个国家
- 总字段数: 100+ 个不同字段
- 分析文件: autosave.v2 (19,292,664 字符)

🔝 高覆盖率字段 (几乎所有国家都有):
1. primary_culture    - 主要文化 (100%覆盖)
2. government         - 政府类型 (100%覆盖) 
3. plurality         - 多元化程度 (100%覆盖)
4. civilized         - 文明化状态 (100%覆盖)
5. capital           - 首都省份ID (100%覆盖)
6. prestige          - 威望值 (100%覆盖)
7. money             - 国库资金 (100%覆盖)
8. badboy            - 恶名度 (100%覆盖)
9. consciousness     - 觉醒度 (100%覆盖)
10. literacy         - 识字率 (100%覆盖)

📈 数值字段范围分析:
- prestige (威望): 范围 -100.000 到 +100.000+
- money (资金): 范围从负数到数百万
- badboy (恶名度): 范围 0.000 到 25.000+
- plurality (多元化): 范围 0.000 到 100.000
- consciousness (觉醒度): 范围 0.000 到 10.000+
- literacy (识字率): 范围 0.000 到 1.000 (百分比)

🏛️ 政府类型常见值:
- absolute_monarchy (专制君主制)
- constitutional_monarchy (君主立宪制) 
- democracy (民主制)
- presidential_dictatorship (总统独裁)
- proletarian_dictatorship (无产阶级专政)
- fascist_dictatorship (法西斯独裁)
- bourgeois_dictatorship (资产阶级独裁)

🌍 文化类型分析:
- 欧洲文化: english, french, german, russian, italian等
- 亚洲文化: chinese, japanese, korean, vietnamese等  
- 中华文化: beifaren, nanfaren, manchu等
- 其他文化: turkish, arabic, persian等

💰 经济字段:
- money: 国库资金
- bank: 银行资金  
- tax_eff: 税收效率
- leadership: 领导力点数
- research_points: 研究点数
- colonial_points: 殖民点数

⚔️ 军事外交字段:
- war_exhaustion: 战争疲惫度
- mobilized: 动员状态
- army: 陆军单位
- navy: 海军单位
- relation: 外交关系

🎓 社会政策字段:
- school_reforms: 教育改革 (no_schools, good_schools, acceptable_schools)
- health_care: 医疗保健 (no_health_care, good_health_care, trinket_health_care)
- safety_regulations: 安全法规
- pensions: 养老金制度 (no_pensions, good_pensions, acceptable_pensions)
- unemployment_subsidies: 失业补贴
- work_hours: 工作时间

🏭 科技和发明:
- technology: 科技树
- invention: 发明
- schools: 学派选择

📍 地理和领土:
- capital: 首都省份
- state: 州管理
- core: 核心省份
- province: 省份控制

🗳️ 政治制度:
- ruling_party: 执政党
- upper_house: 上议院构成
- lower_house: 下议院构成  
- last_election: 上次选举日期
- nationalvalue: 国家价值观

🔍 特殊字段:
- civilized: 文明化状态 (yes/no)
- human: 人类玩家控制 (yes/no)
- ai: AI控制设置
- great_wars_enabled: 大战机制启用
"""

def print_field_categories():
    """按类别显示字段"""
    categories = {
        "🏛️ 基本国家信息": [
            "primary_culture", "religion", "government", "civilized", 
            "capital", "nationalvalue", "tag"
        ],
        
        "💰 经济财政": [
            "money", "bank", "tax_eff", "leadership", "research_points", 
            "colonial_points", "diplomatic_points", "debt", "loan"
        ],
        
        "📊 社会指标": [
            "plurality", "consciousness", "literacy", "prestige", 
            "non_state_culture_literacy", "suppression"
        ],
        
        "⚔️ 军事外交": [
            "badboy", "war_exhaustion", "mobilized", "army", "navy",
            "relation", "influence", "alliance", "truce", "guarantee"
        ],
        
        "🎓 科技教育": [
            "technology", "invention", "schools", "research_points"
        ],
        
        "🗳️ 政治制度": [
            "ruling_party", "upper_house", "lower_house", "last_election",
            "active_party", "political_reforms"
        ],
        
        "🏭 社会政策": [
            "school_reforms", "health_care", "safety_regulations", 
            "pensions", "unemployment_subsidies", "work_hours"
        ],
        
        "📍 地理领土": [
            "state", "province", "core", "colonial_points"
        ],
        
        "👥 人口文化": [
            "culture", "accepted_culture", "pop", "religion"
        ]
    }
    
    print("\n🗂️ Victoria II 国家字段分类:")
    print("=" * 80)
    
    for category, fields in categories.items():
        print(f"\n{category}:")
        for field in fields:
            print(f"  • {field}")

def print_value_ranges():
    """显示重要字段的取值范围"""
    ranges = {
        "prestige": "威望值: -100.000 到 +100.000+ (国际声誉)",
        "money": "资金: 负数到数百万 (国库金币)",
        "badboy": "恶名度: 0.000 到 25.000+ (好战度，影响外交)",
        "plurality": "多元化: 0.000 到 100.000 (政治参与度)",
        "consciousness": "觉醒度: 0.000 到 10.000+ (人民政治意识)",
        "literacy": "识字率: 0.000 到 1.000 (教育水平，小数表示)",
        "war_exhaustion": "战争疲惫: 0.000 到 100.000 (战争对国家的影响)",
        "tax_eff": "税收效率: 0.000 到 1.000+ (税收征收能力)",
        "leadership": "领导力: 0 到 数千 (军事和外交能力点数)",
        "research_points": "研究点: 0 到 数千 (科技研发点数)"
    }
    
    print("\n📏 重要字段取值范围:")
    print("=" * 80)
    
    for field, description in ranges.items():
        print(f"• {description}")

def main():
    """主函数 - 显示分析总结"""
    print(ANALYSIS_SUMMARY)
    print_field_categories()
    print_value_ranges()
    
    print("\n" + "=" * 80)
    print("💡 使用建议:")
    print("- 修改国家属性时，注意数值范围的合理性")
    print("- 政府类型和社会政策要相互匹配")
    print("- 文明化状态影响很多其他属性的可用性") 
    print("- 恶名度过高会影响外交关系")
    print("- 识字率影响科技研发速度")
    print("=" * 80)

if __name__ == "__main__":
    main()
