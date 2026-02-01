"""
K-Shortest Paths 算法实现示例
================================

实现Yen's算法来查找K条最短路径，用于冲突避免
"""

import heapq
from typing import List, Dict, Tuple, Set
from collections import deque


def yen_ksp(graph, start, goal, k=3):
    """
    Yen's算法查找K条最短无环路径

    参数:
        graph: 图结构 {node_id: {neighbor: distance}}
        start: 起始节点ID
        goal: 目标节点ID
        k: 需要的路径数量

    返回:
        List[List[int]]: K条路径，每条路径是节点ID列表
    """

    # 第一次运行A*算法，找到最短路径
    first_path = a_star_search(graph, start, goal)

    if not first_path:
        return []

    # 初始化最短路径列表（A_k）
    a_k_paths = [first_path]

    # 初始化候选路径列表（B_k）
    b_k_candidates = []

    for k_index in range(1, k):
        # 对前k-1条最短路径中的每条路径
        for i, previous_path in enumerate(a_k_paths[:k_index]):
            # 找到偏差节点（ spur node）
            # 路径的前i个节点与之前路径相同，从第i+1个节点开始分支
            spur_node = previous_path[i]
            root_path = previous_path[:i+1]

            # 计算从根路径到所有后续节点的距离
            root_path_cost = sum_path_distance(graph, root_path)

            # 临时移除根路径中的节点（除了spur_node）来避免环
            removed_edges = []
            for path in a_k_paths[:k_index]:
                if len(path) > i and path[:i+1] == root_path:
                    # 移除从spur_node出发的下一条边
                    if i+1 < len(path):
                        edge_to_remove = (path[i], path[i+1])
                        removed_edges.append(edge_to_remove)
                        if edge_to_remove[0] in graph:
                            if edge_to_remove[1] in graph[edge_to_remove[0]]:
                                del graph[edge_to_remove[0]][edge_to_remove[1]]

            # 从spur node运行A*算法到goal
            spur_path = a_star_search(graph, spur_node, goal)

            if spur_path:
                # 合并根路径和支线路径
                total_path = root_path[:-1] + spur_path

                # 如果这条路径不在候选列表中，添加它
                if total_path not in b_k_candidates and total_path not in a_k_paths:
                    heapq.heappush(b_k_candidates, (
                        sum_path_distance(graph, total_path),
                        total_path
                    ))

            # 恢复被移除的边
            for edge in removed_edges:
                if edge[0] not in graph:
                    graph[edge[0]] = {}
                graph[edge[0]][edge[1]] = edge_distance(graph, edge)

        # 如果没有候选路径，结束
        if not b_k_candidates:
            break

        # 从候选列表中选择成本最低的路径
        cost, best_candidate = heapq.heappop(b_k_candidates)
        a_k_paths.append(best_candidate)

    return a_k_paths


def a_star_search(graph, start, goal):
    """
    A*算法搜索最短路径

    返回:
        List[int]: 节点ID列表，如果找不到返回None
    """
    if start not in graph or goal not in graph:
        return None

    # 优先队列：(f_score, node, path)
    open_set = [(0, start, [start])]
    visited = set()

    while open_set:
        current_cost, current_node, path = heapq.heappop(open_set)

        if current_node == goal:
            return path

        if current_node in visited:
            continue

        visited.add(current_node)

        # 检查邻居节点
        if current_node in graph:
            for neighbor, distance in graph[current_node].items():
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    new_cost = current_cost + distance
                    # 使用曼哈顿距离作为启发式
                    h_score = heuristic(neighbor, goal)
                    f_score = new_cost + h_score
                    heapq.heappush(open_set, (f_score, neighbor, new_path))

    return None


def sum_path_distance(graph, path):
    """计算路径的总距离"""
    total = 0
    for i in range(len(path) - 1):
        if path[i] in graph and path[i+1] in graph[path[i]]:
            total += graph[path[i]][path[i+1]]
    return total


def edge_distance(graph, edge):
    """获取边的距离"""
    if edge[0] in graph and edge[1] in graph[edge[0]]:
        return graph[edge[0]][edge[1]]
    return 1.0  # 默认距离


def heuristic(node, goal):
    """
    启发式函数（简化版）
    实际应用中应该使用节点的实际坐标计算欧几里得距离
    """
    return 1.0  # 简化实现


# ========== 使用示例 ==========

