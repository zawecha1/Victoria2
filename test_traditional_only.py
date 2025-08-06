# 强制使用传统方法测试修复
from victoria2_main_modifier import Victoria2Modifier

print("强制使用传统方法测试修复...")

# 创建修改器实例
modifier = Victoria2Modifier(debug_mode=True)
modifier.load_file('China1841_12_17.v2')

# 强制使用传统方法 - 不初始化结构
print("开始修改中国人口属性（传统方法）...")
result = modifier._modify_chinese_population_traditional(max_provinces=3)  # 只处理前3个省份进行测试

if result:
    print("✅ 修改成功!")
    print(f"宗教修改: {modifier.religion_changes} 处")
    print(f"意识形态修改: {modifier.ideology_changes} 处")
    print(f"总修改数: {modifier.population_count} 个人口组")
else:
    print("❌ 修改失败!")
