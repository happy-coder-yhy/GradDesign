"""
机场场面滑行轨迹优化 - A*算法实现（基于GeoPandas）
====================================================

本模块实现了基于A*算法的航空器滑行路径优化，直接使用GeoPandas读取SHP文件。

主要功能：
- 从SHP文件直接加载机场路网数据
- 构建拓扑图结构
- 实现A*算法进行路径规划
- 考虑滑行距离、时间、燃料消耗等多目标优化

参考文献：
1. 基于蚁群算法的航空器滑行路径优化研究
2. Weiszer et al. (2015) - 机场滑行路径多目标优化

未来优化方向：
1. 生成帕累托前沿：遍历不同权重组合（比如weight_time从 0.5 到 2.0，步长 0.1），得到一系列 “最优路径”；
2. 场景化选择：
    高峰时段（追求准点）：选weight_time最大的路径；
    低峰时段（追求降成本）：选weight_fuel最大的路径；
    正常时段：选平衡型权重（比如1.0,1.0,0.5）。
✅ 优点：灵活适配不同运营场景，兼顾多目标；
❌ 缺点：实现复杂，适合大型机场的工程化落地。

作者：毕业设计项目
日期：2026
"""

import heapq
import math
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np


@dataclass
class Node:
    """路网节点类"""
    id: int
    node_type: str  # 节点类型：StandPoint, RunwayPoint, NetworkNode等
    x: float
    y: float
    geometry: Optional[Point] = None
    properties: dict = field(default_factory=dict)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return False

    def __repr__(self):
        return f"Node(id={self.id}, type={self.node_type}, x={self.x:.2f}, y={self.y:.2f})"


@dataclass
class Edge:
    """路网边类"""
    from_node: Node
    to_node: Node
    edge_type: str
    length: float  # 边的长度（米）
    geometry: Optional[LineString] = None
    speed_limit: float = 15.0  # 速度限制（米/秒），默认约54km/h
    properties: dict = field(default_factory=dict)

    def __repr__(self):
        return f"Edge({self.from_node.id} -> {self.to_node.id}, type={self.edge_type}, length={self.length:.2f}m)"


@dataclass(order=True)
class PathNode:
    """A*算法中的路径节点，用于优先队列排序"""
    f_score: float  # f(n) = g(n) + h(n)
    g_score: float  # 从起点到当前节点的实际代价
    node: Node = field(compare=False)
    parent: Optional['PathNode'] = field(default=None, compare=False)