def example_usage():
    """使用示例"""

    # 构建示例图
    graph = {
        1: {15: 100, 12: 120},
        2: {25: 110, 22: 115},
        12: {25: 80, 48: 150},
        15: {28: 90, 45: 130},
        22: {48: 95, 62: 140},
        25: {48: 85},
        28: {45: 60},
        45: {100: 70},
        48: {62: 75, 100: 80},
        62: {100: 65},
        100: {}  # 目标节点
    }

    start = 1
    goal = 100
    k = 3

    print(f"查找从节点 {start} 到节点 {goal} 的{k}条最短路径:")
    print("=" * 60)

    paths = yen_ksp(graph, start, goal, k)

    for i, path in enumerate(paths, 1):
        distance = sum_path_distance(graph, path)
        print(f"\n路径 {i}: {path}")
        print(f"总距离: {distance}m")
        print(f"节点数: {len(path)}")

    return paths


# ========== 集成到现有系统的接口 ==========

class PathAlternativesFinder:
    """路径备选方案查找器"""

    def __init__(self, graph_optimizer):
        """
        参数:
            graph_optimizer: AirportGraph实例
        """
        self.optimizer = graph_optimizer
        self.cache = {}  # 缓存计算结果

    def find_alternatives(self, start_node, goal_node, k=3):
        """
        查找K条备选路径

        返回:
            List[Dict]: 备选路径列表
            [
                {
                    'path_id': 'path_1',
                    'nodes': [node_objects],
                    'node_ids': [1, 15, 28, ...],
                    'distance': 2500,
                    'time': 180,
                    'fuel': 45,
                    'rank': 1,
                    'differences_from_best': {
                        'distance': 0,
                        'time': 0,
                        'fuel': 0
                    }
                },
                ...
            ]
        """
        cache_key = (start_node.id, goal_node.id, k)

        # 检查缓存
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 构建简化的图结构（只包含节点ID和距离）
        simple_graph = self._build_simple_graph()

        # 运行KSP算法
        path_ids_list = yen_ksp(
            simple_graph,
            start_node.id,
            goal_node.id,
            k
        )

        if not path_ids_list:
            return []

        # 转换为详细信息格式
        alternatives = []
        best_stats = None

        for rank, path_ids in enumerate(path_ids_list, 1):
            # 获取节点对象
            nodes = [self.optimizer.graph.get_node(nid) for nid in path_ids]

            # 计算统计数据
            stats = self._calculate_path_stats(nodes)

            if rank == 1:
                best_stats = stats

            alternatives.append({
                'path_id': f'path_{rank}',
                'nodes': nodes,
                'node_ids': path_ids,
                'distance': stats['distance'],
                'time': stats['time'],
                'fuel': stats['fuel'],
                'rank': rank,
                'differences_from_best': {
                    'distance': stats['distance'] - best_stats['distance'],
                    'time': stats['time'] - best_stats['time'],
                    'fuel': stats['fuel'] - best_stats['fuel']
                } if rank > 1 else {'distance': 0, 'time': 0, 'fuel': 0}
            })

        # 缓存结果
        self.cache[cache_key] = alternatives

        return alternatives

    def _build_simple_graph(self):
        """构建简化的图结构用于KSP算法"""
        # 这里需要根据实际的图结构来实现
        # 返回格式: {node_id: {neighbor_id: distance}}
        pass

    def _calculate_path_stats(self, nodes):
        """计算路径统计信息"""
        # 距离、时间、燃料消耗
        # 这里需要根据实际的optimizer实现
        pass


# ========== API接口示例 ==========

@app.route('/api/path/alternatives', methods=['POST'])
def get_alternative_paths():
    """
    获取多条备选路径API接口

    请求体:
    {
        "start_node_id": 1,
        "goal_node_id": 100,
        "k": 3  # 可选，默认3
    }

    响应:
    {
        "success": true,
        "paths": [
            {
                "path_id": "path_1",
                "nodes": [...],
                "distance": 2500,
                "time": 180,
                "rank": 1,
                "differences_from_best": {...}
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        start_node_id = data.get('start_node_id')
        goal_node_id = data.get('goal_node_id')
        k = data.get('k', 3)

        if not start_node_id or not goal_node_id:
            return jsonify({
                'success': False,
                'error': '请提供start_node_id和goal_node_id'
            }), 400

        start_node = graph.get_node(start_node_id)
        goal_node = graph.get_node(goal_node_id)

        if not start_node or not goal_node:
            return jsonify({
                'success': False,
                'error': '未找到指定的节点'
            }), 404

        # 查找备选路径
        finder = PathAlternativesFinder(optimizer)
        alternatives = finder.find_alternatives(start_node, goal_node, k)

        return jsonify({
            'success': True,
            'paths': alternatives
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    example_usage()
