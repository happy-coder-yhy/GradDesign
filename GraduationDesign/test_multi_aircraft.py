"""
测试多航班调度系统
"""

import requests
import json

API_BASE = "http://localhost:5001"

def test_multi_aircraft_scheduling():
    """测试多航班调度功能"""
    print("=" * 70)
    print("测试多航班调度系统")
    print("=" * 70)

    # 1. 生成模拟航班数据
    print("\n1. 生成模拟航班数据...")
    response = requests.post(f"{API_BASE}/api/multi-aircraft/generate-simulation", json={
        "num_flights": 6,
        "base_time": "2024-01-20 14:00:00"
    })

    if response.status_code == 200:
        data = response.json()
        print(f"✓ 成功生成 {data['num_flights']} 个航班")
        flights = data['flights']

        for flight in flights:
            print(f"  - {flight['flight_id']}: {flight['operation']} "
                  f"{flight['start_node_id']} -> {flight['end_node_id']}, "
                  f"时间: {flight['scheduled_time']}")
    else:
        print(f"✗ 生成失败: {response.status_code}")
        print(response.text)
        return

    # 2. 测试FCFS调度
    print("\n2. 测试FCFS调度...")
    response = requests.post(f"{API_BASE}/api/multi-aircraft/schedule", json={
        "strategy": "fcfs",
        "flights": flights
    })

    if response.status_code == 200:
        data = response.json()
        print(f"✓ FCFS调度成功")
        print(f"  - 航班数: {data['flight_count']}")
        print(f"  - 总距离: {data['total_distance']:.2f} 米")
        print(f"  - 总时间: {data['total_time']:.2f} 秒")
        print(f"  - 总延误: {data['total_delay']:.2f} 秒")
        print(f"  - 冲突数: {data['total_conflicts']}")

        # 显示每个航班的详细信息
        print("\n  航班详情:")
        for schedule in data['schedules']:
            print(f"    {schedule['flight_id']}: "
                  f"路径长度 {schedule['total_distance']:.2f}m, "
                  f"时间 {schedule['total_time']:.2f}s, "
                  f"延误 {schedule['delay']:.1f}s, "
                  f"冲突 {schedule['conflict_count']}个")
    else:
        print(f"✗ 调度失败: {response.status_code}")
        print(response.text)

    # 3. 测试优先级调度
    print("\n3. 测试优先级调度...")
    response = requests.post(f"{API_BASE}/api/multi-aircraft/schedule", json={
        "strategy": "priority",
        "flights": flights
    })

    if response.status_code == 200:
        data = response.json()
        print(f"✓ 优先级调度成功")
        print(f"  - 航班数: {data['flight_count']}")
        print(f"  - 总距离: {data['total_distance']:.2f} 米")
        print(f"  - 总时间: {data['total_time']:.2f} 秒")
        print(f"  - 总延误: {data['total_delay']:.2f} 秒")
        print(f"  - 冲突数: {data['total_conflicts']}")
    else:
        print(f"✗ 调度失败: {response.status_code}")
        print(response.text)

    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    test_multi_aircraft_scheduling()
