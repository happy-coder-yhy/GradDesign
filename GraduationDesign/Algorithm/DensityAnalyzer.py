"""
航班密度分析器
用于根据单位时间内的航班密度识别高峰期与低峰期
并提供多目标A*算法权重的动态调整建议
"""

from typing import List, Dict, TYPE_CHECKING
from datetime import datetime, timedelta
import statistics

if TYPE_CHECKING:
    from .MultiAircraftScheduler import Flight


class DensityAnalyzer:
    """
    航班密度分析器

    功能：
    1. 分析航班时间分布，识别高峰期和低峰期
    2. 根据时间段类型动态调整A*算法权重
    3. 提供当前时间段的权重建议
    """

    def __init__(self, time_window_minutes: int = 30, peak_threshold: float = 0.6):
        """
        初始化密度分析器

        参数:
            time_window_minutes: 时间窗口大小（分钟），默认30分钟
            peak_threshold: 高峰期阈值（密度百分比），默认0.6（60%）
        """
        self.time_window_minutes = time_window_minutes
        self.peak_threshold = peak_threshold

        # 权重配置模板
        self.weight_templates = {
            'peak': {
                'distance': 1.0,
                'time': 1.5,      # 高峰期提升滑行时间权重
                'fuel': 0.3       # 高峰期降低燃料损耗权重
            },
            'off_peak': {
                'distance': 1.0,
                'time': 0.7,      # 低峰期降低滑行时间权重
                'fuel': 0.8       # 低峰期提升燃料损耗权重
            },
            'normal': {
                'distance': 1.0,
                'time': 1.0,      # 正常权重
                'fuel': 0.5       # 正常权重
            }
        }

    def analyze_density(self, flights: List) -> Dict:
        """
        分析航班密度，识别高峰期和低峰期

        参数:
            flights: 航班列表

        返回:
            包含分析结果的字典：
            {
                'time_windows': list,  # 时间窗口列表
                'densities': list,     # 每个窗口的航班密度
                'average_density': float,  # 平均密度
                'peak_windows': list,  # 高峰期时间窗口
                'off_peak_windows': list,  # 低峰期时间窗口
                'normal_windows': list  # 正常期时间窗口
            }
        """
        if not flights:
            return {
                'time_windows': [],
                'densities': [],
                'average_density': 0,
                'peak_windows': [],
                'off_peak_windows': [],
                'normal_windows': []
            }

        # 1. 提取航班时间并排序
        flight_times = [flight.scheduled_time for flight in flights]
        flight_times.sort()

        # 2. 确定时间范围
        start_time = flight_times[0]
        end_time = flight_times[-1]

        # 3. 创建时间窗口
        time_windows = []
        current_time = start_time
        window_duration = timedelta(minutes=self.time_window_minutes)

        while current_time < end_time + window_duration:
            window_end = current_time + window_duration
            time_windows.append((current_time, window_end))
            current_time = window_end

        # 4. 计算每个时间窗口的航班数量
        window_counts = []
        for window_start, window_end in time_windows:
            count = sum(1 for ft in flight_times if window_start <= ft < window_end)
            window_counts.append(count)

        # 5. 计算密度（航班数量/时间窗口长度，转换为每小时的航班数）
        densities = [count / (self.time_window_minutes / 60) for count in window_counts]

        # 6. 识别高峰期和低峰期
        # 基于机场运营标准的绝对判断方法
        # 
        # 参考依据：
        # - ICAO Doc 9974: 机场容量评估标准
        # - 中国民航局《机场航班时刻容量评估办法》
        # - 西安咸阳国际机场为大型枢纽机场，设计容量约60-70架次/小时
        #
        # 高峰/低峰判断标准（基于机场容量百分比）：
        # - 高峰时段: > 40 航班/小时 (约60-70%容量)
        # - 正常时段: 15-40 航班/小时
        # - 低峰时段: < 15 航班/小时
        
        AIRPORT_CAPACITY = 60  # 西安机场设计容量（航班/小时）
        PEAK_THRESHOLD = 40    # 高峰阈值：40 航班/小时
        OFF_PEAK_THRESHOLD = 15  # 低峰阈值：15 航班/小时
        
        if len(densities) > 0:
            peak_windows = []
            off_peak_windows = []
            normal_windows = []

            for i, density in enumerate(densities):
                # 使用绝对阈值判断，而非相对平均值
                if density >= PEAK_THRESHOLD:
                    peak_windows.append(time_windows[i])
                elif density <= OFF_PEAK_THRESHOLD:
                    off_peak_windows.append(time_windows[i])
                else:
                    normal_windows.append(time_windows[i])

        else:
            peak_windows = []
            off_peak_windows = []
            normal_windows = []
            
        # 计算平均密度用于显示
        avg_density = statistics.mean(densities) if densities else 0

        return {
            'time_windows': time_windows,
            'densities': densities,
            'average_density': avg_density,
            'peak_windows': peak_windows,
            'off_peak_windows': off_peak_windows,
            'normal_windows': normal_windows,
            'flight_count': len(flights),
            'time_range': {
                'start': start_time,
                'end': end_time,
                'duration_hours': (end_time - start_time).total_seconds() / 3600
            }
        }

    def get_period_for_time(self, flights: List, query_time: datetime) -> str:
        """
        获取指定时间点所属的时间段类型

        参数:
            flights: 航班列表（用于密度分析）
            query_time: 查询的时间点

        返回:
            'peak' - 高峰期
            'off_peak' - 低峰期
            'normal' - 正常期
            'unknown' - 未知（无航班数据）
        """
        if not flights:
            return 'unknown'

        analysis = self.analyze_density(flights)

        # 检查查询时间属于哪个时间窗口
        for i, (window_start, window_end) in enumerate(analysis['time_windows']):
            if window_start <= query_time < window_end:
                # 检查该窗口属于哪种类型
                if (window_start, window_end) in analysis['peak_windows']:
                    return 'peak'
                elif (window_start, window_end) in analysis['off_peak_windows']:
                    return 'off_peak'
                else:
                    return 'normal'

        # 如果查询时间不在任何窗口内，根据机场运营规律推断
        # 参考机场运营数据和中国民航航班时刻分布
        avg_density = analysis['average_density']
        
        # 绝对判断标准
        PEAK_THRESHOLD = 40    # 高峰阈值：40 航班/小时
        OFF_PEAK_THRESHOLD = 15  # 低峰阈值：15 航班/小时
        
        if avg_density > 0:
            hour = query_time.hour
            weekday = query_time.weekday()  # 0=周一, 6=周日

            # 判断是否为工作日
            is_weekday = weekday < 5

            # 首先根据实际密度判断
            if avg_density >= PEAK_THRESHOLD:
                return 'peak'
            elif avg_density <= OFF_PEAK_THRESHOLD:
                return 'off_peak'
            
            # 如果密度处于临界值，再根据时间段推断
            if is_weekday:
                # 工作日典型高峰时段
                if (7 <= hour <= 10) or (17 <= hour <= 21):
                    return 'peak' if avg_density >= 35 else 'normal'
                elif (0 <= hour <= 5):
                    return 'off_peak'
                else:
                    return 'normal'
            else:
                # 周末时段
                if (9 <= hour <= 12) or (15 <= hour <= 20):
                    return 'peak' if avg_density >= 35 else 'normal'
                elif (0 <= hour <= 7):
                    return 'off_peak'
                else:
                    return 'normal'

        return 'unknown'

    def get_weights_for_period(self, period_type: str) -> Dict[str, float]:
        """
        根据时间段类型获取权重配置

        参数:
            period_type: 时间段类型 ('peak', 'off_peak', 'normal', 'unknown')

        返回:
            权重字典 {'distance': float, 'time': float, 'fuel': float}
        """
        if period_type in self.weight_templates:
            return self.weight_templates[period_type].copy()
        else:
            # 未知类型返回正常权重
            return self.weight_templates['normal'].copy()

    def get_current_weights(self, flights: List, current_time: datetime = None) -> Dict:
        """
        获取当前时间点的权重配置

        参数:
            flights: 航班列表
            current_time: 当前时间（如果为None则使用当前系统时间）

        返回:
            {
                'period_type': str,
                'weights': Dict[str, float],
                'description': str
            }
        """
        if current_time is None:
            current_time = datetime.now()

        period_type = self.get_period_for_time(flights, current_time)
        weights = self.get_weights_for_period(period_type)

        # 生成描述文本
        descriptions = {
            'peak': '高峰期 - 优先考虑滑行时间（准点率）',
            'off_peak': '低峰期 - 优先考虑燃料消耗（经济性）',
            'normal': '正常期 - 平衡滑行时间和燃料消耗',
            'unknown': '数据不足 - 使用默认权重'
        }

        return {
            'period_type': period_type,
            'weights': weights,
            'description': descriptions.get(period_type, '未知时间段'),
            'current_time': current_time
        }


