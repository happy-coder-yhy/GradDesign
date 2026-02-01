"""
直接测试API端点，不通过HTTP
"""
import sys
sys.path.insert(0, '/Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign')

from Algorithm.Astar import AirportGraph
from Algorithm.MultiAircraftScheduler import generate_simulation_data
import json

print("正在初始化系统...")
graph = AirportGraph('/Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign/西安机场')
graph.load_data()

print("\n测试生成航班数据...")
try:
    flights = generate_simulation_data(graph, 6)
    print(f"✓ 生成了 {len(flights)} 个航班")

    # 转换为JSON格式（模拟API响应）
    flights_data = []
    for flight in flights:
        flight_data = {
            'flight_id': flight.flight_id,
            'aircraft_type': flight.aircraft_type,
            'operation': flight.operation.value,
            'start_node_id': flight.start_node.id,
            'start_node_type': flight.start_node.node_type,
            'end_node_id': flight.end_node.id,
            'end_node_type': flight.end_node.node_type,
            'scheduled_time': flight.scheduled_time.strftime('%Y-%m-%d %H:%M:%S'),
            'priority': flight.priority.name.lower(),
            'speed': flight.speed,
            'start_position': {
                'x': flight.start_node.x,
                'y': flight.start_node.y
            },
            'end_position': {
                'x': flight.end_node.x,
                'y': flight.end_node.y
            }
        }
        flights_data.append(flight_data)

    # 尝试JSON序列化
    json_str = json.dumps({
        'success': True,
        'num_flights': len(flights_data),
        'flights': flights_data
    }, indent=2)

    print("\n✓ JSON序列化成功")
    print(f"响应数据长度: {len(json_str)} 字符")

except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