class AirportGraph:
    """机场路网图类，从SHP文件加载和管理路网数据"""

    def __init__(self, base_path: str):
        """
        初始化机场路网图

        参数:
            base_path: 西安机场数据文件夹路径
        """
        self.base_path = Path(base_path)
        self.nodes: Dict[int, Node] = {}
        self.edges: Dict[int, List[Edge]] = {}  # adjacency list: node_id -> list of edges
        self.node_id_counter = 0

    def load_data(self):
        """加载所有SHP文件并构建路网图"""
        print("=" * 70)
        print("开始加载机场路网数据...")
        print("=" * 70)

        # 1. 加载点数据
        self._load_points()

        # 2. 加载线路数据
        self._load_lines()

        # 3. 构建拓扑连接
        self._build_topology()

        # 4. 统计信息
        self._print_statistics()

    def _generate_node_id(self) -> int:
        """生成唯一节点ID"""
        self.node_id_counter += 1
        return self.node_id_counter

    def _load_points(self):
        """加载点状数据，并转换坐标系为投影坐标（米）"""
        print("\n1. 加载点状数据...")
        print("  - 坐标系: WGS84 (EPSG:4326) -> UTM投影 (米)")

        # 定义目标投影坐标系（UTM Zone 48N，适用于西安地区）
        target_crs = "EPSG:32648"  # UTM Zone 48N
        source_crs = "EPSG:4326"   # WGS84

        # 加载机位点
        stand_point_path = self.base_path / "西安机场机位和道路SHP" / "机位点.shp"
        if stand_point_path.exists():
            gdf = gpd.read_file(stand_point_path)
            # 如果没有CRS，设置为WGS84
            if gdf.crs is None:
                gdf.crs = source_crs
            # 投影转换
            gdf_projected = gdf.to_crs(target_crs)
            print(f"  - 读取机位点: {len(gdf)} 个")

            for idx, (row_lonlat, row_proj) in enumerate(zip(gdf.iterrows(), gdf_projected.iterrows())):
                _, row_lonlat = row_lonlat
                _, row = row_proj
                if isinstance(row.geometry, Point):
                    node_id = self._generate_node_id()
                    self.nodes[node_id] = Node(
                        id=node_id,
                        node_type='StandPoint',
                        x=row.geometry.x,  # 投影后的X坐标（米）
                        y=row.geometry.y,  # 投影后的Y坐标（米）
                        geometry=row.geometry,
                        properties={'lon': row_lonlat.geometry.x, 'lat': row_lonlat.geometry.y}
                    )

        # 加载跑道点
        runway_point_path = self.base_path / "西安机场路网数据" / "runwaypoints" / "runwaypoints.shp"
        if runway_point_path.exists():
            gdf = gpd.read_file(runway_point_path)
            if gdf.crs is None:
                gdf.crs = source_crs
            gdf_projected = gdf.to_crs(target_crs)
            print(f"  - 读取跑道点: {len(gdf)} 个")

            for idx, (row_lonlat, row_proj) in enumerate(zip(gdf.iterrows(), gdf_projected.iterrows())):
                _, row_lonlat = row_lonlat
                _, row = row_proj
                if isinstance(row.geometry, Point):
                    node_id = self._generate_node_id()
                    self.nodes[node_id] = Node(
                        id=node_id,
                        node_type='RunwayPoint',
                        x=row.geometry.x,
                        y=row.geometry.y,
                        geometry=row.geometry,
                        properties={'lon': row_lonlat.geometry.x, 'lat': row_lonlat.geometry.y}
                    )

        # 加载观察点（来自standpoints.shp，实际是观察位置，不是路网连接点）
        network_point_path = self.base_path / "西安机场路网数据" / "standpoints" / "standpoints.shp"
        if network_point_path.exists():
            gdf = gpd.read_file(network_point_path)
            if gdf.crs is None:
                gdf.crs = source_crs
            gdf_projected = gdf.to_crs(target_crs)
            print(f"  - 读取观察点(standpoints): {len(gdf)} 个")

            for idx, (row_lonlat, row_proj) in enumerate(zip(gdf.iterrows(), gdf_projected.iterrows())):
                _, row_lonlat = row_lonlat
                _, row = row_proj
                if isinstance(row.geometry, Point):
                    node_id = self._generate_node_id()
                    self.nodes[node_id] = Node(
                        id=node_id,
                        node_type='ObservationPoint',  # 观察点/观测点
                        x=row.geometry.x,
                        y=row.geometry.y,
                        geometry=row.geometry,
                        properties={
                            'lon': row_lonlat.geometry.x,
                            'lat': row_lonlat.geometry.y,
                            'source': 'standpoints.shp'
                        }
                    )

        print(f"  ✓ 共加载 {len(self.nodes)} 个点状节点")

    def _load_lines(self):
        """加载线路数据，将线路转换为节点和边，并建立线路间的连接"""
        print("\n2. 加载线路数据...")
        print("  - 坐标系: WGS84 (EPSG:4326) -> UTM投影 (米)")

        # 定义目标投影坐标系
        target_crs = "EPSG:32648"  # UTM Zone 48N
        source_crs = "EPSG:4326"   # WGS84

        line_files = [
            ("西安机场路网数据/network/network.shp", "NetworkRoad"),
            ("西安机场机位和道路SHP/线路_航空器.shp", "AircraftRoad"),
            ("西安机场机位和道路SHP/线路_保障车辆.shp", "ServiceVehicleRoad"),
            ("西安机场机位和道路SHP/线路_围场路.shp", "PerimeterRoad"),
            ("西安机场机位和道路SHP/线路_场外.shp", "ExternalRoad"),
        ]

        # 存储线路端点坐标，用于后续连接（使用投影坐标）
        line_endpoints = {}  # {(x, y): node_id}

        total_lines = 0
        for line_path, road_type in line_files:
            full_path = self.base_path / line_path
            if full_path.exists():
                gdf = gpd.read_file(full_path)
                # 如果没有CRS，设置为WGS84
                if gdf.crs is None:
                    gdf.crs = source_crs
                # 投影转换
                gdf_projected = gdf.to_crs(target_crs)
                print(f"  - 读取{road_type}: {len(gdf)} 条线路")

                for idx, (row_lonlat, row_proj) in enumerate(zip(gdf.iterrows(), gdf_projected.iterrows())):
                    _, row_lonlat = row_lonlat
                    _, row = row_proj

                    if isinstance(row.geometry, LineString):
                        coords = list(row.geometry.coords)

                        if len(coords) >= 2:
                            # 起点坐标（投影后，单位：米）
                            start_x, start_y = coords[0]
                            # 使用整数米作为key，避免浮点误差
                            start_key = (int(start_x), int(start_y))

                            # 终点坐标（投影后，单位：米）
                            end_x, end_y = coords[-1]
                            end_key = (int(end_x), int(end_y))

                            # 创建或复用起点节点
                            if start_key in line_endpoints:
                                start_node_id = line_endpoints[start_key]
                                start_node = self.nodes[start_node_id]
                            else:
                                start_node_id = self._generate_node_id()
                                start_node = Node(
                                    id=start_node_id,
                                    node_type=f'{road_type}_Node',
                                    x=start_x,
                                    y=start_y,
                                    geometry=Point(start_x, start_y),
                                    properties={'line_index': idx, 'line_type': road_type}
                                )
                                self.nodes[start_node_id] = start_node
                                line_endpoints[start_key] = start_node_id

                            # 创建或复用终点节点
                            if end_key in line_endpoints:
                                end_node_id = line_endpoints[end_key]
                                end_node = self.nodes[end_node_id]
                            else:
                                end_node_id = self._generate_node_id()
                                end_node = Node(
                                    id=end_node_id,
                                    node_type=f'{road_type}_Node',
                                    x=end_x,
                                    y=end_y,
                                    geometry=Point(end_x, end_y),
                                    properties={'line_index': idx, 'line_type': road_type}
                                )
                                self.nodes[end_node_id] = end_node
                                line_endpoints[end_key] = end_node_id

                            # 计算线路长度（投影后，单位：米）
                            line_length = row.geometry.length

                            # 创建双向边（起点到终点，终点到起点）
                            edge1 = Edge(
                                from_node=start_node,
                                to_node=end_node,
                                edge_type=road_type,
                                length=line_length,
                                geometry=row.geometry,
                                properties=dict(row_lonlat)
                            )

                            edge2 = Edge(
                                from_node=end_node,
                                to_node=start_node,
                                edge_type=road_type,
                                length=line_length,
                                geometry=row.geometry,
                                properties=dict(row_lonlat)
                            )

                            if start_node_id not in self.edges:
                                self.edges[start_node_id] = []
                            if end_node_id not in self.edges:
                                self.edges[end_node_id] = []

                            self.edges[start_node_id].append(edge1)
                            self.edges[end_node_id].append(edge2)

                            total_lines += 1

        print(f"  ✓ 共处理 {total_lines} 条线路，创建 {len(self.nodes) - len([n for n in self.nodes.values() if n.node_type in ['StandPoint', 'RunwayPoint', 'NetworkPoint']])} 个线路节点")

    def _build_topology(self, connection_threshold=500):
        """
        构建拓扑连接关系
        将点状节点连接到最近的线路节点

        参数:
            connection_threshold: 连接距离阈值（米）
        """
        print("\n3. 构建拓扑连接关系...")
        print(f"  - 连接阈值: {connection_threshold} 米")

        connections_created = 0

        # 获取所有点状节点
        point_nodes = [n for n in self.nodes.values()
                      if n.node_type in ['StandPoint', 'RunwayPoint', 'NetworkPoint']]

        # 获取所有线路节点
        line_nodes = [n for n in self.nodes.values()
                     if 'Road' in n.node_type]

        print(f"  - 点状节点数: {len(point_nodes)}")
        print(f"  - 线路节点数: {len(line_nodes)}")

        # 为每个点状节点找到最近的线路节点
        for point_node in point_nodes:
            # 计算到所有线路节点的距离
            distances = []
            for line_node in line_nodes:
                distance = math.sqrt((point_node.x - line_node.x)**2 +
                                   (point_node.y - line_node.y)**2)
                if distance <= connection_threshold:
                    distances.append((distance, line_node))

            # 按距离排序，只连接最近的5个线路节点（增加连接数量）
            distances.sort(key=lambda x: x[0])
            for distance, line_node in distances[:5]:
                # 创建双向连接
                edge1 = Edge(
                    from_node=point_node,
                    to_node=line_node,
                    edge_type='PROXIMITY',
                    length=distance,
                    speed_limit=15.0
                )

                edge2 = Edge(
                    from_node=line_node,
                    to_node=point_node,
                    edge_type='PROXIMITY',
                    length=distance,
                    speed_limit=15.0
                )

                if point_node.id not in self.edges:
                    self.edges[point_node.id] = []
                if line_node.id not in self.edges:
                    self.edges[line_node.id] = []

                self.edges[point_node.id].append(edge1)
                self.edges[line_node.id].append(edge2)

                connections_created += 2

        print(f"  ✓ 创建了 {connections_created} 个拓扑连接")

    def _print_statistics(self):
        """打印图统计信息"""
        print("\n" + "=" * 70)
        print("路网图统计信息")
        print("=" * 70)

        # 节点统计
        node_types = {}
        for node in self.nodes.values():
            base_type = node.node_type.split('_')[0]  # 去掉后缀
            node_types[base_type] = node_types.get(base_type, 0) + 1

        print("\n节点类型统计:")
        for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {node_type}: {count} 个")

        print(f"\n总节点数: {len(self.nodes)}")

        # 边统计
        edge_types = {}
        total_edges = 0
        for edge_list in self.edges.values():
            for edge in edge_list:
                edge_types[edge.edge_type] = edge_types.get(edge.edge_type, 0) + 1
                total_edges += 1

        print("\n边类型统计:")
        for edge_type, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {edge_type}: {count} 条")

        print(f"\n总边数: {total_edges}")

        # 连通性统计
        nodes_with_edges = sum(1 for edges in self.edges.values() if edges)
        print(f"\n有出边的节点数: {nodes_with_edges}")
        print(f"孤立节点数: {len(self.nodes) - nodes_with_edges}")

    def get_neighbors(self, node: Node) -> List[Edge]:
        """获取节点的邻居边"""
        return self.edges.get(node.id, [])

    def get_node(self, node_id: int) -> Optional[Node]:
        """根据ID获取节点"""
        return self.nodes.get(node_id)

    def find_nearest_node(self, x: float, y: float,
                         node_type: Optional[str] = None,
                         max_distance: float = 1000) -> Optional[Node]:
        """
        查找最近的节点

        参数:
            x: X坐标
            y: Y坐标
            node_type: 节点类型过滤（可选）
            max_distance: 最大搜索距离

        返回:
            最近的节点，如果没有找到则返回None
        """
        nearest_node = None
        min_distance = float('inf')

        for node in self.nodes.values():
            if node_type and not node.node_type.startswith(node_type):
                continue

            distance = math.sqrt((node.x - x)**2 + (node.y - y)**2)
            if distance < min_distance and distance <= max_distance:
                min_distance = distance
                nearest_node = node

        return nearest_node

    def find_nodes_by_type(self, node_type: str) -> List[Node]:
        """根据类型查找所有匹配的节点"""
        return [n for n in self.nodes.values() if n.node_type.startswith(node_type)]


