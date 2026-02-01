# A*算法可视化使用说明

## 项目结构

本项目包含前端（Vue）和后端（Python Flask）两部分：

- **前端**: `/my-vue-app` - Vue.js应用，负责可视化展示
- **后端**: `/GraduationDesign` - Python Flask API，提供A*算法服务

## 启动步骤

### 1. 启动后端API服务

在终端中运行：

```bash
cd /Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign
./start_api.sh
```

或者直接运行：

```bash
cd /Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign
.venv/bin/python api.py
```

看到以下输出表示启动成功：

```
==========================================
机场场面滑行轨迹优化 - A*算法API服务
==========================================

服务地址: http://localhost:5001
API文档: http://localhost:5001/

正在加载路网数据...
...
系统初始化完成！
```

**重要**: 后端服务必须保持运行状态！

### 2. 启动前端Vue应用

在另一个终端中运行：

```bash
cd /Users/xupeihong/Desktop/毕业设计/demo/my-vue-app
npm run serve
```

看到以下输出表示启动成功：

```
App running at:
- Local:   http://localhost:8080/
- Network: http://192.168.x.x:8080/
```

### 3. 访问应用

在浏览器中打开: http://localhost:8888/

点击"A*算法"按钮进入可视化页面。

## 使用功能

### 可视化页面功能

1. **加载路网数据**
   - 点击"加载路网数据"按钮
   - 后端会从西安机场SHP文件加载路网数据
   - Canvas会显示所有节点（机位、跑道、路网点）

2. **演示1: 最远机位路径**
   - 自动找到距离最远的两个机位
   - 计算它们之间的最优路径
   - 显示路径统计信息（距离、时间、燃料消耗）

3. **演示2: 机位到跑道**
   - 找到距离最远的机位和跑道点
   - 计算最优滑行路径
   - 显示详细的路径规划结果

### 图例说明

- 🟢 **绿色点**: 机位 (StandPoint)
- 🟠 **橙色点**: 跑道点 (RunwayPoint)
- 🟣 **紫色点**: 路网点 (NetworkPoint)
- 🔵 **蓝色点**: 其他线路节点
- ➖ **绿色线**: A*算法计算出的最优路径
- 📍 **起/终**: 标记路径的起点和终点

## API接口文档

后端提供以下REST API接口：

### 健康检查
```
GET /api/health
```

### 获取所有节点
```
GET /api/nodes
```

### 根据类型获取节点
```
GET /api/nodes/by-type/<node_type>
```
参数: `StandPoint`, `RunwayPoint`, `NetworkPoint` 等

### 计算路径
```
POST /api/path
```
请求体:
```json
{
  "start_node_id": 1,
  "goal_node_id": 100,
  "weights": {
    "distance": 1.0,
    "time": 1.0,
    "fuel": 0.5
  },
  "speed": 15.0
}
```

### 演示接口
```
GET /api/demo/farthest-stand      # 获取最远机位对
GET /api/demo/stand-to-runway     # 获取机位到跑道
```

## 技术栈

- **后端**:
  - Python 3.12
  - Flask - Web框架
  - Flask-CORS - 跨域支持
  - GeoPandas - 地理数据处理
  - Shapely - 几何计算

- **前端**:
  - Vue.js 3
  - Axios - HTTP客户端
  - Canvas API - 地图可视化

## 数据说明

项目使用的西安机场数据存储在:
```
/Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign/西安机场/
```

包含以下SHP文件：
- 机位点.shp
- 跑道点 (runwaypoints.shp)
- 路网点 (standpoints.shp)
- 线路数据 (network.shp, 航空器道路.shp等)

## 注意事项

1. **后端必须先启动**: 前端需要调用后端API，所以必须先启动Flask服务
2. **端口占用**: 确保端口5000（后端）和8080（前端）未被占用
3. **数据加载**: 首次加载路网数据可能需要几秒钟
4. **跨域问题**: 已通过Flask-CORS解决，如果仍有问题请检查防火墙设置

## 故障排查

### 前端无法连接后端

1. 检查后端是否正常运行
2. 检查浏览器控制台是否有错误
3. 确认后端地址为 http://localhost:5000

### 数据加载失败

1. 检查西安机场数据文件夹路径是否正确
2. 确认所有SHP文件存在
3. 查看后端终端输出的错误信息

### 路径计算失败

1. 可能是起点和终点之间没有可达路径
2. 尝试其他的演示选项
3. 查看后端日志了解详细错误

## 作者

毕业设计项目 - 机场场面滑行轨迹优化系统
