#!/usr/bin/env python3
"""
检查和设置中国的文明化状态
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from victoria2_main_modifier import Victoria2Modifier

def check_and_set_china_civilized():
    """检查和设置中国的文明化状态为yes"""
    print("🇨🇳 检查中国的文明化状态")
    print("="*50)
    
    try:
        # 初始化修改器
        modifier = Victoria2Modifier("autosave.v2")
        
        # 查找中国块
        country_blocks = modifier.find_blocks_by_function_type('countries')
        china_block = None
        
        for block in country_blocks:
            if block.name == "CHI":
                china_block = block
                break
        
        if not china_block:
            print("❌ 未找到中国(CHI)块")
            return False
        
        print("✅ 找到中国块")
        
        # 检查当前的civilized状态
        import re
        civilized_match = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', china_block.content)
        
        if civilized_match:
            current_status = civilized_match.group(1)
            print(f"📊 当前状态: civilized={current_status}")
            
            if current_status == "yes":
                print("✅ 中国已经是文明化状态")
                return True
            else:
                print(f"🔧 需要修改: {current_status} → yes")
        else:
            print("📊 当前状态: 无civilized字段")
            print("🔧 需要添加: civilized=yes")
        
        # 修改为civilized=yes
        print("🔧 正在设置中国为文明化状态...")
        
        modifications = {"civilized": '"yes"'}
        if modifier.modify_block_content_safely(china_block, modifications):
            print("✅ 中国文明化状态修改成功!")
            
            # 保存文件
            import datetime
            timestamp = datetime.datetime.now().strftime("%H%M%S")
            output_file = f"autosave_china_civilized_{timestamp}.v2"
            modifier.save_file(output_file)
            print(f"📁 文件已保存为: {output_file}")
            
            # 验证修改
            print("🔍 验证修改结果...")
            civilized_match_new = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', china_block.content)
            if civilized_match_new:
                new_status = civilized_match_new.group(1)
                print(f"✅ 验证成功: civilized={new_status}")
            else:
                print("❌ 验证失败: 未找到civilized字段")
                
            return True
        else:
            print("❌ 中国文明化状态修改失败")
            return False
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_other_countries_status():
    """检查其他主要国家的文明化状态"""
    print(f"\n📊 检查其他主要国家的文明化状态")
    print("="*50)
    
    try:
        modifier = Victoria2Modifier("autosave.v2")
        country_blocks = modifier.find_blocks_by_function_type('countries')
        
        # 主要国家列表
        major_countries = ["ENG", "FRA", "RUS", "PRU", "GER", "AUS", "USA", "JAP"]
        
        print("主要国家文明化状态:")
        for country_code in major_countries:
            for block in country_blocks:
                if block.name == country_code:
                    import re
                    civilized_match = re.search(r'civilized\s*=\s*"?([^"\s}]+)"?', block.content)
                    if civilized_match:
                        status = civilized_match.group(1)
                        print(f"  {country_code}: {status}")
                    else:
                        print(f"  {country_code}: 未设置")
                    break
            else:
                print(f"  {country_code}: 未找到")
    
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    success = check_and_set_china_civilized()
    check_other_countries_status()
    
    if success:
        print(f"\n🎉 中国文明化状态设置完成!")
    else:
        print(f"\n❌ 中国文明化状态设置失败!")
