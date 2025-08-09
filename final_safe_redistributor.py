#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版省份重分配工具 - 安全首都保护版
保留各国首都，其余省份分配给中国
"""

import os
import re
import json
from datetime import datetime

def load_file_simple(filename):
    """简单文件加载"""
    encodings = ['latin1', 'utf-8', 'utf-8-sig']
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"文件加载成功 (编码: {encoding}), 大小: {len(content):,} 字符")
            return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"加载失败: {e}")
            return None
    return None

def analyze_provinces_and_capitals(content):
    """分析省份和首都信息"""
    print("开始分析省份和国家信息...")
    
    # 分析省份
    province_pattern = re.compile(r'^(\d+)=\s*{', re.MULTILINE)
    province_matches = list(province_pattern.finditer(content))
    
    provinces_data = {}
    countries_data = {}
    
    print(f"找到 {len(province_matches)} 个省份")
    
    for i, match in enumerate(province_matches):
        province_id = int(match.group(1))
        start_pos = match.end()
        
        # 确定省份块结束位置
        if i + 1 < len(province_matches):
            end_pos = province_matches[i + 1].start()
        else:
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+20000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 10000
        
        province_content = content[start_pos:end_pos]
        
        # 提取省份信息
        name_match = re.search(r'name="([^"]+)"', province_content)
        owner_match = re.search(r'owner="?([A-Z]{2,3})"?', province_content)
        
        province_name = name_match.group(1) if name_match else f"Province_{province_id}"
        owner = owner_match.group(1) if owner_match else None
        
        provinces_data[province_id] = {
            'name': province_name,
            'owner': owner
        }
        
        # 按国家分组
        if owner:
            if owner not in countries_data:
                countries_data[owner] = {'provinces': [], 'capital': None}
            countries_data[owner]['provinces'].append(province_id)
        
        if (i + 1) % 500 == 0:
            print(f"  进度: {i + 1}/{len(province_matches)}")
    
    # 分析各国首都
    print("分析各国首都...")
    country_pattern = re.compile(r'^([A-Z]{2,3})=\s*{', re.MULTILINE)
    country_matches = list(country_pattern.finditer(content))
    
    for i, match in enumerate(country_matches):
        country_tag = match.group(1)
        start_pos = match.end()
        
        if i + 1 < len(country_matches):
            end_pos = country_matches[i + 1].start()
        else:
            next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+50000])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = start_pos + 30000
        
        country_content = content[start_pos:end_pos]
        capital_match = re.search(r'capital=(\d+)', country_content)
        
        if capital_match and country_tag in countries_data:
            capital_id = int(capital_match.group(1))
            countries_data[country_tag]['capital'] = capital_id
    
    print(f"分析完成: {len(countries_data)} 个国家, {len(provinces_data)} 个省份")
    return countries_data, provinces_data

def plan_capital_protected_redistribution(countries_data, provinces_data):
    """规划首都保护的重分配方案"""
    print("规划首都保护重分配方案...")
    
    plan = {
        'kept_provinces': {},
        'transferred_provinces': [],
        'china_gains': 0,
        'capital_protected': 0,
        'fallback_used': 0,
        'affected_countries': 0
    }
    
    for country_tag, country_info in countries_data.items():
        if country_tag == 'CHI':  # 跳过中国
            continue
        
        provinces = country_info['provinces']
        capital = country_info['capital']
        
        if not provinces:
            continue
        
        # 首都保护逻辑
        if capital and capital in provinces:
            # 保护首都
            kept_province = capital
            plan['capital_protected'] += 1
            reason = "首都保护"
        else:
            # 使用替代省份
            kept_province = provinces[0]
            plan['fallback_used'] += 1
            reason = "替代省份"
        
        province_name = provinces_data[kept_province]['name']
        
        plan['kept_provinces'][country_tag] = {
            'province_id': kept_province,
            'province_name': province_name,
            'reason': reason
        }
        
        # 转移其余省份给中国
        if len(provinces) > 1:
            plan['affected_countries'] += 1
            for province_id in provinces:
                if province_id != kept_province:
                    plan['transferred_provinces'].append({
                        'province_id': province_id,
                        'province_name': provinces_data[province_id]['name'],
                        'original_owner': country_tag
                    })
                    plan['china_gains'] += 1
    
    return plan

def display_redistribution_plan(plan, countries_data):
    """显示重分配计划"""
    print("\n" + "=" * 50)
    print("首都保护重分配方案")
    print("=" * 50)
    
    # 统计信息
    china_current = len(countries_data.get('CHI', {}).get('provinces', []))
    
    print(f"\n统计信息:")
    print(f"  总国家数: {len(countries_data)} 个")
    print(f"  首都保护成功: {plan['capital_protected']} 个国家")
    print(f"  使用替代省份: {plan['fallback_used']} 个国家")
    print(f"  受影响国家: {plan['affected_countries']} 个")
    print(f"  中国当前省份: {china_current} 个")
    print(f"  中国将获得: {plan['china_gains']} 个省份")
    print(f"  中国重分配后: {china_current + plan['china_gains']} 个省份")
    
    # 显示保留的省份
    print(f"\n各国保留的省份 (前25个):")
    kept_items = list(plan['kept_provinces'].items())[:25]
    for i, (country_tag, info) in enumerate(kept_items, 1):
        status = "首都" if info['reason'] == "首都保护" else "替代"
        print(f"  {i:2d}. {country_tag}: {info['province_name']} ({status})")
    
    if len(plan['kept_provinces']) > 25:
        print(f"  ... 还有 {len(plan['kept_provinces']) - 25} 个国家")
    
    # 显示转移的省份示例
    print(f"\n转移给中国的省份 (前20个):")
    for i, info in enumerate(plan['transferred_provinces'][:20], 1):
        print(f"  {i:2d}. {info['province_name']} <- {info['original_owner']}")
    
    if len(plan['transferred_provinces']) > 20:
        print(f"  ... 还有 {len(plan['transferred_provinces']) - 20} 个省份")
    
    print(f"\n预览完成! 这将创建一个中国统一世界的格局。")

def execute_redistribution(content, plan, provinces_data):
    """执行实际的省份重分配"""
    print("\n开始执行省份重分配...")
    
    modified_content = content
    modifications_made = 0
    
    # 按照从后往前的顺序处理，避免位置偏移
    transfers_by_position = []
    
    for transfer_info in plan['transferred_provinces']:
        province_id = transfer_info['province_id']
        
        # 查找省份在文件中的位置
        province_pattern = re.compile(rf'^{province_id}=\s*{{', re.MULTILINE)
        match = province_pattern.search(content)
        
        if match:
            start_pos = match.end()
            
            # 找到省份块的结束位置
            next_province = re.search(r'\n\d+=\s*{', content[start_pos:start_pos+20000])
            if next_province:
                end_pos = start_pos + next_province.start()
            else:
                next_section = re.search(r'\n[a-z_]+=\s*{', content[start_pos:start_pos+20000])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = start_pos + 10000
            
            transfers_by_position.append({
                'start': match.start(),
                'end': end_pos,
                'province_id': province_id,
                'original_owner': transfer_info['original_owner']
            })
    
    # 按位置从后往前排序
    transfers_by_position.sort(key=lambda x: x['start'], reverse=True)
    
    print(f"找到 {len(transfers_by_position)} 个需要修改的省份")
    
    for i, transfer in enumerate(transfers_by_position):
        province_id = transfer['province_id']
        start_pos = transfer['start']
        end_pos = transfer['end']
        
        province_content = modified_content[start_pos:end_pos]
        original_owner = transfer['original_owner']
        
        # 修改拥有者
        if re.search(r'owner="?[A-Z]{2,3}"?', province_content):
            province_content = re.sub(
                r'owner="?[A-Z]{2,3}"?',
                'owner="CHI"',
                province_content
            )
        else:
            # 如果没有owner字段，在name后添加
            province_content = re.sub(
                r'(name="[^"]*")',
                r'\1\n\towner="CHI"',
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
            # 如果没有controller字段，在owner后添加
            province_content = re.sub(
                r'(owner="CHI")',
                r'\1\n\tcontroller="CHI"',
                province_content
            )
        
        # 添加中国核心（如果还没有）
        if 'core="CHI"' not in province_content:
            if re.search(r'core="[A-Z]{2,3}"', province_content):
                # 在最后一个core后面添加
                province_content = re.sub(
                    r'(core="[A-Z]{2,3}"[^\n]*)',
                    r'\1\n\tcore="CHI"',
                    province_content,
                    count=1
                )
            else:
                # 在controller后面添加
                province_content = re.sub(
                    r'(controller="CHI")',
                    r'\1\n\tcore="CHI"',
                    province_content
                )
        
        # 更新内容
        modified_content = modified_content[:start_pos] + province_content + modified_content[end_pos:]
        modifications_made += 1
        
        if (i + 1) % 100 == 0:
            print(f"  进度: {i + 1}/{len(transfers_by_position)}")
    
    print(f"完成! 修改了 {modifications_made} 个省份")
    return modified_content

def check_bracket_balance(content):
    """检查花括号平衡"""
    open_count = content.count('{')
    close_count = content.count('}')
    difference = open_count - close_count
    
    print(f"花括号检查: 开={open_count}, 闭={close_count}, 差异={difference}")
    return difference == -1  # Victoria II 通常期望 -1

def create_backup(filename):
    """创建备份文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"{filename}.backup_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(filename, backup_filename)
        print(f"备份创建成功: {backup_filename}")
        return backup_filename
    except Exception as e:
        print(f"备份创建失败: {e}")
        return None

