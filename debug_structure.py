# 调试结构化方法的人口检测
from victoria2_main_modifier import Victoria2Modifier

print("调试结构化方法的人口检测...")

# 创建修改器实例
modifier = Victoria2Modifier(debug_mode=True)
modifier.load_file('China1841_12_17.v2')

# 查找中国省份
chinese_provinces = modifier.find_chinese_provinces_structured()
print(f"找到 {len(chinese_provinces)} 个中国省份")

if chinese_provinces:
    # 检查第一个省份的结构
    first_province = chinese_provinces[0]
    print(f"\n分析省份 {first_province.name}:")
    print(f"子块数量: {len(first_province.children)}")
    
    # 检查前5个子块
    pop_types = ['farmers', 'labourers', 'clerks', 'artisans', 'craftsmen',
                'clergymen', 'officers', 'soldiers', 'aristocrats', 'capitalists',
                'bureaucrats', 'intellectuals']
    
    pop_blocks_found = 0
    for i, child_block in enumerate(first_province.children[:10]):
        print(f"\n子块 {i+1}:")
        print(f"  名称: '{child_block.name}'")
        print(f"  内容长度: {len(child_block.content)}")
        print(f"  内容前100字符: {child_block.content[:100]}")
        
        # 检查是否包含人口类型
        contains_pop_type = any(pop_type in child_block.content for pop_type in pop_types)
        print(f"  包含人口类型: {contains_pop_type}")
        
        if contains_pop_type:
            pop_blocks_found += 1
            print(f"  -> 这是人口块!")
            
            # 检查是否包含意识形态
            if 'ideology=' in child_block.content:
                print(f"  -> 包含意识形态数据!")
            else:
                print(f"  -> 不包含意识形态数据")
    
    print(f"\n总结: 省份 {first_province.name} 中找到 {pop_blocks_found} 个人口块")
else:
    print("未找到中国省份")
