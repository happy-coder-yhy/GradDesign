"""
机场场面滑行轨迹优化 - Flask API服务
提供A*算法的HTTP接口
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path

# 添加项目路径到sys.path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

from Algorithm.Astar import AirportGraph, AStarOptimizer
from Algorithm.MultiAircraftScheduler import (
    MultiAircraftScheduler,
    Flight,
    OperationType,
    PriorityLevel,
    generate_simulation_data
)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量存储图和优化器
graph = None
optimizer = None

# 数据路径
BASE_PATH = "/Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign/西安机场"


def initialize_system():
    """初始化路网图和优化器"""
    global graph, optimizer

    if graph is None:
        print("正在加载路网数据...")
        graph = AirportGraph(BASE_PATH)
        graph.load_data()

        print("正在初始化A*优化器...")
        optimizer = AStarOptimizer(
            graph=graph,
            weight_distance=1.0,
            weight_time=1.0,
            weight_fuel=0.5,
            aircraft_speed=15.0
        )
        print("系统初始化完成！")


@app.route('/')
def index():
    """API首页"""
    return jsonify({
        'message': '机场场面滑行轨迹优化API',
        'version': '2.0',
        'endpoints': {
            '/api/health': '健康检查',
            '/api/nodes': '获取所有节点',
            '/api/nodes/by-type/<node_type>': '根据类型获取节点',
            '/api/path': '计算路径（POST）',
            '/api/demo/farthest-stand': '获取距离最远的机位对',
            '/api/demo/stand-to-runway': '获取机位到跑道点',
            '/api/multi-aircraft/generate-simulation': '生成模拟航班数据（POST）',
            '/api/multi-aircraft/schedule': '多航班调度（POST）'
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        if graph is None:
            initialize_system()

        return jsonify({
            'status': 'ok',
            'graph_loaded': graph is not None,
            'node_count': len(graph.nodes) if graph else 0,
            'edge_count': sum(len(edges) for edges in graph.edges.values()) if graph else 0
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    """获取所有节点"""
    try:
        if graph is None:
            initialize_system()

        nodes_data = []
        for node in graph.nodes.values():
            nodes_data.append({
                'id': node.id,
                'type': node.node_type,
                'x': node.x,
                'y': node.y,
                'properties': node.properties
            })

        # 同时返回边数据
        edges_data = []
        for from_node_id, edges in graph.edges.items():
            for edge in edges:
                edges_data.append({
                    'from_node_id': edge.from_node.id,
                    'to_node_id': edge.to_node.id,
                    'from_x': edge.from_node.x,
                    'from_y': edge.from_node.y,
                    'to_x': edge.to_node.x,
                    'to_y': edge.to_node.y,
                    'type': edge.edge_type,
                    'length': edge.length
                })

        return jsonify({
            'success': True,
            'count': len(nodes_data),
            'nodes': nodes_data,
            'edges': edges_data,
            'edge_count': len(edges_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/nodes/by-type/<node_type>', methods=['GET'])
def get_nodes_by_type(node_type):
    """根据类型获取节点"""
    try:
        if graph is None:
            initialize_system()

        nodes = graph.find_nodes_by_type(node_type)

        nodes_data = []
        for node in nodes:
            nodes_data.append({
                'id': node.id,
                'type': node.node_type,
                'x': node.x,
                'y': node.y,
                'properties': node.properties
            })

        return jsonify({
            'success': True,
            'node_type': node_type,
            'count': len(nodes_data),
            'nodes': nodes_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/path', methods=['POST'])
def find_path():
    """
    计算路径
    POST数据格式:
    {
        "start_node_id": int,
        "goal_node_id": int,
        "weights": {
            "distance": float,
            "time": float,
            "fuel": float
        },
        "speed": float
    }
    """
    try:
        if graph is None:
            initialize_system()

        data = request.get_json()

        start_node_id = data.get('start_node_id')
        goal_node_id = data.get('goal_node_id')

        if not start_node_id or not goal_node_id:
            return jsonify({
                'success': False,
                'error': '请提供start_node_id和goal_node_id'
            }), 400

        # 获取节点
        start_node = graph.get_node(start_node_id)
        goal_node = graph.get_node(goal_node_id)

        if not start_node or not goal_node:
            return jsonify({
                'success': False,
                'error': '未找到指定的节点'
            }), 404

        # 更新权重（如果提供）
        weights = data.get('weights', {})
        if weights:
            optimizer.weight_distance = weights.get('distance', 1.0)
            optimizer.weight_time = weights.get('time', 1.0)
            optimizer.weight_fuel = weights.get('fuel', 0.5)

        # 更新速度（如果提供）
        speed = data.get('speed')
        if speed:
            optimizer.aircraft_speed = speed

        # 执行A*算法
        path, stats = optimizer.find_path(start_node, goal_node)

        if path:
            # 构建路径数据
            path_data = []
            for node in path:
                path_data.append({
                    'id': node.id,
                    'type': node.node_type,
                    'x': node.x,
                    'y': node.y,
                    'lon': node.properties.get('lon'),
                    'lat': node.properties.get('lat')
                })

            return jsonify({
                'success': True,
                'path': path_data,
                'stats': stats,
                'start_node': {
                    'id': start_node.id,
                    'type': start_node.node_type,
                    'x': start_node.x,
                    'y': start_node.y
                },
                'goal_node': {
                    'id': goal_node.id,
                    'type': goal_node.node_type,
                    'x': goal_node.x,
                    'y': goal_node.y
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': stats.get('error', '未找到路径'),
                'stats': stats
            }), 404

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/path/alternatives', methods=['POST'])
def get_alternative_paths():
    """
    获取多条备选路径（K-Shortest Paths）
    
    POST数据格式:
    {
        "start_node_id": int,
        "goal_node_id": int,
        "k": int  # 可选，默认3条路径
    }
    
    返回格式:
    {
        "success": true,
        "paths": [
            {
                "path_id": "path_1",
                "nodes": [
                    {"id": 1, "x": 100, "y": 200, "type": "StandPoint"},
                    ...
                ],
                "distance": 2500.5,
                "time": 180.2,
                "fuel": 45.1,
                "num_nodes": 5,
                "rank": 1,
                "differences_from_best": {
                    "distance": 0,
                    "time": 0,
                    "fuel": 0
                }
            },
            ...
        ]
    }
    """
    try:
        if graph is None:
            initialize_system()
        
        data = request.get_json()
        
        start_node_id = data.get('start_node_id')
        goal_node_id = data.get('goal_node_id')
        k = data.get('k', 3)  # 默认返回3条路径
        
        if not start_node_id or not goal_node_id:
            return jsonify({
                'success': False,
                'error': '请提供start_node_id和goal_node_id'
            }), 400
        
        # 获取节点
        start_node = graph.get_node(start_node_id)
        goal_node = graph.get_node(goal_node_id)
        
        if not start_node or not goal_node:
            return jsonify({
                'success': False,
                'error': '未找到指定的节点'
            }), 404
        
        # 使用KSP算法查找多条路径
        paths_with_stats = optimizer.find_k_shortest_paths(start_node, goal_node, k)
        
        if not paths_with_stats:
            return jsonify({
                'success': False,
                'error': '未找到路径'
            }), 404
        
        # 获取第一条路径的统计作为基准
        best_stats = paths_with_stats[0][1]
        
        # 构建响应数据
        paths_data = []
        for rank, (path, stats) in enumerate(paths_with_stats, 1):
            # 构建节点数据
            nodes_data = []
            for node in path:
                nodes_data.append({
                    'id': node.id,
                    'type': node.node_type,
                    'x': node.x,
                    'y': node.y
                })
            
            # 计算与最佳路径的差异
            if rank == 1:
                differences = {'distance': 0, 'time': 0, 'fuel': 0}
            else:
                differences = {
                    'distance': stats['total_distance'] - best_stats['total_distance'],
                    'time': stats['total_time'] - best_stats['total_time'],
                    'fuel': stats['fuel_consumption'] - best_stats['fuel_consumption']
                }
            
            paths_data.append({
                'path_id': f'path_{rank}',
                'nodes': nodes_data,
                'distance': stats['total_distance'],
                'time': stats['total_time'],
                'fuel': stats['fuel_consumption'],
                'num_nodes': stats['num_nodes'],
                'rank': rank,
                'differences_from_best': differences
            })
        
        print(f"[API] 返回 {len(paths_data)} 条备选路径: {start_node_id} -> {goal_node_id}")
        
        return jsonify({
            'success': True,
            'paths': paths_data
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/demo/farthest-stand', methods=['GET'])
def get_farthest_stand():
    """获取距离最远的机位对（用于演示）"""
    try:
        if graph is None:
            initialize_system()

        import math

        standpoints = graph.find_nodes_by_type('StandPoint')

        if len(standpoints) < 2:
            return jsonify({
                'success': False,
                'error': '机位数量不足'
            }), 400

        # 找到距离最远的两个机位
        max_distance = 0
        best_pair = (standpoints[0], standpoints[1])

        for i, node1 in enumerate(standpoints):
            for node2 in standpoints[i+1:]:
                distance = math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)
                if distance > max_distance:
                    max_distance = distance
                    best_pair = (node1, node2)

        start_node, goal_node = best_pair

        return jsonify({
            'success': True,
            'start_node': {
                'id': start_node.id,
                'type': start_node.node_type,
                'x': start_node.x,
                'y': start_node.y,
                'lon': start_node.properties.get('lon'),
                'lat': start_node.properties.get('lat')
            },
            'goal_node': {
                'id': goal_node.id,
                'type': goal_node.node_type,
                'x': goal_node.x,
                'y': goal_node.y,
                'lon': goal_node.properties.get('lon'),
                'lat': goal_node.properties.get('lat')
            },
            'distance': max_distance
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/demo/stand-to-runway', methods=['GET'])
def get_stand_to_runway():
    """获取距离最远的机位到跑道点（用于演示）"""
    try:
        if graph is None:
            initialize_system()

        import math

        standpoints = graph.find_nodes_by_type('StandPoint')
        runwaypoints = graph.find_nodes_by_type('RunwayPoint')

        if not standpoints or not runwaypoints:
            return jsonify({
                'success': False,
                'error': '节点数量不足'
            }), 400

        # 找到距离最远的机位和跑道点对
        max_distance = 0
        best_pair = (standpoints[0], runwaypoints[0])

        for stand in standpoints:
            for runway in runwaypoints:
                distance = math.sqrt((stand.x - runway.x)**2 + (stand.y - runway.y)**2)
                if distance > max_distance:
                    max_distance = distance
                    best_pair = (stand, runway)

        start_node, goal_node = best_pair

        return jsonify({
            'success': True,
            'start_node': {
                'id': start_node.id,
                'type': start_node.node_type,
                'x': start_node.x,
                'y': start_node.y,
                'lon': start_node.properties.get('lon'),
                'lat': start_node.properties.get('lat')
            },
            'goal_node': {
                'id': goal_node.id,
                'type': goal_node.node_type,
                'x': goal_node.x,
                'y': goal_node.y,
                'lon': goal_node.properties.get('lon'),
                'lat': goal_node.properties.get('lat')
            },
            'distance': max_distance
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== 多航班调度API ====================

@app.route('/api/multi-aircraft/schedule', methods=['POST', 'OPTIONS'])
def schedule_multi_aircraft():
    """
    多航班调度接口
    POST数据格式:
    {
        "strategy": "fcfs" | "priority" | "time_window",
        "flights": [...]
    }
    """
    # 处理OPTIONS请求（CORS预检）
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        if graph is None:
            initialize_system()

        data = request.get_json(force=True, silent=True)
        if data is None:
            data = {}

        strategy = data.get('strategy', 'fcfs')
        flights_data = data.get('flights', [])

        print(f"[API] 调度请求: strategy={strategy}, flights={len(flights_data)}")

        if not flights_data:
            error_response = jsonify({
                'success': False,
                'error': '请提供航班数据'
            })
            error_response.headers.add('Access-Control-Allow-Origin', '*')
            return error_response, 400

        # 构建Flight对象列表
        flights = []
        for flight_data in flights_data:
            try:
                start_node = graph.get_node(flight_data['start_node_id'])
                end_node = graph.get_node(flight_data['end_node_id'])

                if not start_node or not end_node:
                    print(f"[API] 未找到节点: {flight_data.get('start_node_id')} 或 {flight_data.get('end_node_id')}")
                    continue

                from datetime import datetime

                flight = Flight(
                    flight_id=flight_data['flight_id'],
                    aircraft_type=flight_data.get('aircraft_type', 'A320'),
                    operation=OperationType.DEPARTURE if flight_data['operation'] == 'departure' else OperationType.ARRIVAL,
                    start_node=start_node,
                    end_node=end_node,
                    scheduled_time=datetime.strptime(flight_data['scheduled_time'], '%Y-%m-%d %H:%M:%S'),
                    priority=PriorityLevel.HIGH if flight_data.get('priority') == 'high' else
                            (PriorityLevel.LOW if flight_data.get('priority') == 'low' else PriorityLevel.MEDIUM),
                    speed=flight_data.get('speed', 15.0)
                )
                flights.append(flight)
            except Exception as e:
                print(f"[API] 处理航班数据时出错: {e}")
                continue

        if not flights:
            error_response = jsonify({
                'success': False,
                'error': '没有有效的航班数据'
            })
            error_response.headers.add('Access-Control-Allow-Origin', '*')
            return error_response, 400

        print(f"[API] 开始调度 {len(flights)} 个航班...")

        # 创建调度器并执行调度
        scheduler = MultiAircraftScheduler(graph, strategy=strategy)
        schedules = scheduler.schedule_multiple_flights(flights)

        # 构建返回数据
        schedules_data = []
        for flight_id, schedule in schedules.items():
            try:
                # 构建路径数据
                path_data = []
                for node in schedule.path:
                    path_data.append({
                        'id': node.id,
                        'type': node.node_type,
                        'x': node.x,
                        'y': node.y
                    })

                # 构建时间点数据
                waypoints_data = []
                for node, time in schedule.waypoints:
                    waypoints_data.append({
                        'node_id': node.id,
                        'x': node.x,
                        'y': node.y,
                        'time': time.strftime('%Y-%m-%d %H:%M:%S')
                    })

                # 构建冲突数据
                conflicts_data = []
                for conflict in schedule.conflicts:
                    conflicts_data.append({
                        'conflict_id': conflict.conflict_id,
                        'conflict_type': conflict.conflict_type,
                        'flight_ids': conflict.flight_ids,
                        'node_id': conflict.node_id,
                        'time': conflict.time.strftime('%Y-%m-%d %H:%M:%S'),
                        'severity': conflict.severity
                    })

                schedules_data.append({
                    'flight_id': flight_id,
                    'aircraft_type': schedule.flight.aircraft_type,
                    'operation': schedule.flight.operation.value,
                    'start_node_id': schedule.flight.start_node.id,
                    'end_node_id': schedule.flight.end_node.id,
                    'scheduled_time': schedule.flight.scheduled_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'start_time': schedule.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': schedule.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'path': path_data,
                    'waypoints': waypoints_data,
                    'total_distance': schedule.total_distance,
                    'total_time': schedule.total_time,
                    'delay': schedule.delay.total_seconds(),
                    'conflicts': conflicts_data,
                    'conflict_count': len(conflicts_data)
                })
            except Exception as e:
                print(f"[API] 处理调度结果时出错: {e}")
                continue

        # 计算总体统计
        total_distance = sum(s.total_distance for s in schedules.values())
        total_time = sum(s.total_time for s in schedules.values())
        total_delay = sum(s.delay.total_seconds() for s in schedules.values())
        total_conflicts = sum(len(s.conflicts) for s in schedules.values())

        response_data = {
            'success': True,
            'strategy': strategy,
            'flight_count': len(schedules),
            'total_distance': total_distance,
            'total_time': total_time,
            'total_delay': total_delay,
            'total_conflicts': total_conflicts,
            'schedules': schedules_data
        }

        print(f"[API] 调度完成: {len(schedules)} 个航班, {total_conflicts} 个冲突")

        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        import traceback
        print(f"[API] 调度错误: {e}")
        traceback.print_exc()

        error_response = jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500


@app.route('/api/multi-aircraft/generate-simulation', methods=['POST', 'OPTIONS'])
def generate_simulation():
    """
    生成模拟航班数据
    POST数据格式:
    {
        "num_flights": 6,
        "base_time": "2024-01-20 14:00:00"
    }
    """
    # 处理OPTIONS请求（CORS预检）
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        if graph is None:
            initialize_system()

        data = request.get_json(force=True, silent=True)
        if data is None:
            data = {}

        num_flights = int(data.get('num_flights', 6))
        base_time_str = data.get('base_time', '2024-01-20 14:00:00')

        print(f"[API] 生成模拟航班: num_flights={num_flights}, base_time={base_time_str}")

        # 生成模拟数据
        flights = generate_simulation_data(graph, num_flights)

        print(f"[API] 成功生成 {len(flights)} 个航班")

        # 构建返回数据
        flights_data = []
        for flight in flights:
            try:
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
            except Exception as e:
                print(f"[API] 处理航班 {flight.flight_id} 时出错: {e}")
                continue

        response_data = {
            'success': True,
            'num_flights': len(flights_data),
            'flights': flights_data
        }

        print(f"[API] 返回数据: {len(flights_data)} 个航班")

        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        import traceback
        print(f"[API] 错误: {e}")
        traceback.print_exc()

        error_response = jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("机场场面滑行轨迹优化 - API服务")
    print("="*70)
    print("\n服务地址: http://localhost:5001")
    print("API文档: http://localhost:5001/")
    print("\n正在初始化系统...")
    initialize_system()
    print("\n" + "="*70)
    print("服务启动中...")
    print("="*70 + "\n")

    app.run(host='0.0.0.0', port=5001, debug=True)