def save_modified_file(filename, content, plan):
    """保存修改后的文件"""
    # 检查花括号平衡
    if not check_bracket_balance(content):
        print("错误: 花括号不平衡，拒绝保存!")
        return False
    
    # 创建备份
    backup_file = create_backup(filename)
    if not backup_file:
        print("警告: 备份失败，但继续保存...")
    
    try:
        # 保存修改后的文件
        with open(filename, 'w', encoding='latin1') as f:
            f.write(content)
        
        print(f"文件保存成功: {filename}")
        
        # 保存执行报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"redistribution_execution_report_{timestamp}.json"
        
        execution_report = {
            'timestamp': timestamp,
            'original_file': filename,
            'backup_file': backup_file,
            'modifications_made': len(plan['transferred_provinces']),
            'china_gains': plan['china_gains'],
            'affected_countries': plan['affected_countries'],
            'plan': plan
        }
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(execution_report, f, ensure_ascii=False, indent=2)
        
        print(f"执行报告已保存: {report_filename}")
        return True
        
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def get_available_save_files():
    """获取可用的存档文件列表"""
    save_files = []
    try:
        for file in os.listdir('.'):
            if file.endswith('.v2'):
                file_size = os.path.getsize(file)
                file_size_mb = file_size / (1024 * 1024)
                save_files.append({
                    'filename': file,
                    'size_mb': file_size_mb,
                    'size_bytes': file_size
                })
        
        # 按文件大小排序（大文件通常是存档）
        save_files.sort(key=lambda x: x['size_bytes'], reverse=True)
        return save_files
    except Exception as e:
        print(f"扫描存档文件失败: {e}")
        return []

