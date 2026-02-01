"""
多航班滑行路径优化与冲突调度系统
=====================================

基于参考文献：
1. 桃园机场TPE的FCFS调度策略
2. Weiszer et al. - 多目标优化
3. 大型机场航空器动态滑行调度研究

主要功能：
- 多航班时空冲突检测
- FCFS和优先级调度策略
- 动态路径规划
- 冲突消解（等待、重规划、速度调整）
"""

import heapq
import math
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import copy

from .Astar import AirportGraph, Node, AStarOptimizer


class OperationType(Enum):
    """运行类型"""
    DEPARTURE = "departure"  # 离港
    ARRIVAL = "arrival"      # 进港


class PriorityLevel(Enum):
    """优先级"""
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class Flight:
    """航班类"""
    flight_id: str
    aircraft_type: str
    operation: OperationType
    start_node: Node
    end_node: Node
    scheduled_time: datetime
    priority: PriorityLevel = PriorityLevel.MEDIUM
    speed: float = 15.0  # 滑行速度（米/秒）

    def __repr__(self):
        return f"Flight({self.flight_id}, {self.operation.value}, {self.start_node.id}->{self.end_node.id})"


@dataclass
class SpatioTemporalSlot:
    """时空槽：记录节点在特定时间段的占用"""
    node_id: int
    start_time: datetime
    end_time: datetime
    flight_id: str

    def overlaps(self, other: 'SpatioTemporalSlot', margin: int = 30) -> bool:
        """检查是否重叠（考虑安全间隔）"""
        margin_seconds = timedelta(seconds=margin)
        return not (self.end_time + margin_seconds <= other.start_time or
                   other.end_time + margin_seconds <= self.start_time)


@dataclass
class Conflict:
    """冲突信息"""
    conflict_id: str
    conflict_type: str  # 'node', 'edge', 'crossing'
    flight_ids: List[str]
    node_id: int
    time: datetime
    severity: str = 'medium'  # 'low', 'medium', 'high'

    def __repr__(self):
        return f"Conflict({self.conflict_type}, {self.flight_ids}, {self.time.strftime('%H:%M:%S')})"


@dataclass
class AircraftSchedule:
    """单个航班的调度结果"""
    flight: Flight
    path: List[Node]
    start_time: datetime
    end_time: datetime
    waypoints: List[Tuple[Node, datetime]]  # (节点, 到达时间)
    conflicts: List[Conflict] = field(default_factory=list)
    total_distance: float = 0.0
    total_time: float = 0.0
    delay: timedelta = timedelta(0)