class AStarOptimizer:
    """
    A*算法优化器，用于机场场面滑行路径规划

    参考文献：
    1. 基于蚁群算法的航空器滑行路径优化研究 - 目标函数和约束条件设计
    2. Weiszer et al. (2015) - 多目标优化方法
    """

    def __init__(self, graph: AirportGraph,
                 weight_distance: float = 1.0,
                 weight_time: float = 1.0,
                 weight_fuel: float = 0.5,
                 aircraft_speed: float = 15.0):
        """
        初始化A*优化器

        参数:
            graph: 机场路网图
            weight_distance: 距离权重
            weight_time: 时间权重
            weight_fuel: 燃料消耗权重
            aircraft_speed: 航空器平均滑行速度（米/秒）
        """
        self.graph = graph
        self.weight_distance = weight_distance
        self.weight_time = weight_time
        self.weight_fuel = weight_fuel
        self.aircraft_speed = aircraft_speed

    def heuristic(self, node: Node, goal: Node) -> float:
        """
        启发式函数（h函数）：估算从当前节点到目标节点的代价

        使用欧几里得距离作为启发式，保证可采纳性

        参数:
            node: 当前节点
            goal: 目标节点

        返回:
            估算代价
        """
        # 欧几里得距离
        distance = math.sqrt((node.x - goal.x)**2 + (node.y - goal.y)**2)

        # 转换为综合代价
        return self._calculate_cost(distance, distance / self.aircraft_speed)

    def _calculate_cost(self, distance: float, time: float) -> float:
        """
        计算边的代价（多目标优化）

        参考文献中的目标函数：
        - 最小化滑行距离
        - 最小化滑行时间
        - 最小化燃料消耗

        参数:
            distance: 距离（米）
            time: 时间（秒）

        返回:
            综合代价
        """
        # 燃料消耗估算：基于距离和时间
        # 简化模型：燃料消耗与距离和时间成正比
        fuel_consumption = distance * 0.1 + time * 0.05

        # 加权综合代价
        total_cost = (self.weight_distance * distance +
                     self.weight_time * time +
                     self.weight_fuel * fuel_consumption)

        return total_cost

    def find_path(self, start: Node, goal: Node) -> Tuple[Optional[List[Node]], Dict]:
        """
        使用A*算法查找最优路径

        参数:
            start: 起始节点
            goal: 目标节点

        返回:
            (路径, 统计信息字典)
        """
        # 初始化
        open_set = []  # 优先队列（开放集合）
        closed_set: Set[int] = set()  # 已访问节点集合
        path_nodes: Dict[int, PathNode] = {}  # node_id -> PathNode

        # 创建起始节点
        start_path_node = PathNode(
            f_score=self.heuristic(start, goal),
            g_score=0.0,
            node=start,
            parent=None
        )

        heapq.heappush(open_set, start_path_node)
        path_nodes[start.id] = start_path_node

        iterations = 0
        max_iterations = len(self.graph.nodes) * 2  # 防止无限循环

        while open_set and iterations < max_iterations:
            iterations += 1

            # 获取f_score最小的节点
            current = heapq.heappop(open_set)

            # 检查是否到达目标
            if current.node.id == goal.id:
                # 重建路径
                path = self._reconstruct_path(current)
                stats = self._calculate_path_stats(path)

                print(f"\n✓ 找到最优路径！")
                print(f"  - 迭代次数: {iterations}")
                print(f"  - 路径节点数: {stats['num_nodes']}")
                print(f"  - 路径长度: {stats['total_distance']:.2f} 米")
                print(f"  - 预计时间: {stats['total_time']:.2f} 秒 ({stats['total_time']/60:.2f} 分钟)")
                print(f"  - 燃料消耗: {stats['fuel_consumption']:.2f} 单位")
                print(f"  - 综合代价: {stats['total_cost']:.2f}")

                return path, stats

            # 将当前节点加入已访问集合
            closed_set.add(current.node.id)

            # 遍历邻居节点
            for edge in self.graph.get_neighbors(current.node):
                neighbor = edge.to_node

                # 如果已访问，跳过
                if neighbor.id in closed_set:
                    continue

                # 计算从起点到邻居的实际代价
                travel_time = edge.length / min(edge.speed_limit, self.aircraft_speed)
                tentative_g_score = current.g_score + self._calculate_cost(
                    edge.length, travel_time
                )

                # 检查是否需要更新邻居节点
                if neighbor.id not in path_nodes or tentative_g_score < path_nodes[neighbor.id].g_score:
                    # 创建新的路径节点
                    neighbor_path_node = PathNode(
                        f_score=tentative_g_score + self.heuristic(neighbor, goal),
                        g_score=tentative_g_score,
                        node=neighbor,
                        parent=current
                    )

                    path_nodes[neighbor.id] = neighbor_path_node
                    heapq.heappush(open_set, neighbor_path_node)

        # 未找到路径
        print(f"\n✗ 未找到路径（迭代次数: {iterations}）")
        return None, {
            'iterations': iterations,
            'error': '未找到路径'
        }

    def _reconstruct_path(self, path_node: PathNode) -> List[Node]:
        """从最终节点回溯重建路径"""
        path = []
        current = path_node

        while current is not None:
            path.append(current.node)
            current = current.parent

        path.reverse()
        return path

    def _calculate_path_stats(self, path: List[Node]) -> Dict:
        """计算路径统计信息"""
        total_distance = 0.0
        total_time = 0.0
        fuel_consumption = 0.0

        for i in range(len(path) - 1):
            current_node = path[i]
            next_node = path[i + 1]

            # 计算距离
            distance = math.sqrt((current_node.x - next_node.x)**2 +
                               (current_node.y - next_node.y)**2)
            total_distance += distance

            # 计算时间
            time = distance / self.aircraft_speed
            total_time += time

            # 计算燃料消耗
            fuel_consumption += distance * 0.1 + time * 0.05

        total_cost = self._calculate_cost(total_distance, total_time)

        return {
            'total_distance': total_distance,
            'total_time': total_time,
            'fuel_consumption': fuel_consumption,
            'total_cost': total_cost,
            'num_nodes': len(path)
        }

    def find_k_shortest_paths(self, start: Node, goal: Node, k: int = 3) -> List[Tuple[List[Node], Dict]]:
        """
        使用简化的方法查找K条最短路径
        
        这个实现使用边惩罚策略（edge penalty strategy）：
        每次找到一条路径后，惩罚该路径中的边，使得下次搜索会寻找不同的路径
        
        参数:
            start: 起始节点
            goal: 目标节点
            k: 需要的路径数量（默认3）
            
        返回:
            [(路径, 统计信息), ...]  # K条路径的列表
        """
        from dataclasses import replace
        
        paths = []
        
        # 用于惩罚边的字典：{(from_node, to_node): penalty_count}
        penalized_edges = {}
        
        for i in range(k):
            # 临时保存原始的get_neighbors方法
            original_get_neighbors = self.graph.get_neighbors
            
            def get_penalized_neighbors(node):
                """获取邻居节点，应用边惩罚"""
                original_neighbors = original_get_neighbors(node)
                if not original_neighbors:
                    return []
                
                filtered_neighbors = []
                for edge in original_neighbors:
                    edge_key = (node.id, edge.to_node.id)
                    # 如果这条边被惩罚，增加其代价
                    if edge_key in penalized_edges and penalized_edges[edge_key] > 0:
                        # 通过修改edge的length来增加代价
                        penalty_factor = 1.0 + penalized_edges[edge_key] * 0.5
                        # 创建一个新的edge对象，增加length
                        penalized_edge = replace(edge, length=edge.length * penalty_factor)
                        filtered_neighbors.append(penalized_edge)
                    else:
                        filtered_neighbors.append(edge)
                
                return filtered_neighbors
            
            # 临时替换get_neighbors方法
            self.graph.get_neighbors = get_penalized_neighbors
            
            try:
                # 运行A*搜索
                path, stats = self.find_path(start, goal)
                
                if path is None:
                    # 没有找到更多路径
                    break
                
                # 添加到结果列表
                paths.append((path, stats))
                
                # 惩罚这条路径中的边，使得下次搜索会找不同路径
                for j in range(len(path) - 1):
                    from_node = path[j]
                    to_node = path[j + 1]
                    edge_key = (from_node.id, to_node.id)
                    
                    if edge_key not in penalized_edges:
                        penalized_edges[edge_key] = 0
                    penalized_edges[edge_key] += 1
                    
            finally:
                # 恢复原始的get_neighbors方法
                self.graph.get_neighbors = original_get_neighbors
        
        if paths:
            print(f"\\n✓ 找到 {len(paths)} 条备选路径:")
            for i, (path, stats) in enumerate(paths, 1):
                print(f"  路径{i}: {stats['num_nodes']}个节点, "
                      f"{stats['total_distance']:.1f}m, "
                      f"{stats['total_time']/60:.1f}min")

        return paths