def select_save_file():
    """选择存档文件"""
    save_files = get_available_save_files()
    
    if not save_files:
        print("未找到任何 .v2 存档文件")
        return None
    
    print("\n" + "=" * 60)
    print("选择要处理的存档文件")
    print("=" * 60)
    
    for i, file_info in enumerate(save_files, 1):
        filename = file_info['filename']
        size_mb = file_info['size_mb']
        print(f"{i:2d}. {filename} ({size_mb:.1f} MB)")
    
    print(f"{len(save_files) + 1:2d}. 取消")
    
    while True:
        try:
            choice = input(f"\n请选择文件 (1-{len(save_files) + 1}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(save_files):
                selected_file = save_files[choice_num - 1]['filename']
                print(f"已选择: {selected_file}")
                return selected_file
            elif choice_num == len(save_files) + 1:
                print("用户取消选择")
                return None
            else:
                print(f"无效选择，请输入 1-{len(save_files) + 1}")
        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n用户取消操作")
            return None
        except EOFError:
            # 处理管道输入的情况
            if save_files:
                return save_files[0]['filename']  # 默认选择第一个文件
            return None
        except Exception:
            print("输入错误，请重试")

def interactive_menu():
    """交互式菜单"""
    print("\n" + "=" * 60)
    print("Victoria II 首都保护省份重分配工具")
    print("=" * 60)
    print("策略: 保留各国首都，其余省份转移给中国")
    print("\n选择操作:")
    print("1. 预览重分配方案 (安全)")
    print("2. 执行重分配 (修改存档文件)")
    print("3. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (1-3): ").strip()
            if choice == '1':
                return 1
            elif choice == '2':
                return 2
            elif choice == '3':
                return 3
            else:
                print("无效选择，请输入 1、2 或 3")
        except KeyboardInterrupt:
            print("\n\n用户取消操作")
            return 3
        except EOFError:
            # 处理管道输入的情况
            return 1  # 默认返回预览模式
        except Exception:
            print("输入错误，请重试")

def execute_with_confirmation(filename, content, countries_data, provinces_data, plan):
    """确认后执行重分配"""
    print("\n" + "=" * 50)
    print("重分配执行确认")
    print("=" * 50)
    
    print(f"文件: {filename}")
    print(f"将要修改: {plan['china_gains']} 个省份")
    print(f"受影响国家: {plan['affected_countries']} 个")
    print(f"中国省份将从 {len(countries_data.get('CHI', {}).get('provinces', []))} 增加到 {len(countries_data.get('CHI', {}).get('provinces', [])) + plan['china_gains']}")
    
    print("\n警告:")
    print("- 这将永久修改您的存档文件")
    print("- 程序会自动创建备份")
    print("- 建议在执行前手动备份重要存档")
    
    while True:
        confirm = input("\n确认执行重分配? (直接回车确认，输入 no 取消): ").strip().lower()
        if confirm in ['', 'yes', 'y', '是']:  # 空字符串（回车）也视为确认
            break
        elif confirm in ['no', 'n', '否']:
            print("用户取消操作")
            return False
        else:
            print("请直接回车确认，或输入 no 取消")
    
    # 执行重分配
    print("\n开始执行重分配...")
    modified_content = execute_redistribution(content, plan, provinces_data)
    
    # 保存文件
    if save_modified_file(filename, modified_content, plan):
        print("\n" + "=" * 50)
        print("重分配执行成功!")
        print("=" * 50)
        print(f"修改省份: {plan['china_gains']} 个")
        print(f"受影响国家: {plan['affected_countries']} 个")
        print("现在可以在游戏中加载修改后的存档文件。")
        return True
    else:
        print("重分配执行失败!")
        return False

def save_redistribution_report(plan, filename_suffix=""):
    """保存重分配报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"capital_protected_redistribution_plan_{timestamp}{filename_suffix}.json"
    
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存: {report_filename}")
        return report_filename
    except Exception as e:
        print(f"保存报告失败: {e}")
        return None

def main():
    """主函数"""
    import sys
    
    filename = None
    choice = None  # 初始化choice变量
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ['preview', 'execute']:
            mode = sys.argv[1].lower()
            # 如果有第二个参数作为文件名
            if len(sys.argv) > 2:
                filename = sys.argv[2]
            else:
                # 如果没有指定文件，使用默认文件
                filename = 'autosave.v2'
            
            choice = 1 if mode == 'preview' else 2
        else:
            # 第一个参数作为文件名，交互模式
            filename = sys.argv[1]
    
    # 如果没有指定文件，让用户选择
    if not filename:
        filename = select_save_file()
        if not filename:
            print("未选择文件，退出程序")
            return
    
    # 检查文件是否存在
    if not os.path.exists(filename):
        print(f"错误: 未找到文件 {filename}")
        print("可用的存档文件:")
        save_files = get_available_save_files()
        for file_info in save_files[:5]:  # 显示前5个文件
            print(f"  - {file_info['filename']} ({file_info['size_mb']:.1f} MB)")
        return
    
    # 如果还没有选择操作模式，显示菜单
    if choice is None:
        choice = interactive_menu()
    
    if choice == 3:
        print("退出程序")
        return
    
    # 加载文件
    print(f"\n加载文件: {filename}")
    content = load_file_simple(filename)
    if not content:
        print("文件加载失败")
        return
    
    # 分析数据
    countries_data, provinces_data = analyze_provinces_and_capitals(content)
    
    # 规划重分配
    plan = plan_capital_protected_redistribution(countries_data, provinces_data)
    
    if choice == 1:
        # 预览模式
        print("\n[预览模式]")
        display_redistribution_plan(plan, countries_data)
        save_redistribution_report(plan, "_preview")
        print(f"\n注意: 这只是预览! 要实际执行重分配，请使用 'python final_safe_redistributor.py execute {filename}'")
        
    elif choice == 2:
        # 执行模式
        print("\n[执行模式]")
        display_redistribution_plan(plan, countries_data)
        
        # 确认并执行
        success = execute_with_confirmation(filename, content, countries_data, provinces_data, plan)
        if not success:
            print("重分配未执行")

if __name__ == "__main__":
    main()
