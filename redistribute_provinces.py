#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国家省份重分配工具 (redistribute_provinces.py)
==============================================
分析国家结构，保留各国首都，其余省份分配给中国

功能:
1. 分析所有国家的省份分布
2. 保护每个国家的首都省份（优先策略）
3. 将非首都省份重新分配给中国
4. 保持核心声明不变
5. 自动备份和完整性检查
6. 确保每个国家至少保留一个省份

使用方法:
    python redistribute_provinces.py [模式]
    
模式:
    preview  - 仅预览，不修改 (默认)
    execute  - 实际执行重分配
"""

from victoria2_main_modifier import Victoria2Modifier
import sys
import os
import re
from typing import Dict, List, Tuple

class ProvinceRedistributor:
    """省份重分配器"""
    
    def __init__(self, filename: str):
        self.modifier = Victoria2Modifier(filename, debug_mode=True)
        self.content = self.modifier.content
        
    def analyze_country_provinces(self) -> Dict[str, Dict]:
        """分析各国的省份分布"""
        print("🔍 分析国家省份分布...")
        
        # 查找所有省份
        province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
        province_matches = list(province_pattern.finditer(self.content))
        
        countries_data = {}
        provinces_data = {}
        
        for i, match in enumerate(province_matches):
            province_id = int(match.group(1))
            start_pos = match.end()
            
            # 确定省份块的结束位置
            if i + 1 < len(province_matches):
                end_pos = province_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+20000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 10000
            
            province_content = self.content[start_pos:end_pos]
            
            # 提取省份信息
            province_info = {
                'id': province_id,
                'name': 'Unknown',
                'owner': None,
                'controller': None,
                'cores': [],
                'is_capital': False,
                'start_pos': match.start(),
                'end_pos': end_pos,
                'content': province_content
            }
            
            # 查找省份名称
            name_match = re.search(r'name="([^"]+)"', province_content)
            if name_match:
                province_info['name'] = name_match.group(1)
            
            # 查找拥有者
            owner_match = re.search(r'owner="?([A-Z]{2,3})"?', province_content)
            if owner_match:
                province_info['owner'] = owner_match.group(1)
            
            # 查找控制者
            controller_match = re.search(r'controller="?([A-Z]{2,3})"?', province_content)
            if controller_match:
                province_info['controller'] = controller_match.group(1)
            
            # 查找核心声明
            core_matches = re.findall(r'core="?([A-Z]{2,3})"?', province_content)
            province_info['cores'] = core_matches
            
            provinces_data[province_id] = province_info
            
            # 如果有拥有者，添加到相应国家
            if province_info['owner']:
                owner = province_info['owner']
                if owner not in countries_data:
                    countries_data[owner] = {
                        'tag': owner,
                        'provinces': [],
                        'capital_province': None
                    }
                countries_data[owner]['provinces'].append(province_id)
            
            # 显示进度
            if (i + 1) % 500 == 0:
                print(f"  处理进度: {i + 1}/{len(province_matches)} ({(i + 1)/len(province_matches)*100:.1f}%)")
        
        # 为每个国家确定首都省份
        self._determine_capitals(countries_data, provinces_data)
        
        print(f"✅ 分析完成: {len(countries_data)} 个国家, {len(provinces_data)} 个省份")
        return countries_data, provinces_data
    
    def _determine_capitals(self, countries_data: Dict, provinces_data: Dict):
        """为每个国家确定首都省份"""
        print("🏛️ 确定各国首都...")
        
        # 查找各国的首都信息
        country_pattern = re.compile(r'^([A-Z]{2,3})=\s*{', re.MULTILINE)
        country_matches = list(country_pattern.finditer(self.content))
        
        for i, match in enumerate(country_matches):
            country_tag = match.group(1)
            start_pos = match.end()
            
            if i + 1 < len(country_matches):
                end_pos = country_matches[i + 1].start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', self.content[start_pos:start_pos+50000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 30000
            
            country_content = self.content[start_pos:end_pos]
            
            # 查找首都
            capital_match = re.search(r'capital=(\d+)', country_content)
            if capital_match and country_tag in countries_data:
                capital_id = int(capital_match.group(1))
                countries_data[country_tag]['capital_province'] = capital_id
                
                # 标记省份为首都
                if capital_id in provinces_data:
                    provinces_data[capital_id]['is_capital'] = True
    
    def plan_redistribution(self, countries_data: Dict, provinces_data: Dict) -> Dict:
        """规划省份重分配方案"""
        print("📋 规划省份重分配方案...")
        
        redistribution_plan = {
            'kept_provinces': {},      # 各国保留的省份
            'transferred_provinces': [], # 转移给中国的省份
            'china_gains': 0,          # 中国获得的省份数
            'affected_countries': 0,     # 受影响的国家数
            'capital_protected': 0,     # 首都保护的国家数
            'no_capital_countries': []  # 没有首都的国家
        }
        
        for country_tag, country_info in countries_data.items():
            if country_tag == 'CHI':  # 跳过中国
                continue
                
            provinces = country_info['provinces']
            capital = country_info['capital_province']
            
            # 检查国家是否有省份
            if not provinces:
                print(f"⚠️ {country_tag}: 没有省份，跳过")
                continue
            
            # 强制保留首都（如果存在且在拥有的省份中）
            if capital and capital in provinces:
                kept_province = capital
                redistribution_plan['capital_protected'] += 1
                print(f"🏛️ {country_tag}: 保护首都 {capital} ({provinces_data[capital]['name']})")
            else:
                # 如果没有首都或首都不在拥有省份中，保留第一个省份
                kept_province = provinces[0]
                redistribution_plan['no_capital_countries'].append(country_tag)
                print(f"⚠️ {country_tag}: 没有有效首都，保留省份 {kept_province} ({provinces_data[kept_province]['name']})")
            
            redistribution_plan['kept_provinces'][country_tag] = {
                'province_id': kept_province,
                'province_name': provinces_data[kept_province]['name'],
                'is_capital': capital == kept_province,
                'reason': 'capital' if capital == kept_province else 'fallback'
            }
            
            # 如果有多于一个省份，其余省份转移给中国
            if len(provinces) > 1:
                redistribution_plan['affected_countries'] += 1
                
                for province_id in provinces:
                    if province_id != kept_province:
                        redistribution_plan['transferred_provinces'].append({
                            'province_id': province_id,
                            'province_name': provinces_data[province_id]['name'],
                            'original_owner': country_tag,
                            'cores': provinces_data[province_id]['cores']
                        })
                        redistribution_plan['china_gains'] += 1
        
        # 统计信息
        print(f"📊 重分配方案统计:")
        print(f"   总国家数: {len(countries_data)} 个")
        print(f"   首都保护: {redistribution_plan['capital_protected']} 个国家")
        print(f"   无首都国家: {len(redistribution_plan['no_capital_countries'])} 个")
        print(f"   受影响国家: {redistribution_plan['affected_countries']} 个")
        print(f"   中国将获得: {redistribution_plan['china_gains']} 个省份")
        print(f"   保留省份的国家: {len(redistribution_plan['kept_provinces'])} 个")
        
        if redistribution_plan['no_capital_countries']:
            print(f"⚠️ 无有效首都的国家: {', '.join(redistribution_plan['no_capital_countries'][:10])}")
            if len(redistribution_plan['no_capital_countries']) > 10:
                print(f"   ... 还有 {len(redistribution_plan['no_capital_countries']) - 10} 个")
        
        return redistribution_plan
    
    def preview_redistribution(self) -> Dict:
        """预览重分配方案"""
        print("🔍 省份重分配预览模式")
        print("=" * 40)
        
        # 分析当前状态
        countries_data, provinces_data = self.analyze_country_provinces()
        
        # 规划重分配
        plan = self.plan_redistribution(countries_data, provinces_data)
        
        # 显示详细信息
        print(f"\\n🏆 主要受益者 - 中国(CHI):")
        china_provinces = countries_data.get('CHI', {}).get('provinces', [])
        print(f"   当前省份: {len(china_provinces)} 个")
        print(f"   将获得: {plan['china_gains']} 个省份")
        print(f"   重分配后: {len(china_provinces) + plan['china_gains']} 个省份")
        
        print(f"\\n📋 各国保留的省份 (前20个):")
        kept_items = list(plan['kept_provinces'].items())[:20]
        for i, (country_tag, info) in enumerate(kept_items, 1):
            if info['reason'] == 'capital':
                status_mark = " (首都) ✅"
            else:
                status_mark = " (替代) ⚠️"
            print(f"   {i:2d}. {country_tag}: {info['province_name']}{status_mark}")
        
        if len(plan['kept_provinces']) > 20:
            print(f"   ... 还有 {len(plan['kept_provinces']) - 20} 个国家")
        
        # 显示首都保护统计
        print(f"\\n🏛️ 首都保护统计:")
        print(f"   首都保护成功: {plan['capital_protected']} 个国家")
        print(f"   使用替代省份: {len(plan['no_capital_countries'])} 个国家")
        if plan['no_capital_countries']:
            print(f"   无有效首都: {', '.join(plan['no_capital_countries'][:5])}")
            if len(plan['no_capital_countries']) > 5:
                print(f"                 ... 还有 {len(plan['no_capital_countries']) - 5} 个")
        
        print(f"\\n🔄 转移给中国的省份 (前20个):")
        transferred_items = plan['transferred_provinces'][:20]
        for i, info in enumerate(transferred_items, 1):
            cores_str = f" (核心:{','.join(info['cores'][:3])})" if info['cores'] else ""
            print(f"   {i:2d}. {info['province_name']} <- {info['original_owner']}{cores_str}")
        
        if len(plan['transferred_provinces']) > 20:
            print(f"   ... 还有 {len(plan['transferred_provinces']) - 20} 个省份")
        
        return {
            'countries_data': countries_data,
            'provinces_data': provinces_data,
            'redistribution_plan': plan
        }
    
    def execute_redistribution(self, dry_run: bool = True) -> Dict:
        """执行省份重分配"""
        print("🔄 执行省份重分配...")
        
        # 获取重分配方案
        analysis_result = self.preview_redistribution()
        plan = analysis_result['redistribution_plan']
        provinces_data = analysis_result['provinces_data']
        
        if dry_run:
            print("\\n🔍 这是预览模式，未实际修改")
            return analysis_result
        
        print("\\n⚠️ 开始实际修改操作...")
        
        modifications_made = 0
        content_modified = self.content
        
        # 修改转移给中国的省份
        for transfer_info in plan['transferred_provinces']:
            province_id = transfer_info['province_id']
            
            if province_id in provinces_data:
                province_data = provinces_data[province_id]
                
                # 找到省份块并修改owner和controller
                province_start = province_data['start_pos']
                province_end = province_data['end_pos']
                province_content = content_modified[province_start:province_end]
                
                # 修改拥有者
                if re.search(r'owner="?[A-Z]{2,3}"?', province_content):
                    province_content = re.sub(
                        r'owner="?[A-Z]{2,3}"?',
                        'owner="CHI"',
                        province_content
                    )
                else:
                    # 如果没有owner字段，添加一个
                    province_content = re.sub(
                        r'(name="[^"]*")',
                        r'\\1\\n\\towner="CHI"',
                        province_content
                    )
                
                # 修改控制者
                if re.search(r'controller="?[A-Z]{2,3}"?', province_content):
                    province_content = re.sub(
                        r'controller="?[A-Z]{2,3}"?',
                        'controller="CHI"',
                        province_content
                    )
                else:
                    # 如果没有controller字段，添加一个
                    province_content = re.sub(
                        r'(owner="CHI")',
                        r'\\1\\n\\tcontroller="CHI"',
                        province_content
                    )
                
                # 添加中国核心（如果还没有）
                if 'CHI' not in transfer_info['cores']:
                    # 在适当位置添加核心
                    if re.search(r'core="[A-Z]{2,3}"', province_content):
                        # 在最后一个core后面添加
                        province_content = re.sub(
                            r'(core="[A-Z]{2,3}"[\\s\\n]*)',
                            r'\\1\\tcore="CHI"\\n',
                            province_content,
                            count=1
                        )
                    else:
                        # 在controller后面添加
                        province_content = re.sub(
                            r'(controller="CHI")',
                            r'\\1\\n\\tcore="CHI"',
                            province_content
                        )
                
                # 更新内容
                content_modified = content_modified[:province_start] + province_content + content_modified[province_end:]
                modifications_made += 1
                
                print(f"✅ 转移省份 {province_data['name']} ({province_id}) -> CHI")
        
        # 更新修改器内容
        self.modifier.content = content_modified
        
        print(f"\\n✅ 重分配完成:")
        print(f"   修改省份: {modifications_made} 个")
        print(f"   中国新增省份: {plan['china_gains']} 个")
        
        return {
            'modifications_made': modifications_made,
            'redistribution_plan': plan,
            'success': True
        }
    
    def redistribute_with_backup(self, backup_suffix: str = None) -> Dict:
        """安全执行重分配（自动备份）"""
        if backup_suffix is None:
            from datetime import datetime
            backup_suffix = f"before_redistribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print("🛡️ 安全执行省份重分配")
        print("=" * 40)
        
        # 创建备份
        backup_name = self.modifier.create_backup(self.modifier.file_path, backup_suffix)
        if not backup_name:
            print("❌ 备份失败，取消重分配操作")
            return None
        
        # 先进行预览
        print("\\n1️⃣ 执行预览分析...")
        preview_result = self.execute_redistribution(dry_run=True)
        
        # 询问确认
        plan = preview_result['redistribution_plan']
        print(f"\\n⚠️ 将要重分配 {plan['china_gains']} 个省份给中国")
        print(f"   受影响国家: {plan['affected_countries']} 个")
        print(f"   备份文件: {backup_name}")
        
        confirm = input("\\n确认执行重分配? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print("❌ 用户取消操作")
            return None
        
        # 执行实际重分配
        print("\\n2️⃣ 执行实际重分配...")
        result = self.execute_redistribution(dry_run=False)
        
        # 检查花括号平衡
        print("\\n3️⃣ 检查文件完整性...")
        if self.modifier.check_bracket_balance():
            # 保存修改后的文件
            try:
                with open(self.modifier.file_path, 'w', encoding='utf-8-sig') as f:
                    f.write(self.modifier.content)
                
                print(f"✅ 重分配完成并保存到原文件")
                
                # 保存重分配报告
                from datetime import datetime
                report_filename = f"province_redistribution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                try:
                    import json
                    with open(report_filename, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print(f"📋 重分配报告已保存: {report_filename}")
                except:
                    pass
                
                return result
                
            except Exception as e:
                print(f"❌ 保存文件失败: {e}")
                return None
        else:
            print("❌ 花括号平衡检查失败，未保存修改")
            return None

def preview_redistribution(filename='autosave.v2'):
    """预览省份重分配"""
    print("🔍 省份重分配预览模式")
    print("=" * 30)
    
    if not os.path.exists(filename):
        print(f"❌ 未找到文件: {filename}")
        return False
    
    try:
        redistributor = ProvinceRedistributor(filename)
        result = redistributor.preview_redistribution()
        
        if result:
            plan = result['redistribution_plan']
            print(f"\\n📊 预览结果:")
            print(f"   受影响国家: {plan['affected_countries']} 个")
            print(f"   中国将获得: {plan['china_gains']} 个省份")
            print(f"\\n💡 这将创造一个中国统治世界的局面！")
            return True
        else:
            print("❌ 预览失败")
            return False
            
    except Exception as e:
        print(f"❌ 预览出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def execute_redistribution(filename='autosave.v2'):
    """实际执行省份重分配"""
    print("🔄 省份重分配执行模式")
    print("=" * 30)
    
    if not os.path.exists(filename):
        print(f"❌ 未找到文件: {filename}")
        return False
    
    try:
        redistributor = ProvinceRedistributor(filename)
        result = redistributor.redistribute_with_backup()
        
        if result:
            print(f"\\n🎉 重分配成功完成!")
            print(f"   修改省份: {result['modifications_made']} 个")
            return True
        else:
            print("❌ 重分配失败或被取消")
            return False
            
    except Exception as e:
        print(f"❌ 重分配出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def interactive_mode():
    """交互式模式"""
    print("🌍 Victoria II 省份重分配工具")
    print("=" * 40)
    print("🇨🇳 中国世界统一计划！保护各国首都，其余省份归中国")
    print("🏛️ 策略：每个国家保留首都，非首都省份转移给中国")
    
    # 检查存档文件
    available_files = [f for f in os.listdir('.') if f.endswith('.v2')]
    
    if not available_files:
        print("❌ 未找到.v2存档文件")
        return
    
    print(f"\\n📁 找到 {len(available_files)} 个存档文件:")
    for i, file in enumerate(available_files, 1):
        size_mb = os.path.getsize(file) / (1024 * 1024)
        print(f"   {i}. {file} ({size_mb:.1f} MB)")
    
    # 选择文件
    if len(available_files) == 1:
        selected_file = available_files[0]
        print(f"\\n📂 自动选择: {selected_file}")
    else:
        try:
            choice = input(f"\\n请选择文件 (1-{len(available_files)}): ").strip()
            if not choice:
                selected_file = available_files[0]
            else:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(available_files):
                    selected_file = available_files[choice_idx]
                else:
                    selected_file = available_files[0]
        except ValueError:
            selected_file = available_files[0]
    
    # 选择操作模式
    print(f"\\n选择操作模式:")
    print(f"1. 预览模式 - 仅查看重分配方案 (推荐)")
    print(f"2. 执行模式 - 实际执行省份重分配")
    
    mode_choice = input("\\n请选择模式 (1/2): ").strip()
    
    if mode_choice == "2":
        print(f"\\n⚠️ 注意: 执行模式将永久修改省份归属")
        print(f"   各国将保留首都，其余省份转移给中国")
        print(f"   程序会自动创建备份，但请确保重要数据已保存")
        confirm = input("\\n确认执行重分配? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes', '是']:
            execute_redistribution(selected_file)
        else:
            print("❌ 用户取消重分配操作")
    else:
        preview_redistribution(selected_file)

def main():
    """主函数"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "preview":
            preview_redistribution()
        elif mode == "execute":
            execute_redistribution()
        else:
            print(f"❌ 未知模式: {mode}")
            print(f"支持的模式: preview, execute")
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
