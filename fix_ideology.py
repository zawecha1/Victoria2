#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复意识形态修改的直接补丁
"""

import re
import shutil
from datetime import datetime

def fix_ideology_modification():
    """直接修复意识形态修改问题"""
    
    print("🔧 直接修复意识形态修改问题")
    print("=" * 50)
    
    filename = 'China1837_01_24.v2'
    
    # 创建备份
    backup_filename = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filename, backup_filename)
    print(f"📁 已创建备份: {backup_filename}")
    
    # 读取文件
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        print(f"✅ 文件读取成功，大小: {len(content):,}")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return False
    
    # 意识形态映射
    ideology_mapping = {1: 3, 2: 6, 4: 3, 5: 6, 7: 3}
    
    # 查找中国省份（1-29）
    modification_count = 0
    
    for province_id in range(1, 30):
        print(f"🔍 处理省份 {province_id}...")
        
        # 查找省份
        province_pattern = f'^{province_id}=\\s*{{'
        province_match = re.search(province_pattern, content, re.MULTILINE)
        
        if not province_match:
            continue
        
        # 提取省份内容
        start_pos = province_match.end()
        brace_count = 1
        current_pos = start_pos
        while current_pos < len(content) and brace_count > 0:
            char = content[current_pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            current_pos += 1
        
        province_content = content[start_pos:current_pos-1]
        
        # 查找该省份中所有的ideology块
        ideology_pattern = r'ideology=\s*\{([^}]*)\}'
        ideology_matches = list(re.finditer(ideology_pattern, province_content, re.DOTALL))
        
        for match in ideology_matches:
            ideology_content = match.group(1)
            
            # 解析意识形态数据
            ideology_pairs = re.findall(r'(\d+)=([\d.]+)', ideology_content)
            ideology_dist = {int(id_str): float(value_str) for id_str, value_str in ideology_pairs}
            
            # 检查是否需要转换
            needs_conversion = any(ideology_dist.get(old_id, 0) > 0 for old_id in [1, 2, 4, 5, 7])
            
            if needs_conversion:
                # 应用转换
                transferred_to_liberal = 0.0
                transferred_to_conservative = 0.0
                
                for old_id, new_id in ideology_mapping.items():
                    if old_id in ideology_dist and ideology_dist[old_id] > 0:
                        value = ideology_dist[old_id]
                        
                        if new_id == 6:  # Liberal
                            transferred_to_liberal += value
                        elif new_id == 3:  # Conservative  
                            transferred_to_conservative += value
                        
                        ideology_dist[old_id] = 0.0
                
                # 更新目标意识形态的值
                if transferred_to_liberal > 0:
                    ideology_dist[6] = ideology_dist.get(6, 0) + transferred_to_liberal
                
                if transferred_to_conservative > 0:
                    ideology_dist[3] = ideology_dist.get(3, 0) + transferred_to_conservative
                
                # 生成新的内容
                new_content_lines = []
                for ideology_id in range(1, 8):
                    value = ideology_dist.get(ideology_id, 0.0)
                    formatted_value = f"{value:.5f}"
                    new_content_lines.append(f"{ideology_id}={formatted_value}")
                
                # 保持原有的缩进格式
                new_ideology_content = '\n'.join(new_content_lines)
                
                # 构建新的ideology块
                new_ideology_block = f'ideology=\n\t\t{{\n\t\t{new_ideology_content}\n\t\t}}'
                old_ideology_block = match.group(0)
                
                # 在整个内容中替换
                content = content.replace(old_ideology_block, new_ideology_block)
                modification_count += 1
                
                print(f"  ✅ 修改了1个意识形态块")
    
    # 保存修改后的文件
    if modification_count > 0:
        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            print(f"\n✅ 文件保存成功")
            print(f"📊 总共修改了 {modification_count} 个意识形态块")
            return True
        except Exception as e:
            print(f"❌ 文件保存失败: {e}")
            return False
    else:
        print("\n❌ 没有找到需要修改的意识形态块")
        return False

if __name__ == "__main__":
    success = fix_ideology_modification()
    if success:
        print("\n🎉 修复完成！请运行验证脚本检查结果。")
    else:
        print("\n❌ 修复失败！")
