#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复后的存档文件完整性
"""

def verify_file_integrity(filename):
    """验证文件完整性"""
    print(f"验证文件: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return False
    
    print(f"文件大小: {len(content):,} 字符")
    
    # 检查大括号匹配
    open_braces = content.count('{')
    close_braces = content.count('}')
    print(f"大括号匹配: {open_braces} 开 / {close_braces} 闭 (差值: {open_braces - close_braces})")
    
    if open_braces != close_braces + 1:  # Victoria II文件通常是开括号比闭括号多1个
        print("⚠️ 大括号不匹配，可能有语法错误")
    else:
        print("✅ 大括号匹配正常")
    
    # 检查CHI块
    import re
    chi_blocks = len(re.findall(r'\nCHI=\s*\{', content))
    print(f"CHI块数量: {chi_blocks}")
    
    # 查找真正的CHI国家块
    china_pattern = r'\nCHI=\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*(?:primary_culture|capital|technology|ruling_party|upper_house|consciousness|nonstate_consciousness|schools|political_reform_want|social_reform_want|government|plurality|revanchism|war_policy|economic_policy|trade_policy|religious_policy|citizenship_policy|war_exhaustion|badboy|mobilized|created_from|ai)'
    china_matches = list(re.finditer(china_pattern, content, re.DOTALL))
    
    print(f"真正的CHI国家块: {len(china_matches)} 个")
    
    if china_matches:
        match = china_matches[0]
        start_pos = match.start()
        next_country = re.search(r'\n[A-Z]{3}=\s*{', content[start_pos + 100:])
        end_pos = start_pos + 100 + next_country.start() if next_country else len(content)
        
        chi_block = content[start_pos:end_pos]
        print(f"CHI块位置: {start_pos}-{end_pos}")
        print(f"CHI块大小: {len(chi_block):,} 字符")
        
        # 检查文化设置
        primary_culture = re.search(r'primary_culture="?([^"\s]+)"?', chi_block)
        accepted_cultures = re.findall(r'"([^"]+)"', re.search(r'culture=\s*\{([^}]+)\}', chi_block, re.DOTALL).group(1) if re.search(r'culture=\s*\{([^}]+)\}', chi_block, re.DOTALL) else "")
        badboy = re.search(r'badboy=([\d.]+)', chi_block)
        
        print(f"主文化: {primary_culture.group(1) if primary_culture else '未设置'}")
        print(f"接受文化: {accepted_cultures if accepted_cultures else '未设置'}")
        print(f"恶名度: {badboy.group(1) if badboy else '未设置'}")
    
    return True

def main():
    print("=" * 60)
    print("验证修复后的存档文件完整性")
    print("=" * 60)
    
    current_file = "China2281_01_01.v2"
    backup_file = "China2281_01_01_unified_backup_20250728_225649.v2"
    
    print("当前文件:")
    verify_file_integrity(current_file)
    
    print("\n" + "-" * 40)
    print("备份文件:")
    verify_file_integrity(backup_file)
    
    print("\n" + "=" * 60)
    print("验证完成")

if __name__ == "__main__":
    main()
