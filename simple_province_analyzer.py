#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版国家省份分析器 (simple_province_analyzer.py)
=================================================
快速分析Victoria II存档中每个国家的省份分布

使用方法:
    python simple_province_analyzer.py [存档文件名]
    
如果不指定文件名，将自动使用 autosave.v2
"""

import sys
import os
from victoria2_main_modifier import Victoria2Modifier

def analyze_provinces(filename='autosave.v2'):
    """执行省份分析"""
    if not os.path.exists(filename):
        print(f"❌ 未找到文件: {filename}")
        return False
    
    print(f"🔍 分析文件: {filename}")
    
    try:
        # 创建修改器实例
        modifier = Victoria2Modifier(filename, debug_mode=False)
        
        # 执行分析
        result_file = modifier.save_countries_provinces_analysis()
        
        if result_file:
            print(f"✅ 分析完成，结果保存到: {result_file}")
            return True
        else:
            print("❌ 分析失败")
            return False
            
    except Exception as e:
        print(f"❌ 分析出错: {e}")
        return False

def main():
    """主函数"""
    print("🌍 Victoria II 省份分析器")
    print("=" * 30)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'autosave.v2'
    
    # 执行分析
    success = analyze_provinces(filename)
    
    if success:
        print("\n🎉 分析成功完成！")
    else:
        print("\n💥 分析失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