def demo_astar_optimization():
    """演示A*算法的路径优化功能"""
    print("\n" + "=" * 70)
    print("机场场面滑行轨迹优化 - A*算法演示")
    print("=" * 70)

    # 数据路径
    base_path = "/Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign/西安机场"

    # 创建路网图并加载数据
    graph = AirportGraph(base_path)
    graph.load_data()

    # 创建A*优化器
    optimizer = AStarOptimizer(
        graph=graph,
        weight_distance=1.0,  # 距离权重
        weight_time=1.0,      # 时间权重
        weight_fuel=0.5,      # 燃料权重
        aircraft_speed=15.0   # 滑行速度约54km/h
    )

    # 获取所有节点
    standpoints = graph.find_nodes_by_type('StandPoint')
    runwaypoints = graph.find_nodes_by_type('RunwayPoint')
    networkpoints = graph.find_nodes_by_type('NetworkPoint')

    print("\n" + "=" * 70)
    print("示例1: 距离最远的两个机位之间的路径规划")
    print("=" * 70)

    if len(standpoints) >= 2:
        # 找到距离最远的两个机位
        max_distance = 0
        best_pair = (standpoints[0], standpoints[1])

        for i, node1 in enumerate(standpoints):
            for node2 in standpoints[i+1:]:
                distance = math.sqrt((node1.x - node2.x)**2 +
                                   (node1.y - node2.y)**2)
                if distance > max_distance:
                    max_distance = distance
                    best_pair = (node1, node2)

        start_node, goal_node = best_pair

        print(f"\n起点: {start_node}")
        print(f"终点: {goal_node}")
        print(f"直线距离: {max_distance:.2f} 米 ({max_distance/1000:.3f} km)")
        print(f"经纬度跨度: ΔX={abs(start_node.x - goal_node.x):.4f}°, ΔY={abs(start_node.y - goal_node.y):.4f}°")

        # 执行A*算法
        path, stats = optimizer.find_path(start_node, goal_node)

        if path:
            print(f"\n最优路径分析:")
            print(f"  - 实际路径长度: {stats['total_distance']:.2f} 米")
            print(f"  - 路径迂回系数: {stats['total_distance']/max_distance:.2f}")
            print(f"  - 途径节点数: {stats['num_nodes']}")
            print(f"  - 预计滑行时间: {stats['total_time']/60:.2f} 分钟")
            print(f"  - 燃料消耗: {stats['fuel_consumption']:.2f} 单位")

            print(f"\n路径详细节点序列（前30个）:")
            for i, node in enumerate(path[:30]):
                if i < len(path) - 1:
                    next_node = path[i + 1]
                    distance = math.sqrt((node.x - next_node.x)**2 +
                                      (node.y - next_node.y)**2)
                    node_info = f"{node.node_type}"
                    if 'Road' in node.node_type:
                        node_info = f"线路节点"
                    print(f"  {i+1}. {node_info} (坐标: {node.x:.6f}, {node.y:.6f}) -> [距离: {distance:.2f}m]")
                else:
                    print(f"  {i+1}. {node.node_type} (到达目标)")

            if len(path) > 30:
                print(f"  ... (共 {len(path)} 个节点)")
        else:
            print(f"\n未找到路径 - {stats.get('error', '未知错误')}")
    else:
        print("\n未找到足够的机位节点")

    print("\n" + "=" * 70)
    print("示例2: 距离最远的机位到跑道点路径规划")
    print("=" * 70)

    if standpoints and runwaypoints:
        # 找到距离最远的机位和跑道点对
        max_distance = 0
        best_pair = (standpoints[0], runwaypoints[0])

        for stand in standpoints:
            for runway in runwaypoints:
                distance = math.sqrt((stand.x - runway.x)**2 +
                                   (stand.y - runway.y)**2)
                if distance > max_distance:
                    max_distance = distance
                    best_pair = (stand, runway)

        start_node, goal_node = best_pair

        print(f"\n起点: {start_node}")
        print(f"终点: {goal_node}")
        print(f"直线距离: {max_distance:.2f} 米 ({max_distance/1000:.3f} km)")
        print(f"经纬度跨度: ΔX={abs(start_node.x - goal_node.x):.4f}°, ΔY={abs(start_node.y - goal_node.y):.4f}°")

        # 执行A*算法
        path, stats = optimizer.find_path(start_node, goal_node)

        if path:
            print(f"\n最优路径分析:")
            print(f"  - 实际路径长度: {stats['total_distance']:.2f} 米")
            print(f"  - 路径迂回系数: {stats['total_distance']/max_distance:.2f}")
            print(f"  - 途径节点数: {stats['num_nodes']}")
            print(f"  - 预计滑行时间: {stats['total_time']/60:.2f} 分钟")
            print(f"  - 燃料消耗: {stats['fuel_consumption']:.2f} 单位")

            print(f"\n路径详细节点序列（前30个）:")
            for i, node in enumerate(path[:30]):
                if i < len(path) - 1:
                    next_node = path[i + 1]
                    distance = math.sqrt((node.x - next_node.x)**2 +
                                      (node.y - next_node.y)**2)
                    node_info = f"{node.node_type}"
                    if 'Road' in node.node_type:
                        node_info = f"线路节点"
                    print(f"  {i+1}. {node_info} (坐标: {node.x:.6f}, {node.y:.6f}) -> [距离: {distance:.2f}m]")
                else:
                    print(f"  {i+1}. {node.node_type} (到达目标)")

            if len(path) > 30:
                print(f"  ... (共 {len(path)} 个节点)")
        else:
            print(f"\n未找到路径 - {stats.get('error', '未知错误')}")
    else:
        print("\n未找到足够的节点")

    print("\n" + "=" * 70)
    print("示例3: 横跨机场的复杂路径（路网点到路网点）")
    print("=" * 70)

    if len(networkpoints) >= 2:
        # 找到距离最远的两个路网点
        max_distance = 0
        best_pair = (networkpoints[0], networkpoints[1])

        for i, node1 in enumerate(networkpoints):
            for node2 in networkpoints[i+1:]:
                distance = math.sqrt((node1.x - node2.x)**2 +
                                   (node1.y - node2.y)**2)
                if distance > max_distance:
                    max_distance = distance
                    best_pair = (node1, node2)

        start_node, goal_node = best_pair

        print(f"\n起点: {start_node}")
        print(f"终点: {goal_node}")
        print(f"直线距离: {max_distance:.2f} 米 ({max_distance/1000:.3f} km)")
        print(f"经纬度跨度: ΔX={abs(start_node.x - goal_node.x):.4f}°, ΔY={abs(start_node.y - goal_node.y):.4f}°")

        # 执行A*算法
        path, stats = optimizer.find_path(start_node, goal_node)

        if path:
            print(f"\n最优路径分析:")
            print(f"  - 实际路径长度: {stats['total_distance']:.2f} 米")
            print(f"  - 路径迂回系数: {stats['total_distance']/max_distance:.2f}")
            print(f"  - 途径节点数: {stats['num_nodes']}")
            print(f"  - 预计滑行时间: {stats['total_time']/60:.2f} 分钟")
            print(f"  - 燃料消耗: {stats['fuel_consumption']:.2f} 单位")

            print(f"\n路径详细节点序列（前40个）:")
            for i, node in enumerate(path[:40]):
                if i < len(path) - 1:
                    next_node = path[i + 1]
                    distance = math.sqrt((node.x - next_node.x)**2 +
                                      (node.y - next_node.y)**2)
                    node_info = f"{node.node_type}"
                    if 'Road' in node.node_type:
                        node_info = f"线路节点"
                    print(f"  {i+1}. {node_info} (坐标: {node.x:.6f}, {node.y:.6f}) -> [距离: {distance:.2f}m]")
                else:
                    print(f"  {i+1}. {node.node_type} (到达目标)")

            if len(path) > 40:
                print(f"  ... (共 {len(path)} 个节点)")
        else:
            print(f"\n未找到路径 - {stats.get('error', '未知错误')}")
    else:
        print("\n未找到足够的路网节点")

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)


def main():
    """主函数"""
    print("\n机场场面滑行轨迹优化 - 基于A*算法的路径规划")
    print("\n参考理论:")
    print("  1. A*算法：结合实际代价和启发式估计的最优路径搜索")
    print("  2. 多目标优化：距离、时间、燃料消耗的加权优化")
    print("  3. 机场约束：速度限制、路径连续性")
    print("\n数据来源: GeoPandas直接读取SHP文件")

    # 运行演示
    demo_astar_optimization()


if __name__ == "__main__":
    main()
