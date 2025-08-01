#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Victoria II 存档解析器测试脚本
"""

from victoria2_parser import Victoria2Parser
import json
import os

def test_parser():
    """测试解析器功能"""
    
    # 文件路径
    input_file = r"China2245_04_06.v2"
    
    if not os.path.exists(input_file):
        print(f"错误: 找不到文件 {input_file}")
        return
    
    print("=== Victoria II 存档解析器测试 ===\n")
    
    # 创建解析器实例
    parser = Victoria2Parser()
    
    try:
        # 解析文件
        print("1. 开始解析存档文件...")
        game_data = parser.parse_file(input_file)
        
        # 显示基本信息
        print("\n2. 基本游戏信息:")
        print(f"   游戏日期: {game_data.date}")
        print(f"   玩家: {game_data.player}")
        print(f"   政府类型: {game_data.government}")
        print(f"   开始日期: {game_data.start_date}")
        
        # 显示标志信息
        print(f"\n3. 游戏标志 (前10个):")
        for i, flag in enumerate(game_data.flags[:10]):
            print(f"   {flag.name}: {flag.value}")
        
        # 显示世界市场信息
        if game_data.worldmarket:
            print(f"\n4. 世界市场信息:")
            print(f"   商品种类: {len(game_data.worldmarket.worldmarket_pool)}")
            
            # 显示部分商品价格
            print("   部分商品价格:")
            for i, (commodity, price) in enumerate(list(game_data.worldmarket.price_pool.items())[:5]):
                print(f"     {commodity}: {price:.2f}")
        
        # 显示国家信息
        print(f"\n5. 国家信息:")
        print(f"   总国家数: {len(game_data.countries)}")
        print("   主要国家:")
        for tag, country in list(game_data.countries.items())[:5]:
            print(f"     {tag}: 税收={country.tax_base:.2f}, 研究点={country.research_points:.2f}")
        
        # 显示省份信息
        print(f"\n6. 省份信息:")
        print(f"   总省份数: {len(game_data.provinces)}")
        print("   部分省份:")
        for pid, province in list(game_data.provinces.items())[:5]:
            print(f"     {pid} ({province.name}): {province.owner} -> {province.controller}")
        
        # 保存为JSON文件
        output_file = "china_save_parsed.json"
        print(f"\n7. 保存解析结果到 {output_file}...")
        
        # 创建一个简化的数据结构用于JSON输出
        simplified_data = {
            "basic_info": {
                "date": game_data.date,
                "player": game_data.player,
                "government": game_data.government,
                "start_date": game_data.start_date,
                "start_pop_index": game_data.start_pop_index
            },
            "flags": [{"name": f.name, "value": f.value} for f in game_data.flags[:20]],
            "countries": {
                tag: {
                    "tax_base": country.tax_base,
                    "capital": country.capital,
                    "research_points": country.research_points,
                    "flag_count": len(country.flags),
                    "tech_count": len(country.technologies)
                }
                for tag, country in list(game_data.countries.items())[:10]
            },
            "provinces": {
                str(pid): {
                    "name": province.name,
                    "owner": province.owner,
                    "controller": province.controller,
                    "cores": province.cores,
                    "garrison": province.garrison,
                    "building_count": len(province.buildings),
                    "modifier_count": len(province.modifiers)
                }
                for pid, province in list(game_data.provinces.items())[:10]
            }
        }
        
        if game_data.worldmarket:
            simplified_data["worldmarket"] = {
                "commodity_count": len(game_data.worldmarket.worldmarket_pool),
                "sample_prices": dict(list(game_data.worldmarket.price_pool.items())[:10])
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(simplified_data, f, indent=2, ensure_ascii=False)
        
        print("解析完成！")
        print(f"\n=== 摘要 ===")
        print(f"成功解析了Victoria II存档文件")
        print(f"- 游戏日期: {game_data.date}")
        print(f"- 总标志: {len(game_data.flags)}")
        print(f"- 总国家: {len(game_data.countries)}")
        print(f"- 总省份: {len(game_data.provinces)}")
        print(f"- 解析结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"解析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser()
