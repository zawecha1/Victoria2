#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人口清理逻辑测试工具
"""

import re

def test_population_cleanup_logic():
    """测试人口清理逻辑"""
    print("=" * 60)
    print("测试人口清理逻辑")
    print("=" * 60)
    
    filename = 'autosave.v2'
    
    # 加载文件
    try:
        with open(filename, 'r', encoding='latin1') as f:
            content = f.read()
        print(f"文件加载成功: {len(content):,} 字符")
    except Exception as e:
        print(f"加载失败: {e}")
        return
    
    # 分析中国的文化设置
    print("\n分析中国的文化设置...")
    china_pattern = re.compile(r'^CHI=\s*{', re.MULTILINE)
    china_match = china_pattern.search(content)
    
    if not china_match:
        print("错误: 未找到中国国家数据")
        return
    
    start_pos = china_match.end()
    next_country = re.search(r'\n[A-Z]{2,3}=\s*{', content[start_pos:start_pos+500000])
    if next_country:
        end_pos = start_pos + next_country.start()
    else:
        end_pos = start_pos + 400000
    
    china_content = content[start_pos:end_pos]
    
    # 提取主流文化
    primary_culture_match = re.search(r'primary_culture\s*=\s*"([a-z_]+)"', china_content)
    primary_culture = primary_culture_match.group(1) if primary_culture_match else 'beifaren'
    
    # 提取可接受文化
    accepted_cultures = []
    culture_block_match = re.search(r'culture\s*=\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', china_content, re.DOTALL)
    if culture_block_match:
        culture_block_content = culture_block_match.group(1)
        culture_names = re.findall(r'"([a-z_]+)"', culture_block_content)
        for culture in culture_names:
            if culture != "noculture" and culture != primary_culture:
                accepted_cultures.append(culture)
    
    print(f"中国主流文化: {primary_culture}")
    print(f"中国可接受文化: {accepted_cultures}")
    
    # 查找几个中国省份并测试人口分析
    print(f"\n测试中国省份的人口分析...")
    
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    china_provinces_tested = 0
    total_pops_found = 0
    kept_pops = 0
    removed_pops = 0
    
    for i, match in enumerate(province_matches):
        if china_provinces_tested >= 50:  # 只测试前50个中国省份
            break
            
        province_id = int(match.group(1))
        start_pos = match.end()
        
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+20000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 15000
        
        province_content = content[start_pos:end_pos]
        
        # 检查是否是中国省份
        if 'owner="CHI"' in province_content or 'owner=CHI' in province_content:
            china_provinces_tested += 1
            name_match = re.search(r'name="([^"]+)"', province_content)
            province_name = name_match.group(1) if name_match else f"Province_{province_id}"
            
            # 分析人口
            pop_types = ['aristocrats', 'artisans', 'bureaucrats', 'capitalists', 'clergymen', 
                        'clerks', 'craftsmen', 'farmers', 'labourers', 'officers', 'soldiers']
            
            province_pops = 0
            province_kept = 0
            province_removed = 0
            
            for pop_type in pop_types:
                start_pattern = rf'\b{pop_type}\s*=\s*{{'
                start_matches = list(re.finditer(start_pattern, province_content))
                
                for start_match in start_matches:
                    # 找到完整的人口块
                    brace_start = start_match.end() - 1
                    brace_count = 0
                    block_end = None
                    
                    for j in range(brace_start, len(province_content)):
                        char = province_content[j]
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                block_end = j + 1
                                break
                    
                    if block_end is None:
                        continue
                    
                    pop_block_start = start_match.start()
                    pop_content = province_content[pop_block_start:block_end]
                    province_pops += 1
                    total_pops_found += 1
                    
                    # 提取文化信息
                    culture = extract_culture_from_pop_block(pop_content)
                    
                    if culture:
                        if culture == primary_culture or culture in accepted_cultures:
                            province_kept += 1
                            kept_pops += 1
                        else:
                            province_removed += 1
                            removed_pops += 1
                            
                            # 显示一些删除的示例
                            if removed_pops <= 10:
                                size_match = re.search(r'\bsize\s*=\s*([0-9.]+)', pop_content)
                                size = float(size_match.group(1)) if size_match else 0
                                print(f"  删除示例 {removed_pops}: {province_name} - {pop_type}, 文化={culture}, 大小={size}")
                    else:
                        print(f"  警告: 无法识别文化 in {province_name} - {pop_type}")
            
            if province_removed > 0 and china_provinces_tested <= 5:
                print(f"省份 {province_name}: 总人口={province_pops}, 保留={province_kept}, 删除={province_removed}")
    
    print(f"\n测试总结:")
    print(f"测试的中国省份: {china_provinces_tested} 个")
    print(f"总人口单位: {total_pops_found} 个")
    print(f"保留人口: {kept_pops} 个")
    print(f"删除人口: {removed_pops} 个")
    print(f"删除比例: {removed_pops/total_pops_found*100:.1f}%" if total_pops_found > 0 else "N/A")

def extract_culture_from_pop_block(pop_content):
    """从人口块中提取文化信息"""
    # 查找 文化名=宗教名 格式
    culture_pattern = r'\s+([a-z_]+)\s*=\s*([a-z_]+)'
    culture_matches = re.findall(culture_pattern, pop_content)
    
    # 系统字段列表
    system_fields = {
        'id', 'size', 'money', 'ideology', 'issues', 
        'consciousness', 'militancy', 'type', 'rebel'
    }
    
    for potential_culture, religion in culture_matches:
        if potential_culture not in system_fields:
            if len(potential_culture) <= 15 and potential_culture.replace('_', '').isalpha():
                return potential_culture
    
    return None

if __name__ == "__main__":
    test_population_cleanup_logic()
