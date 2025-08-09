#!/usr/bin/env python3
"""
检查modify_block_content_safely方法是否破坏了文件内容
"""

import re
import os

def check_file_integrity():
    """检查文件完整性"""
    print("🔍 检查文件完整性问题")
    print("="*60)
    
    files_to_check = ["autosave.v2", "test_civilized_simple_143915.v2"]
    
    for filename in files_to_check:
        if not os.path.exists(filename):
            print(f"❌ 文件不存在: {filename}")
            continue
            
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
            
            print(f"\n📄 {filename}:")
            print(f"  文件大小: {len(content):,} 字符")
            
            # 检查括号平衡
            open_braces = content.count('{')
            close_braces = content.count('}')
            print(f"  花括号: 开 {open_braces}, 闭 {close_braces}, 平衡: {'✅' if open_braces == close_braces else '❌'}")
            
            # 检查基本结构完整性
            # 查找关键块是否存在
            key_blocks = {
                '省份块': r'\d{3,4}\s*=\s*\{',
                '人口块': r'\d+\s*=\s*\{[^{}]*?size\s*=',
                '国家块': r'[A-Z]{2,3}\s*=\s*\{[^{}]*?capital\s*=',
                'size字段': r'size\s*=\s*[\d.]+',
                'culture字段': r'culture\s*=\s*\w+',
                'type字段': r'type\s*=\s*\d+'
            }
            
            for block_name, pattern in key_blocks.items():
                matches = re.findall(pattern, content, re.DOTALL)
                print(f"  {block_name}: {len(matches)}")
            
            # 检查是否有损坏的块标记
            corrupted_patterns = [
                r'\{\s*\{\s*\{',  # 三重花括号
                r'\}\s*\}\s*\}',  # 三重结束花括号
                r'=\s*=',         # 双等号
                r'\{\s*\}',       # 空块（可能正常，但要统计）
            ]
            
            corruption_found = False
            for i, pattern in enumerate(corrupted_patterns):
                matches = re.findall(pattern, content)
                if matches and i < 2:  # 前两个是明确的损坏模式
                    print(f"  ⚠️ 可能损坏: {['三重开括号', '三重闭括号', '双等号', '空块'][i]}: {len(matches)}")
                    corruption_found = True
                elif matches:
                    print(f"  ℹ️ {['三重开括号', '三重闭括号', '双等号', '空块'][i]}: {len(matches)}")
            
            if not corruption_found:
                print(f"  ✅ 没有发现明显的结构损坏")
                
        except Exception as e:
            print(f"❌ 检查 {filename} 时出错: {e}")

def check_population_loss():
    """具体检查人口丢失问题"""
    print(f"\n" + "="*60)
    print("🔍 检查人口丢失问题")
    print("="*60)
    
    files = {
        "autosave.v2": "主程序修改后",
        "test_civilized_simple_143915.v2": "简单测试修改后"
    }
    
    results = {}
    
    for filename, description in files.items():
        if not os.path.exists(filename):
            continue
            
        try:
            with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
            
            # 统计人口相关数据
            size_matches = re.findall(r'size\s*=\s*([\d.]+)', content)
            sizes = [float(x) for x in size_matches if float(x) > 0]
            
            results[filename] = {
                'description': description,
                'size_count': len(size_matches),
                'non_zero_pop': len(sizes),
                'total_pop': sum(sizes) if sizes else 0,
                'avg_pop': sum(sizes) / len(sizes) if sizes else 0
            }
            
            print(f"\n📊 {description} ({filename}):")
            print(f"  size字段总数: {len(size_matches)}")
            print(f"  非零人口数: {len(sizes)}")
            print(f"  总人口: {sum(sizes):,.0f}")
            print(f"  平均人口: {sum(sizes) / len(sizes) if sizes else 0:.1f}")
            
        except Exception as e:
            print(f"❌ 检查 {filename} 时出错: {e}")
    
    # 比较结果
    if len(results) == 2:
        files_list = list(results.keys())
        autosave_result = results[files_list[0]]
        test_result = results[files_list[1]]
        
        print(f"\n📈 对比分析:")
        pop_diff = autosave_result['total_pop'] - test_result['total_pop']
        count_diff = autosave_result['size_count'] - test_result['size_count']
        
        print(f"  人口数差异: {pop_diff:+,.0f}")
        print(f"  size字段差异: {count_diff:+d}")
        
        if abs(pop_diff) > 1000000:
            print(f"  ❌ 严重的人口丢失问题!")
        elif abs(count_diff) > 100:
            print(f"  ⚠️ 人口块数量异常!")
        else:
            print(f"  ✅ 人口数据基本正常")

if __name__ == "__main__":
    check_file_integrity()
    check_population_loss()