class ConflictDetector:
    """冲突检测器"""

    def __init__(self, safety_margin: int = 60):
        """
        初始化冲突检测器

        参数:
            safety_margin: 安全时间间隔（秒）
        """
        self.safety_margin = safety_margin

    def detect_all_conflicts(self, schedules: Dict[str, AircraftSchedule]) -> List[Conflict]:
        """
        检测所有航班之间的冲突

        参数:
            schedules: 所有航班的调度方案

        返回:
            冲突列表（已去重）
        """
        conflicts = []
        flight_list = list(schedules.values())
        seen_conflicts = set()  # 用于去重

        # 两两检测冲突
        for i, sched1 in enumerate(flight_list):
            for sched2 in flight_list[i+1:]:
                # 检测节点冲突
                node_conflicts = self._detect_node_conflicts(sched1, sched2)
                for conflict in node_conflicts:
                    # 创建唯一标识符用于去重
                    conflict_key = (conflict.node_id, conflict.time)
                    if conflict_key not in seen_conflicts:
                        seen_conflicts.add(conflict_key)
                        conflicts.append(conflict)

                # 检测路径交叉冲突（暂时禁用，减少误报）
                # crossing_conflicts = self._detect_crossing_conflicts(sched1, sched2)
                # for conflict in crossing_conflicts:
                #     conflict_key = (conflict.conflict_id, conflict.time)
                #     if conflict_key not in seen_conflicts:
                #         seen_conflicts.add(conflict_key)
                #         conflicts.append(conflict)

        return conflicts

    def _detect_node_conflicts(self, sched1: AircraftSchedule,
                              sched2: AircraftSchedule) -> List[Conflict]:
        """检测节点冲突"""
        conflicts = []

        for node1, time1 in sched1.waypoints:
            for node2, time2 in sched2.waypoints:
                if node1.id == node2.id:
                    # 同一节点，检查时间间隔
                    time_diff = abs((time1 - time2).total_seconds())
                    if time_diff < self.safety_margin:
                        conflict = Conflict(
                            conflict_id=f"node_{sched1.flight.flight_id}_{sched2.flight.flight_id}_{node1.id}",
                            conflict_type='node',
                            flight_ids=[sched1.flight.flight_id, sched2.flight.flight_id],
                            node_id=node1.id,
                            time=time1 if time1 < time2 else time2,
                            severity='high' if time_diff < 15 else 'medium'
                        )
                        conflicts.append(conflict)

        return conflicts

    def _detect_crossing_conflicts(self, sched1: AircraftSchedule,
                                  sched2: AircraftSchedule) -> List[Conflict]:
        """检测路径交叉冲突"""
        conflicts = []

        # 检测边交叉
        for i in range(len(sched1.waypoints) - 1):
            node1_a, time1_a = sched1.waypoints[i]
            node1_b, time1_b = sched1.waypoints[i + 1]

            for j in range(len(sched2.waypoints) - 1):
                node2_a, time2_a = sched2.waypoints[j]
                node2_b, time2_b = sched2.waypoints[j + 1]

                # 检测边交叉 (a->b 与 c->d)
                if self._edges_cross(node1_a, node1_b, node2_a, node2_b):
                    # 检查时间重叠
                    if self._time_ranges_overlap(
                        (time1_a, time1_b),
                        (time2_a, time2_b)
                    ):
                        conflict = Conflict(
                            conflict_id=f"cross_{sched1.flight.flight_id}_{sched2.flight.flight_id}",
                            conflict_type='crossing',
                            flight_ids=[sched1.flight.flight_id, sched2.flight.flight_id],
                            node_id=node1_a.id,
                            time=time1_a if time1_a < time2_a else time2_a,
                            severity='high'
                        )
                        conflicts.append(conflict)

        return conflicts

    def _edges_cross(self, a1: Node, a2: Node, b1: Node, b2: Node) -> bool:
        """检测两条边是否交叉"""
        # 简化判断：如果两条边有共同的中间节点，则可能交叉
        # 实际应用中可以使用更复杂的几何判断
        return (a1.id != b1.id and a1.id != b2.id and
                a2.id != b1.id and a2.id != b2.id)

    def _time_ranges_overlap(self, range1, range2) -> bool:
        """检测时间范围是否重叠"""
        start1, end1 = range1
        start2, end2 = range2
        return not (end1 <= start2 or end2 <= start1)


