# 维多利亚2国家信息提取系统

## 项目概述

基于现有的`victoria2_main_modifier.py`中的国家查找代码，开发了一套完整的维多利亚2存档国家信息提取和查询系统。

## 文件说明

### 1. `country_extractor.py` - 主要提取工具
- **功能**: 从维多利亚2存档文件中提取所有国家的详细信息
- **特色**: 智能识别CHI标签（根据文化判断是中国还是智利）
- **输出**: 生成详细的JSON报告，包含221个国家的完整信息

### 2. `simple_country_list.py` - 简化版生成器
- **功能**: 从详细报告生成简洁的国家代码和名称列表
- **输出**: 生成便于查询的简化JSON文件

### 3. `country_query.py` - 交互式查询工具
- **功能**: 提供多种查询方式的命令行工具
- **使用方法**:
  ```bash
  python country_query.py CHI      # 查询特定国家
  python country_query.py active   # 显示活跃国家
  python country_query.py codes    # 显示所有代码
  python country_query.py China    # 按名称搜索
  ```

## 提取结果统计

基于当前存档(`China1838_12_26.v2`)的统计数据：

- **总国家数**: 221个
- **活跃国家**: 98个（拥有省份）
- **已灭亡国家**: 123个
- **文明化国家**: 74个
- **未文明化国家**: 147个

## 主要功能特色

### 1. 智能国家识别
- 解决了CHI标签的歧义问题（中国 vs 智利）
- 根据`primary_culture`字段智能判断：
  - `beifaren`/`nanfaren`/`manchu` → China（中国）
  - 其他文化 → Chile（智利）

### 2. 完整信息提取
每个国家包含以下信息：
- 国家标签（tag）
- 国家名称（name）
- 首都省份（capital）
- 政府类型（government）
- 主要文化（primary_culture）
- 技术学派（technology_school）
- 文明化状态（civilized）
- 威望（prestige）
- 恶名度（badboy）
- 国库金钱（money）
- 上次选举（last_election）

### 3. 多维度分析
- 活跃/已灭亡国家分类
- 文明化/未文明化状态统计
- 政府类型分布统计
- 文化分布统计
- 技术学派统计

## 技术实现

### 国家块识别模式
```python
country_pattern = re.compile(r'^([A-Z]{2,3})=\s*{', re.MULTILINE)
```

### 智能文化判断
```python
def get_smart_country_name(self, tag: str, culture: str) -> str:
    if tag == 'CHI':
        chinese_cultures = ['beifaren', 'nanfaren', 'manchu']
        if culture in chinese_cultures:
            return 'China'
        else:
            return 'Chile'
    return self.get_country_display_name(tag)
```

### 省份所有者检测
```python
province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
owner_match = re.search(r'owner="?([A-Z]{2,3})"?', province_content)
```

## 输出文件格式

### 详细报告 (`countries_*.json`)
```json
{
  "metadata": {
    "source_file": "China1838_12_26.v2",
    "total_countries": 221,
    "active_countries": 98,
    "dead_countries": 123
  },
  "countries": {
    "CHI": {
      "tag": "CHI",
      "name": "China",
      "capital": 1612,
      "government": "{1 0.000}",
      "primary_culture": "beifaren",
      "civilized": true,
      "active": true
    }
  },
  "statistics": { ... }
}
```

### 简化列表 (`simple_countries_*.json`)
```json
{
  "countries": {
    "CHI": {
      "name": "China",
      "capital": 1612,
      "culture": "beifaren",
      "civilized": true,
      "active": true
    }
  },
  "country_codes": ["REB", "ENG", "RUS", ...],
  "active_country_codes": ["CHI", "JAP", "RUS", ...]
}
```

## 主要发现

### 重要国家状态
- **CHI (China)**: 🟢 活跃，🏛️ 文明化，文化：beifaren
- **JAP (Japan)**: 🟢 活跃，🏛️ 文明化
- **RUS (Russia)**: 🟢 活跃，🏛️ 文明化
- **USA (United States)**: 🟢 活跃，🏛️ 文明化
- **GER (Germany)**: 🔴 已灭亡，🏺 未文明化

### 文化分布统计
- `north_german`: 23个国家
- `north_italian`: 9个国家
- `central_american`: 7个国家
- `beifaren` (中国北方): 4个国家

## 使用示例

```bash
# 查看中国详细信息
python country_query.py CHI

# 查看所有活跃国家
python country_query.py active

# 搜索德国相关国家
python country_query.py german

# 显示所有国家代码
python country_query.py codes
```

## 总结

成功将`victoria2_main_modifier.py`中的国家查找逻辑提取为独立的工具包，提供了：
1. 完整的国家信息提取
2. 智能的国家识别
3. 便捷的查询界面
4. 结构化的数据输出

这套工具可以帮助分析维多利亚2存档中的国家状态，为游戏分析和修改提供数据支持。
