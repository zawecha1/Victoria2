"""
测试选择性日期修改功能的性能
验证优化后的函数是否正常工作且性能良好
"""

import time
from victoria2_main_modifier import Victoria2Modifier

def test_selective_date_performance():
    print("🧪 测试选择性日期修改功能性能...")
    
    # 使用实际的存档文件进行测试
    save_file = "ChinaUseIt.v2"
    
    try:
        # 创建修改器实例
        modifier = Victoria2Modifier(save_file)
        
        # 记录开始时间
        start_time = time.time()
        
        # 测试只修改游戏开始日期
        result = modifier.modify_game_date_selective("2399.12.31", ["游戏开始日期"])
        
        # 记录结束时间
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 性能测试结果:")
        print(f"  ⏱️  执行时间: {duration:.2f} 秒")
        print(f"  📈 修改次数: {modifier.date_changes}")
        if duration > 0:
            print(f"  🚀 处理速度: {modifier.date_changes/duration:.0f} 次修改/秒")
        print(f"  ✅ 功能状态: {'成功' if result else '失败'}")
        
        # 再次测试修改所有类型的日期
        modifier2 = Victoria2Modifier(save_file)
        
        start_time2 = time.time()
        result2 = modifier2.modify_game_date_selective("2299.1.1", ["游戏开始日期", "选举日期", "结束日期", "出生日期"])
        end_time2 = time.time()
        duration2 = end_time2 - start_time2
        
        print(f"\n📊 全类型修改测试结果:")
        print(f"  ⏱️  执行时间: {duration2:.2f} 秒")
        print(f"  📈 修改次数: {modifier2.date_changes}")
        if duration2 > 0:
            print(f"  🚀 处理速度: {modifier2.date_changes/duration2:.0f} 次修改/秒")
        print(f"  ✅ 功能状态: {'成功' if result2 else '失败'}")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_selective_date_performance()
