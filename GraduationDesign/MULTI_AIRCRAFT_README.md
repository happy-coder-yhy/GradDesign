# 多航班滑行路径优化与冲突调度系统

## 系统概述

基于参考文献（桃园机场TPE应用案例）开发的多航班滑行路径优化与冲突调度系统，实现了：
- 多航班时空冲突检测
- FCFS（先来先服务）调度策略
- 优先级调度策略
- 时间窗调度策略
- 2D路径可视化与动画
- 甘特图展示
- 冲突点标注

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│          多航班滑行路径优化与冲突调度系统                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  前端 (Vue 3)                                           │
│  ┌───────────────────────────────────────┐             │
│  │   MultiAircraftScheduling.vue         │             │
│  │   - 控制面板                           │             │
│  │   - 航班列表                           │             │
│  │   - 2D路径可视化                       │             │
│  │   - 冲突列表                           │             │
│  │   - 甘特图                             │             │
│  │   - 动画控制                           │             │
│  └───────────────┬───────────────────────┘             │
│                  │ HTTP API                              │
└──────────────────┼─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  后端 (Flask)                                           │
│  ┌───────────────────────────────────────┐             │
│  │   API 服务                             │             │
│  │   - /api/multi-aircraft/generate      │             │
│  │   - /api/multi-aircraft/schedule      │             │
│  └───────────────┬───────────────────────┘             │
│                  │                                        │
│  ┌───────────────┴───────────────────────┐             │
│  │   MultiAircraftScheduler              │             │
│  │   - 冲突检测器                         │             │
│  │   - 调度器                             │             │
│  │   - 路径规划                           │             │
│  └───────────────┬───────────────────────┘             │
│                  │                                        │
│  ┌───────────────┴───────────────────────┐             │
│  │   AirportGraph + A*算法               │             │
│  └───────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

## 文件结构

```
GraduationDesign/
├── Algorithm/
│   ├── Astar.py                      # A*算法实现
│   └── MultiAircraftScheduler.py     # 多航班调度器 ⭐新增
├── 西安机场/                          # 机场数据
├── api.py                            # API服务 ⭐扩展
├── test_multi_aircraft.py            # 测试脚本 ⭐新增
└── 参考文献/                          # 参考论文

my-vue-app/src/
├── components/
│   └── MultiAircraftScheduling.vue   # 多航班调度页面 ⭐新增
└── router/
    └── index.js                      # 路由配置 ⭐更新
```

## 快速开始

### 1. 启动后端API服务

```bash
cd /Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign
python api.py
```

服务将在 `http://localhost:5001` 启动。

### 2. 启动前端开发服务器

```bash
cd /Users/xupeihong/Desktop/毕业设计/demo/my-vue-app
npm install  # 首次运行需要安装依赖
npm run serve
```

前端将在 `http://localhost:8080` 启动。

### 3. 访问多航班调度页面

在浏览器中打开：`http://localhost:8080/multi-aircraft`

## API 接口文档

### 1. 生成模拟航班数据

**接口**: `POST /api/multi-aircraft/generate-simulation`

**请求参数**:
```json
{
  "num_flights": 6,
  "base_time": "2024-01-20 14:00:00"
}
```

**响应示例**:
```json
{
  "success": true,
  "num_flights": 6,
  "flights": [
    {
      "flight_id": "FL1000",
      "aircraft_type": "A320",
      "operation": "departure",
      "start_node_id": 1,
      "end_node_id": 100,
      "scheduled_time": "2024-01-20 14:00:00",
      "priority": "medium",
      "speed": 15.0
    }
  ]
}
```

### 2. 多航班调度

**接口**: `POST /api/multi-aircraft/schedule`

**请求参数**:
```json
{
  "strategy": "fcfs",
  "flights": [...]
}
```

**策略类型**:
- `fcfs`: 先来先服务
- `priority`: 优先级调度
- `time_window`: 时间窗调度

**响应示例**:
```json
{
  "success": true,
  "strategy": "fcfs",
  "flight_count": 6,
  "total_distance": 25000.5,
  "total_time": 1800.0,
  "total_delay": 60.0,
  "total_conflicts": 2,
  "schedules": [
    {
      "flight_id": "FL1000",
      "path": [...],
      "waypoints": [...],
      "total_distance": 4200.5,
      "total_time": 280.0,
      "delay": 0.0,
      "conflicts": []
    }
  ]
}
```

