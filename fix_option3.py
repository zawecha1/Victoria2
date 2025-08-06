#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复选项3功能：完整实现中国=0，其他=10的斗争性修改
"""

def generate_fixed_modify_militancy():
    """生成修复后的modify_militancy方法代码"""
    return '''    def modify_militancy(self, china_militancy: float = 0.0, other_militancy: float = 10.0) -> bool:
        """修改人口忠诚度 - 中国省份loyalty_value设为0，其他国家设为10"""
        print(f"\\n⚔️ 开始修改人口忠诚度 (中国: {china_militancy}, 其他: {other_militancy})")
        print(f"💡 注意: 实际修改的是loyalty_value字段 (Victoria II中的忠诚度/斗争性指标)")
        
        # 获取中国省份列表
        chinese_provinces = set(self.find_chinese_provinces())
        if self.debug_mode:
            print(f"🎯 找到中国省份: {sorted(list(chinese_provinces))}")
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\\d+)=\\s*{', re.MULTILINE)
        
        # 获取所有省份
        all_provinces = []
        province_matches = list(province_pattern.finditer(self.content))
        
        print(f"📊 总共找到 {len(province_matches)} 个省份")
        
        # 收集所有省份ID
        for match in province_matches:
            province_id = int(match.group(1))
            all_provinces.append(province_id)
        
        # 分类省份：中国 vs 非中国
        non_chinese_provinces = [pid for pid in all_provinces if pid not in chinese_provinces]
        
        print(f"🎯 中国省份数量: {len(chinese_provinces)}")
        print(f"🌍 非中国省份数量: {len(non_chinese_provinces)}")
        
        # 第一步：处理中国省份 (设为china_militancy，通常是0)
        print(f"🔄 步骤1: 处理中国省份 ({len(chinese_provinces)}个) -> {china_militancy}")
        chinese_processed = 0
        for province_id in sorted(chinese_provinces):
            if self.debug_mode:
                print(f"  🔄 处理中国省份 {province_id}")
            
            if self._modify_single_province_loyalty(province_id, china_militancy):
                chinese_processed += 1
        
        print(f"✅ 中国省份处理完成: {chinese_processed}/{len(chinese_provinces)} 个省份")
        
        # 第二步：处理非中国省份 (设为other_militancy，通常是10)
        print(f"🔄 步骤2: 处理非中国省份 ({len(non_chinese_provinces)}个) -> {other_militancy}")
        non_chinese_processed = 0
        for i, province_id in enumerate(sorted(non_chinese_provinces)):
            if self.debug_mode and i % 200 == 0:  # 每200个省份输出一次进度
                print(f"  🌍 进度: {i}/{len(non_chinese_provinces)} ({i/len(non_chinese_provinces)*100:.1f}%)")
            
            if self._modify_single_province_loyalty(province_id, other_militancy):
                non_chinese_processed += 1
        
        print(f"✅ 非中国省份处理完成: {non_chinese_processed}/{len(non_chinese_provinces)} 个省份")
        
        total_processed = chinese_processed + non_chinese_processed
        print(f"✅ 忠诚度修改完成: 总共处理 {total_processed} 个省份，修改 {self.militancy_changes} 处loyalty_value")
        return True'''

if __name__ == "__main__":
    print("🔧 修复选项3功能：完整实现中国=0，其他=10的斗争性修改")
    print("=" * 60)
    
    print("\n📋 新功能说明:")
    print("✅ 中国省份 (2687-2740): loyalty_value 设为 0.0")
    print("✅ 非中国省份 (所有其他): loyalty_value 设为 10.0") 
    print("✅ 显示详细处理进度")
    print("✅ 统计实际修改数量")
    
    print("\n🔄 生成修复后的代码...")
    fixed_code = generate_fixed_modify_militancy()
    
    print("✅ 代码生成完成!")
    print("📝 需要将此代码替换原 modify_militancy 方法")
