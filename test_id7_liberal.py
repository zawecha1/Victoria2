#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试ID 7为Liberal
"""

from test_id6_liberal import ChinesePopulationModifier_TestID6
import shutil

class ChinesePopulationModifier_TestID7(ChinesePopulationModifier_TestID6):
    """测试Liberal=ID 7的修改器"""
    
    def __init__(self):
        super().__init__()
        
        # 意识形态映射规则 (测试方案C: Liberal = ID 7)
        self.ideology_mapping = {
            # 基于游戏结果分析：ID 1=Reactionary, ID 2=Fascist, ID 3=Conservative, ID 4=Socialist
            # 测试假设：ID 7=Liberal
            1: 3,  # Reactionary(1) -> Conservative(3)
            2: 7,  # Fascist(2) -> Liberal(7) - 测试ID 7是Liberal
            4: 3,  # Socialist(4) -> Conservative(3)  
            5: 7,  # Anarcho-Liberal(5) -> Liberal(7) - 测试ID 7是Liberal
            6: 3   # (原来的Anarcho-Liberal) -> Conservative(3)
        }
    
    def create_backup(self, filename: str) -> str:
        """创建备份文件"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename.replace('.v2', '')}_backup_id7_test_{timestamp}.v2"
        print(f"创建备份文件: {backup_filename}")
        shutil.copy2(filename, backup_filename)
        return backup_filename
    
    def modify_chinese_populations(self, filename: str) -> bool:
        """修改中国人口的宗教和意识形态"""
        print(f"\n{'='*70}")
        print("中国人口属性修改器 - 测试Liberal=ID 7")
        print(f"{'='*70}")
        print(f"目标文件: {filename}")
        print("修改内容:")
        print("- 所有中国人口宗教 → mahayana")
        print("- 意识形态调整 (测试Liberal=ID 7):")
        print("  • Reactionary(1) + Socialist(4) + Anarcho-Liberal(6) → Conservative(3)")
        print("  • Fascist(2) + (原ID 5) → Liberal(7)")
        print(f"{'='*70}")
        
        return super().modify_chinese_populations(filename)
    
    def _modify_ideology_distribution(self, ideology_content: str) -> str:
        """修改意识形态分布"""
        # 解析现有的意识形态分布
        import re
        ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
        ideology_dist = {}
        
        for id_str, value_str in ideology_pairs:
            ideology_dist[int(id_str)] = float(value_str)
        
        # 应用转换规则
        total_transferred = 0.0
        transferred_to_liberal = 0.0
        transferred_to_conservative = 0.0
        
        for old_id, new_id in self.ideology_mapping.items():
            if old_id in ideology_dist:
                value = ideology_dist[old_id]
                total_transferred += value
                
                if new_id == 7:  # Liberal = ID 7 (测试中)
                    transferred_to_liberal += value
                elif new_id == 3:  # Conservative = ID 3
                    transferred_to_conservative += value
                
                # 将原意识形态设为0
                ideology_dist[old_id] = 0.0
        
        # 增加目标意识形态的值
        if transferred_to_liberal > 0:
            ideology_dist[7] = ideology_dist.get(7, 0.0) + transferred_to_liberal  # Liberal = ID 7 (测试中)
        
        if transferred_to_conservative > 0:
            ideology_dist[3] = ideology_dist.get(3, 0.0) + transferred_to_conservative  # Conservative = ID 3
        
        # 重新构建意识形态内容，保持原有格式
        new_lines = []
        for ideology_id in sorted(ideology_dist.keys()):
            value = ideology_dist[ideology_id]
            new_lines.append(f'{ideology_id}={value:.5f}')
        
        # 保持原有的格式：没有缩进的数值行，最后有制表符缩进的结束大括号
        return '\n'.join(new_lines) + '\n\t\t'

def test_id7_liberal(source_file, test_file):
    """测试ID 7为Liberal的非交互式版本"""
    
    print("🧪 意识形态映射测试 (Liberal = ID 7)")
    print("="*50)
    
    # 复制源文件到测试文件
    print(f"复制 {source_file} 到 {test_file}")
    shutil.copy2(source_file, test_file)
    
    # 创建修改器实例
    modifier = ChinesePopulationModifier_TestID7()
    
    # 执行修改
    success = modifier.modify_chinese_populations(test_file)
    
    if success:
        print("\n✅ 测试修改成功!")
        print("📁 备份文件已创建")
        
        # 显示统计信息
        print(f"\n📊 修改统计:")
        print(f"宗教修改: {modifier.religion_changes} 处")
        print(f"意识形态修改: {modifier.ideology_changes} 处")
        print(f"总修改数: {modifier.modifications_count} 个人口组")
        
        return True
    else:
        print("\n❌ 测试修改失败!")
        return False

def main():
    """主函数"""
    import sys
    import os
    
    if len(sys.argv) < 2:
        print("用法: python test_id7_liberal.py <源文件> [测试文件名]")
        print("示例: python test_id7_liberal.py China2245_04_06.v2 test_liberal_id7.v2")
        return
    
    source_file = sys.argv[1]
    test_file = sys.argv[2] if len(sys.argv) > 2 else "test_liberal_id7.v2"
    
    # 检查源文件是否存在
    if not os.path.exists(source_file):
        print(f"❌ 源文件不存在: {source_file}")
        return
    
    # 执行测试
    success = test_id7_liberal(source_file, test_file)
    
    if success:
        print(f"\n🎯 测试完成！请检查文件: {test_file}")
        print("💡 可以用以下命令检查结果:")
        print(f"   python check_single_file.py {test_file} 3")
    else:
        print("\n❌ 测试失败!")

if __name__ == "__main__":
    main()