## 功能说明

### 1. 航班数据生成
- 支持自定义航班数量
- 自动生成起点、终点、时间、优先级
- 随机生成离港/进港航班

### 2. 调度策略

**FCFS (First-Come-First-Serve)**
- 按照计划时间排序
- 优先调度早到航班
- 适用于正常运营场景

**优先级调度**
- 高优先级航班优先
- 优先级相同时按时间排序
- 适用于重要航班保障

**时间窗调度**
- 离港航班优先
- 动态调整起飞时间
- 适用于高峰时段

### 3. 冲突检测

**节点冲突**
- 多架飞机同时到达同一节点
- 时间间隔 < 30秒视为冲突

**边冲突**
- 两架飞机在同一路段相向或同向
- 距离过近视为冲突

**交叉冲突**
- 路径在交叉口相交
- 时间重叠视为冲突

### 4. 可视化功能

**2D路径可视化**
- Canvas绘制机场路网
- 不同颜色区分不同航班
- 虚线显示规划路径
- 实心点标注起点、终点

**冲突点标注**
- 红色圆圈标注冲突位置
- 不同严重程度用颜色区分
- 点击查看冲突详情

**路径动画**
- 播放/暂停控制
- 速度调节（1x-10x）
- 实时显示飞机位置
- 时间轴同步

**甘特图**
- X轴：时间
- Y轴：航班
- 条形：滑行时间占用
- 红色：延误时间

## 测试

运行测试脚本：

```bash
cd /Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign
python test_multi_aircraft.py
```

测试内容：
1. 生成模拟航班数据
2. FCFS策略调度
3. 优先级策略调度
4. 统计信息输出

## 核心算法

### 冲突检测算法

```python
class ConflictDetector:
    def detect_all_conflicts(self, schedules):
        """检测所有航班之间的冲突"""
        # 1. 检测节点冲突
        # 2. 检测路径交叉冲突
        # 返回冲突列表
```

### 调度算法

```python
class MultiAircraftScheduler:
    def schedule_multiple_flights(self, flights):
        """为多个航班调度路径"""
        # 1. 对航班排序（根据策略）
        # 2. 依次为每个航班规划路径
        # 3. 检测冲突
        # 4. 冲突消解（延迟后到航班）
        # 返回调度方案
```

### A*路径规划

```python
def find_path(self, flight, existing_schedules):
    """为单个航班规划路径"""
    # 1. 使用A*算法找最短路径
    # 2. 计算时间节点
    # 3. 检查时空占用
    # 返回路径和时间点
```

## 评估指标

| 指标 | 说明 | 优化目标 |
|-----|------|---------|
| 总延误时间 | 所有航班延误总和 | 最小化 |
| 最大延误 | 单个航班最大延误 | < 5分钟 |
| 冲突数量 | 检测到的冲突点 | 0 |
| 路径长度 | 实际路径vs最优路径 | 迂回系数 < 1.3 |
| 计算时间 | 算法运行时间 | < 10秒 |

## 参考文献

1. **Wang et al. (2023)** - Enhancing Airside Operation Efficiency through Trajectory Optimization by Computer Software
   - 桃园机场TPE应用案例
   - FCFS调度策略
   - Excel工具实现

2. **王欢** - 大型机场航空器动态滑行调度研究
   - 多目标优化模型
   - 冲突消解策略

3. **Weiszer et al. (2015)** - 机场滑行路径多目标优化
   - 距离、时间、燃料消耗
   - 帕累托最优

## 未来优化方向

1. **算法优化**
   - 集成遗传算法自动调度
   - 深度强化学习动态决策
   - 多目标帕累托优化

2. **功能扩展**
   - 实时航班数据接入
   - 天气影响建模
   - 燃料消耗精确计算
   - 噪音污染评估

3. **可视化增强**
   - 3D机场场景渲染
   - 交互式路径编辑
   - 实时数据更新
   - 历史回放功能

## 作者

毕业设计项目 - 机场场面滑行轨迹优化系统

## 版本历史

- **v2.0** (2026-01) - 多航班调度系统
  - 新增多航班冲突检测
  - 实现多种调度策略
  - 添加2D可视化和动画
  - 添加甘特图展示

- **v1.0** (2025-12) - 单机A*算法
  - 基础A*路径规划
  - 单机最优路径
  - 基本可视化