def demo_density_analysis():
    """演示密度分析功能"""
    print("\n" + "=" * 70)
    print("航班密度分析演示")
    print("=" * 70)

    # 创建模拟航班数据
    from .MultiAircraftScheduler import generate_simulation_data
    from .Astar import AirportGraph

    # 需要机场路网图来生成模拟数据
    base_path = "/Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign/西安机场"
    graph = AirportGraph(base_path)
    graph.load_data()

    # 生成航班
    flights = generate_simulation_data(graph, num_flights=10)

    if not flights:
        print("未能生成航班数据")
        return

    print(f"生成了 {len(flights)} 个航班:")
    for flight in flights[:5]:  # 显示前5个
        print(f"  - {flight.flight_id}: {flight.scheduled_time.strftime('%H:%M:%S')}")
    if len(flights) > 5:
        print(f"  ... 还有 {len(flights) - 5} 个航班")

    # 创建密度分析器
    analyzer = DensityAnalyzer(time_window_minutes=30, peak_threshold=0.6)

    # 分析密度
    analysis = analyzer.analyze_density(flights)

    print(f"\n密度分析结果:")
    print(f"  时间范围: {analysis['time_range']['start'].strftime('%H:%M')} - {analysis['time_range']['end'].strftime('%H:%M')}")
    print(f"  总航班数: {analysis['flight_count']}")
    print(f"  平均密度: {analysis['average_density']:.2f} 航班/小时")
    print(f"  高峰期窗口数: {len(analysis['peak_windows'])}")
    print(f"  低峰期窗口数: {len(analysis['off_peak_windows'])}")
    print(f"  正常期窗口数: {len(analysis['normal_windows'])}")

    # 获取当前时间点的权重
    current_time = flights[0].scheduled_time  # 使用第一个航班的时间作为示例
    weight_info = analyzer.get_current_weights(flights, current_time)

    print(f"\n当前时间点权重配置 ({current_time.strftime('%H:%M:%S')}):")
    print(f"  时间段类型: {weight_info['period_type']}")
    print(f"  描述: {weight_info['description']}")
    print(f"  距离权重: {weight_info['weights']['distance']:.1f}")
    print(f"  时间权重: {weight_info['weights']['time']:.1f}")
    print(f"  燃料权重: {weight_info['weights']['fuel']:.1f}")

    # 演示不同时间点的权重变化
    print(f"\n不同时间点的权重变化示例:")
    test_times = [
        current_time,
        current_time + timedelta(hours=1),
        current_time + timedelta(hours=3),
        current_time + timedelta(hours=6)
    ]

    for test_time in test_times:
        weight_info = analyzer.get_current_weights(flights, test_time)
        print(f"  {test_time.strftime('%H:%M:%S')}: {weight_info['period_type']} - "
              f"时间权重={weight_info['weights']['time']:.1f}, "
              f"燃料权重={weight_info['weights']['fuel']:.1f}")


if __name__ == "__main__":
    demo_density_analysis()