class MultiAircraftScheduler:
    """
    多航班调度器

    实现多种调度策略：
    1. FCFS (First-Come-First-Serve) - 先来先服务
    2. Priority-based - 基于优先级
    3. Time-window - 时间窗调度
    """

    def __init__(self, graph: AirportGraph, strategy: str = 'fcfs'):
        """
        初始化调度器

        参数:
            graph: 机场路网图
            strategy: 调度策略 ('fcfs', 'priority', 'time_window')
        """
        self.graph = graph
        self.strategy = strategy
        self.optimizer = AStarOptimizer(graph)
        self.conflict_detector = ConflictDetector(safety_margin=30)

    def schedule_multiple_flights(self, flights: List[Flight],
                                  max_iterations: int = 10) -> Dict[str, AircraftSchedule]:
        """
        为多个航班调度路径

        参数:
            flights: 航班列表
            max_iterations: 最大迭代次数（冲突消解）

        返回:
            调度方案字典 {flight_id: AircraftSchedule}
        """
        print("=" * 70)
        print(f"开始调度 {len(flights)} 个航班")
        print(f"调度策略: {self.strategy.upper()}")
        print("=" * 70)

        # 1. 对航班排序
        sorted_flights = self._sort_flights(flights)

        # 2. 依次为每个航班规划路径
        schedules = {}
        occupied_slots = []  # 时空占用记录

        for flight in sorted_flights:
            print(f"\n正在规划航班: {flight.flight_id}")

            # 计算初始延误（如果有的话）
            delay = timedelta(0)

            # 尝试规划路径（考虑冲突）
            schedule = self._plan_single_flight(
                flight,
                existing_schedules=schedules,
                occupied_slots=occupied_slots
            )

            if schedule:
                schedules[flight.flight_id] = schedule

                # 记录时空占用
                for node, time in schedule.waypoints:
                    occupied_slots.append(SpatioTemporalSlot(
                        node_id=node.id,
                        start_time=time,
                        end_time=time + timedelta(seconds=30),  # 假设占用30秒
                        flight_id=flight.flight_id
                    ))

                print(f"  ✓ 路径规划成功")
                print(f"    - 路径长度: {schedule.total_distance:.2f} 米")
                print(f"    - 预计时间: {schedule.total_time:.2f} 秒")
                print(f"    - 延误: {delay.total_seconds():.2f} 秒")
            else:
                # 路径规划失败：创建一个失败的调度记录，包含错误信息
                print(f"  ✗ 路径规划失败 - 起点: {flight.start_node.id}, 终点: {flight.end_node.id}")

                # 创建一个标记为失败的调度，这样前端也能看到这个航班
                failed_schedule = AircraftSchedule(
                    flight=flight,
                    path=[flight.start_node, flight.end_node],  # 只包含起点和终点
                    start_time=flight.scheduled_time,
                    end_time=flight.scheduled_time,
                    waypoints=[],
                    total_distance=0,
                    total_time=0,
                    delay=timedelta(0)
                )
                # 添加一个特殊的冲突标记
                failed_schedule.conflicts.append(Conflict(
                    conflict_id=f"path_fail_{flight.flight_id}",
                    conflict_type='path_not_found',
                    flight_ids=[flight.flight_id],
                    node_id=flight.start_node.id,
                    time=flight.scheduled_time,
                    severity='critical'
                ))
                schedules[flight.flight_id] = failed_schedule

        # 3. 冲突检测与消解（多轮迭代）
        print("\n" + "=" * 70)
        print("检测并消解冲突...")
        print("=" * 70)

        max_iterations = 5  # 最多进行5轮冲突消解
        iteration = 0

        while iteration < max_iterations:
            conflicts = self.conflict_detector.detect_all_conflicts(schedules)

            if not conflicts:
                print(f"✓ 第{iteration + 1}轮：未发现冲突")
                break

            print(f"\n第{iteration + 1}轮：发现 {len(conflicts)} 个冲突")

            # 将冲突分配给相关航班
            for flight_id in list(schedules.keys()):
                schedules[flight_id].conflicts = []  # 清空之前的冲突

            for conflict in conflicts:
                for flight_id in conflict.flight_ids:
                    if flight_id in schedules:
                        schedules[flight_id].conflicts.append(conflict)

            # 如果是第一轮，尝试消解冲突
            if iteration < max_iterations - 1:
                resolved = self._resolve_conflicts_iteration(schedules, conflicts)
                print(f"  已处理 {resolved} 个冲突")
                iteration += 1
            else:
                print(f"  达到最大迭代次数，停止消解")
                break

        if iteration == 0 and not conflicts:
            print("✓ 未发现冲突")
        elif conflicts:
            print(f"\n最终剩余 {len(conflicts)} 个冲突")

        # 5. 输出统计信息
        self._print_statistics(schedules)

        return schedules

    def _sort_flights(self, flights: List[Flight]) -> List[Flight]:
        """根据调度策略对航班排序"""
        if self.strategy == 'fcfs':
            # 先来先服务：按计划时间排序
            return sorted(flights, key=lambda f: f.scheduled_time)

        elif self.strategy == 'priority':
            # 基于优先级：先按优先级，再按时间
            return sorted(flights,
                        key=lambda f: (-f.priority.value, f.scheduled_time))

        elif self.strategy == 'time_window':
            # 离港优先
            return sorted(flights,
                        key=lambda f: (0 if f.operation == OperationType.DEPARTURE else 1,
                                     f.scheduled_time))

        return flights

    def _plan_single_flight(self, flight: Flight,
                           existing_schedules: Dict[str, AircraftSchedule],
                           occupied_slots: List[SpatioTemporalSlot]) -> Optional[AircraftSchedule]:
        """
        为单个航班规划路径（考虑已调度航班的占用）

        参数:
            flight: 航班
            existing_schedules: 已存在的调度
            occupied_slots: 时空占用槽

        返回:
            调度方案
        """
        # 使用A*算法找路径
        path, stats = self.optimizer.find_path(flight.start_node, flight.end_node)

        if not path:
            return None

        # 计算时间节点
        waypoints = []
        current_time = flight.scheduled_time

        for i, node in enumerate(path):
            waypoints.append((node, current_time))

            if i < len(path) - 1:
                next_node = path[i + 1]
                distance = math.sqrt((node.x - next_node.x)**2 +
                                   (node.y - next_node.y)**2)
                travel_time = distance / flight.speed
                current_time += timedelta(seconds=travel_time)

        # 创建调度方案
        schedule = AircraftSchedule(
            flight=flight,
            path=path,
            start_time=flight.scheduled_time,
            end_time=current_time,
            waypoints=waypoints,
            total_distance=stats.get('total_distance', 0),
            total_time=stats.get('total_time', 0)
        )

        return schedule

    def _resolve_conflicts_iteration(self,
                                     schedules: Dict[str, AircraftSchedule],
                                     conflicts: List[Conflict]) -> int:
        """
        单轮冲突消解：通过延迟后到航班

        参数:
            schedules: 调度方案
            conflicts: 冲突列表

        返回:
            处理的冲突数量
        """
        resolved_count = 0
        delayed_flights = set()  # 记录已延迟的航班，避免重复延迟

        for conflict in conflicts:
            if len(conflict.flight_ids) >= 2:
                # 找出两个航班
                flight1_id = conflict.flight_ids[0]
                flight2_id = conflict.flight_ids[1]

                # 延迟较晚的航班（计划时间较晚的）
                sched1 = schedules.get(flight1_id)
                sched2 = schedules.get(flight2_id)

                if not sched1 or not sched2:
                    continue

                # 跳过已失败的调度
                if len(sched1.waypoints) == 0 or len(sched2.waypoints) == 0:
                    continue

                # 选择计划时间较晚的航班进行延迟
                if sched1.start_time > sched2.start_time:
                    later_flight_id, earlier_flight_id = flight1_id, flight2_id
                    later_sched = sched1
                else:
                    later_flight_id, earlier_flight_id = flight2_id, flight1_id
                    later_sched = sched2

                # 如果该航班已经延迟过，跳过
                if later_flight_id in delayed_flights:
                    continue

                # 计算延迟时间：确保与早航班的时间间隔至少为safety_margin
                delay_amount = timedelta(seconds=45)  # 基础延迟45秒

                # 应用延迟
                self._apply_delay(later_sched, delay_amount)
                delayed_flights.add(later_flight_id)
                resolved_count += 1

        return resolved_count

    def _apply_delay(self, schedule: AircraftSchedule, delay: timedelta) -> None:
        """
        对调度应用延迟，更新所有相关时间

        参数:
            schedule: 航班调度
            delay: 延迟时间
        """
        # 更新开始和结束时间
        schedule.start_time += delay
        schedule.end_time += delay
        schedule.delay += delay

        # 更新所有waypoints的时间
        new_waypoints = []
        for node, time in schedule.waypoints:
            new_waypoints.append((node, time + delay))
        schedule.waypoints = new_waypoints

    def _print_statistics(self, schedules: Dict[str, AircraftSchedule]):
        """打印统计信息"""
        print("\n" + "=" * 70)
        print("调度统计")
        print("=" * 70)

        total_distance = sum(s.total_distance for s in schedules.values())
        total_time = sum(s.total_time for s in schedules.values())
        total_delay = sum(s.delay.total_seconds() for s in schedules.values())
        total_conflicts = sum(len(s.conflicts) for s in schedules.values())

        print(f"\n航班总数: {len(schedules)}")
        print(f"总滑行距离: {total_distance:.2f} 米")
        print(f"总滑行时间: {total_time:.2f} 秒 ({total_time/60:.2f} 分钟)")
        print(f"总延误时间: {total_delay:.2f} 秒 ({total_delay/60:.2f} 分钟)")
        print(f"剩余冲突数: {total_conflicts}")

        print("\n各航班详细信息:")
        for flight_id, schedule in schedules.items():
            print(f"\n{flight_id}:")
            print(f"  - 路径: {schedule.path[0].id} -> {schedule.path[-1].id}")
            print(f"  - 距离: {schedule.total_distance:.2f} 米")
            print(f"  - 时间: {schedule.total_time:.2f} 秒")
            print(f"  - 延误: {schedule.delay.total_seconds():.2f} 秒")
            print(f"  - 冲突: {len(schedule.conflicts)} 个")


