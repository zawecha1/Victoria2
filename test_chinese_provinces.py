# 测试中国省份查找逻辑
from victoria2_main_modifier import Victoria2Modifier

print("测试中国省份查找...")

# 初始化修改器
modifier = Victoria2Modifier()
modifier.load_file('China1841_12_17.v2')

# 查找中国省份
chinese_provinces = modifier.find_chinese_provinces()

print(f"传统方法找到的中国省份: {len(chinese_provinces)} 个")
print(f"前10个省份ID: {chinese_provinces[:10]}")

# 测试结构化方法
modifier.parse_structure()
chinese_provinces_structured = modifier.find_chinese_provinces_structured()

print(f"结构化方法找到的中国省份: {len(chinese_provinces_structured)} 个")
print(f"前10个省份: {[block.name for block in chinese_provinces_structured[:10]]}")

# 测试一个中国省份的内容
if chinese_provinces_structured:
    first_province = chinese_provinces_structured[0]
    print(f"\n第一个中国省份 {first_province.name} 的内容片段:")
    print(first_province.content[:1000])
    
    # 检查是否包含意识形态数据
    if 'ideology=' in first_province.content:
        print(f"\n省份 {first_province.name} 包含意识形态数据!")
    else:
        print(f"\n省份 {first_province.name} 不包含意识形态数据。")
