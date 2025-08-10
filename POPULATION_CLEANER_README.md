# Victoria II 中国人口清理工具使用说明

## 功能描述
这个工具可以安全地删除中国境内所有非主流文化和非可接受文化的人口，实现文化同化。

## 主要特性
- **安全检测**: 自动识别中国的主流文化(beifaren)和可接受文化
- **智能分析**: 扫描所有中国拥有的省份和人口数据
- **详细预览**: 执行前显示完整的删除计划和统计信息
- **自动备份**: 执行前自动创建备份文件
- **数据完整性**: 执行后验证花括号平衡，确保存档不损坏

## 使用方法

### 1. 预览模式（推荐先使用）
```bash
python china_population_cleaner.py <存档文件> preview
```
或者
```bash
python china_population_cleaner.py <存档文件>  # 默认为预览模式
```

### 2. 执行模式
```bash
python china_population_cleaner.py <存档文件> execute
```

## 使用示例

### 预览清理计划
```bash
python china_population_cleaner.py ChinaUseIt.v2 preview
```

### 实际执行清理
```bash
python china_population_cleaner.py ChinaUseIt.v2 execute
```

## 输出结果
- **预览模式**: 生成详细报告JSON文件，包含所有将要删除的人口信息
- **执行模式**: 创建备份文件，修改原存档，生成执行报告

## 安全提示
1. **强烈建议先在预览模式下查看清理计划**
2. **执行前手动备份重要存档文件**
3. **程序会自动创建带时间戳的备份文件**
4. **如果出现问题，可以从备份文件恢复**

## 典型使用流程
1. 先运行预览模式查看将要删除的人口
2. 检查报告确认删除计划正确
3. 手动备份存档（可选但推荐）
4. 运行执行模式进行实际清理
5. 在游戏中测试修改后的存档

## 清理统计示例
```
保留文化:
  主流文化: beifaren
  可接受文化: 无

统计信息:
  受影响省份: 714 个
  删除人口单位: 3347 个
  删除人口总数: 8901532

按文化统计:
   1. manchu: 986 个人口单位     # 满族
   2. yankee: 915 个人口单位     # 美国佬
   3. nanfaren: 309 个人口单位   # 南方汉族
   4. dixie: 164 个人口单位      # 南方美国人
   5. russian: 154 个人口单位    # 俄罗斯人
```

## 文件命名说明
- 备份文件: `原文件名.backup_时间戳`
- 预览报告: `china_population_cleanup_plan_时间戳_preview.json`
- 执行报告: `population_cleanup_report_时间戳.json`

## 技术说明
- 支持latin1编码的Victoria II存档文件
- 使用括号平衡检测确保文件完整性
- 按位置倒序删除避免位置偏移问题
- 保留所有beifaren(北方汉族)文化的人口
