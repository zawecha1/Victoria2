# Victoria II 国家省份分析功能

## 概述

成功添加了全面的国家省份分析功能，能够统计每个国家拥有的省份数量和详细信息，并保存到JSON文件中。

## 新增功能

### 1. 核心分析方法

在 `victoria2_main_modifier.py` 中添加了两个新方法：

- `analyze_all_countries_provinces()`: 分析所有国家的省份分布
- `save_countries_provinces_analysis()`: 保存分析结果到JSON文件

### 2. 分析工具

创建了两个使用工具：

- `analyze_countries_provinces.py`: 完整的交互式分析工具
- `simple_province_analyzer.py`: 简化版分析器

## 分析结果

### 统计数据
- **总国家数**: 99个拥有省份的国家
- **总省份数**: 2509个省份
- **最大的国家**: 中国(CHI) - 904个省份

### 前10大国家排名
1. **CHI (中国)**: 904个省份
2. **ENG (英国)**: 188个省份  
3. **SPA (西班牙)**: 119个省份
4. **TUR (奥斯曼)**: 107个省份
5. **BRZ (巴西)**: 102个省份
6. **USA (美国)**: 93个省份
7. **FRA (法国)**: 84个省份
8. **NET (荷兰)**: 55个省份
9. **EGY (埃及)**: 51个省份
10. **AUS (奥地利)**: 50个省份

## JSON输出格式

生成的JSON文件包含：

```json
{
  "analysis_info": {
    "total_countries": 99,
    "total_provinces": 2509,
    "analysis_date": "2025-08-09T19:07:14.xxx",
    "file_analyzed": "autosave.v2"
  },
  "countries": {
    "CHI": {
      "country_tag": "CHI",
      "province_count": 904,
      "provinces": [
        {
          "id": 1,
          "name": "Sitka",
          "controller": "CHI", 
          "cores": ["USA", "CHI"]
        },
        // ... 更多省份
      ]
    },
    // ... 更多国家
  },
  "summary": {
    "top_10_countries": [
      // 前10大国家摘要
    ]
  }
}
```

### 省份信息包含
- **ID**: 省份游戏内ID
- **名称**: 省份名称
- **拥有者**: 当前拥有国家
- **控制者**: 当前控制国家  
- **核心**: 对该省有核心声明的国家列表

## 使用方法

### 方法1: 简化版分析器
```bash
python simple_province_analyzer.py
# 或指定文件
python simple_province_analyzer.py China1841_10_22.v2
```

### 方法2: 完整交互式工具
```bash
python analyze_countries_provinces.py
```
然后选择:
- 1: 交互式选择存档文件
- 2: 快速测试(使用autosave.v2)

### 方法3: 直接调用API
```python
from victoria2_main_modifier import Victoria2Modifier

modifier = Victoria2Modifier('存档文件.v2')
result_file = modifier.save_countries_provinces_analysis()
```

## 输出文件

分析结果自动保存为:
- `countries_provinces_analysis_YYYYMMDD_HHMMSS.json` (默认)
- `test_provinces_analysis.json` (测试模式)

## 技术特点

1. **高性能**: 处理3248个省份，速度较快
2. **内存安全**: 流式处理，不会导致内存溢出
3. **数据完整**: 包含省份的所有关键信息
4. **格式友好**: JSON格式便于后续处理和分析
5. **进度显示**: 处理大文件时显示实时进度

## 实际应用

这个功能可以用于：
- 了解游戏中各国的实际实力分布
- 分析领土变化情况
- 为游戏策略制定提供数据支持
- 检查游戏平衡性

## 文件生成示例

最新生成的分析文件：
- `countries_provinces_analysis_20250809_190714.json` (462KB)

该文件包含了完整的99个国家、2509个省份的详细分析数据。