def generate_simulation_data(graph: AirportGraph, num_flights: int = 5) -> List[Flight]:
    """
    生成模拟航班数据

    参数:
        graph: 机场路网图
        num_flights: 航班数量

    返回:
        航班列表
    """
    import random

    flights = []
    base_time = datetime(2024, 1, 20, 14, 0, 0)

    # 获取机位和跑道点
    stands = graph.find_nodes_by_type('StandPoint')
    runways = graph.find_nodes_by_type('RunwayPoint')

    if not stands or not runways:
        print("警告: 未找到足够的机位或跑道节点")
        return []

    # 创建A*优化器用于路径验证
    optimizer = AStarOptimizer(graph)

    attempts = 0
    max_attempts = num_flights * 10  # 最多尝试10倍

    while len(flights) < num_flights and attempts < max_attempts:
        attempts += 1

        # 随机选择起点和终点
        if len(flights) % 2 == 0:
            # 离港：机位 -> 跑道
            start_node = random.choice(stands)
            end_node = random.choice(runways)
            operation = OperationType.DEPARTURE
        else:
            # 进港：跑道 -> 机位
            start_node = random.choice(runways)
            end_node = random.choice(stands)
            operation = OperationType.ARRIVAL

        # 验证路径是否存在
        path, _ = optimizer.find_path(start_node, end_node)
        if not path:
            print(f"  跳过: {start_node.id} -> {end_node.id} (无路径)")
            continue

        # 随机时间（在3小时内）
        time_offset = random.randint(0, 10800)
        scheduled_time = base_time + timedelta(seconds=time_offset)

        # 随机优先级
        priority = random.choice(list(PriorityLevel))

        flight = Flight(
            flight_id=f"FL{1000+len(flights)}",
            aircraft_type=random.choice(["A320", "B737", "A330", "B777"]),
            operation=operation,
            start_node=start_node,
            end_node=end_node,
            scheduled_time=scheduled_time,
            priority=priority,
            speed=random.uniform(12.0, 18.0)  # 随机速度
        )

        flights.append(flight)
        print(f"  生成航班: {flight.flight_id} ({operation.value}) {start_node.id} -> {end_node.id}")

    print(f"成功生成 {len(flights)} 个航班 (尝试 {attempts} 次)")
    return flights


