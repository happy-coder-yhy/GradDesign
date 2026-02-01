# GraduationDesign - 机场场面滑行轨迹优化系统

## 项目结构

```
GraduationDesign/
├── Algorithm/           # 算法模块
│   ├── __init__.py
│   └── Astar.py        # A*算法实现
│
├── Neo4j/              # Neo4j数据库模块
│   ├── __init__.py
│   ├── main.py         # Neo4j数据导入脚本
│   ├── check_db.py     # 检查数据库节点类型
│   ├── check_edges.py  # 检查边的连接情况
│   ├── check_connectivity.py  # 检查节点连通性
│   ├── check_network_coords.py  # 检查网络坐标
│   └── debug_path.py   # 调试路径查找
│
├── api.py              # Flask API服务（主入口）
├── test_api.py         # API测试脚本
├── check_crs.py        # 检查坐标系统
├── requirements.txt    # Python依赖
├── .env.example        # 环境变量示例
├── start_api.sh        # API启动脚本
├── API_README.md       # API文档
│
├── 西安机场/            # GIS数据目录
├── 参考文献/           # 参考文献资料
└── .venv/             # Python虚拟环境
```

## 模块说明

### Algorithm模块
包含路径规划算法的实现，主要是基于A*算法的路径优化器。

**主要类：**
- `AirportGraph`: 机场路网图类，从SHP文件加载和管理路网数据
- `AStarOptimizer`: A*算法优化器，用于机场场面滑行路径规划

**使用示例：**
```python
from Algorithm.Astar import AirportGraph, AStarOptimizer

# 创建路网图
graph = AirportGraph("/path/to/西安机场")
graph.load_data()

# 创建优化器
optimizer = AStarOptimizer(graph)
```

### Neo4j模块
包含Neo4j图数据库的连接、数据导入和查询功能。

**主要脚本：**
- `main.py`: 将SHP文件数据导入到Neo4j数据库
- `check_*.py`: 各种数据库检查和调试脚本

**使用示例：**
```bash
# 导入数据到Neo4j
cd Neo4j
python main.py
```

### API服务
提供HTTP接口的Flask应用，用于前端调用路径规划功能。

**启动API服务：**
```bash
# 方式1：使用启动脚本
bash start_api.sh

# 方式2：直接运行
python api.py
```

**访问地址：**
- API服务: http://localhost:5001
- API文档: http://localhost:5001/

## 依赖安装

```bash
pip install -r requirements.txt
```

## 环境配置

复制 `.env.example` 到 `.env` 并配置相关参数：

```bash
cp .env.example .env
```

## 开发说明

### 添加新的算法
1. 在 `Algorithm/` 目录下创建新的算法文件
2. 在 `Algorithm/__init__.py` 中导出新的类或函数

### 添加新的Neo4j操作
1. 在 `Neo4j/` 目录下创建新的脚本文件
2. 使用现有的 `Neo4jConnection` 类或创建新的连接类

## 整理说明

本次整理将项目按照功能模块进行了重组：
- **Algorithm目录**: 存放所有算法相关的代码
- **Neo4j目录**: 存放所有Neo4j数据库操作相关的代码
- **根目录**: 保留API主入口、测试脚本和配置文件

这样的结构使得项目更加清晰，便于维护和扩展。
