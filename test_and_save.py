# 测试并保存修复后的意识形态修改
from victoria2_main_modifier import Victoria2Modifier

print("测试并保存修复后的意识形态修改...")

# 创建修改器实例
modifier = Victoria2Modifier(debug_mode=True)
modifier.load_file('China1841_12_17.v2')

# 只执行意识形态修改
print("开始修改中国人口属性...")
result = modifier.modify_chinese_population(max_provinces=10)  # 处理前10个省份

if result:
    print("✅ 修改成功!")
    print(f"宗教修改: {modifier.religion_changes} 处")
    print(f"意识形态修改: {modifier.ideology_changes} 处")
    print(f"总修改数: {modifier.population_count} 个人口组")
    
    # 保存文件
    print("\n💾 保存修改到文件...")
    output_file = 'China1841_12_17_ideology_fixed.v2'
    modifier.save_file(output_file)
    print(f"文件已保存为: {output_file}")
    
else:
    print("❌ 修改失败!")