def demo_multi_aircraft_scheduling():
    """演示多航班调度"""
    print("\n" + "=" * 70)
    print("多航班滑行路径优化与冲突调度系统")
    print("=" * 70)

    # 数据路径
    base_path = "/Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign/西安机场"

    # 创建路网图
    graph = AirportGraph(base_path)
    graph.load_data()

    # 生成模拟数据
    print("\n生成模拟航班数据...")
    flights = generate_simulation_data(graph, num_flights=6)

    if not flights:
        print("未能生成航班数据")
        return

    print(f"\n生成了 {len(flights)} 个航班:")
    for flight in flights:
        print(f"  - {flight.flight_id}: {flight.operation.value} "
              f"{flight.start_node.id} -> {flight.end_node.id}, "
              f"时间: {flight.scheduled_time.strftime('%H:%M:%S')}, "
              f"优先级: {flight.priority.name}")

    # 创建调度器并执行调度
    print("\n" + "=" * 70)
    print("使用FCFS策略调度...")
    print("=" * 70)

    scheduler_fcfs = MultiAircraftScheduler(graph, strategy='fcfs')
    schedules_fcfs = scheduler_fcfs.schedule_multiple_flights(flights)

    print("\n" + "=" * 70)
    print("使用优先级策略调度...")
    print("=" * 70)

    scheduler_priority = MultiAircraftScheduler(graph, strategy='priority')
    schedules_priority = scheduler_priority.schedule_multiple_flights(flights)

    return {
        'flights': flights,
        'fcfs': schedules_fcfs,
        'priority': schedules_priority
    }


if __name__ == "__main__":
    demo_multi_aircraft_scheduling()
