<template>
  <div class="network-visualization">
    <div class="demo-controls">
      <button @click="$emit('loadData')" :disabled="isLoading" class="demo-btn">
        {{ isLoading ? '加载中...' : '加载路网数据' }}
      </button>
      <button @click="$emit('runDemo1')" :disabled="isLoading || !nodesLoaded" class="demo-btn">
        {{ demo1ButtonName }}
      </button>
      <button @click="$emit('runDemo2')" :disabled="isLoading || !nodesLoaded" class="demo-btn">
        {{ demo2ButtonName }}
      </button>
      <button @click="toggleDisplay" :disabled="!nodesLoaded" class="demo-btn toggle-btn">
        {{ showCoreNodesOnly ? toggleButtonText.showMore : toggleButtonText.showOnly }}
      </button>
    </div>

    <!-- 节点选择区域 -->
    <div v-if="nodesLoaded" class="node-selection-controls">
      <div class="selection-group">
        <label class="selection-label">🟢 选择起点:</label>
        <el-select
          v-model="selectedStartNodeId"
          @change="handleStartNodeChange"
          filterable
          placeholder="请输入节点ID搜索"
          class="node-select-el"
          clearable
        >
          <el-option-group v-if="standPoints.length > 0" label="机位点">
            <el-option
              v-for="node in standPoints"
              :key="'start-' + node.id"
              :label="`机位点 #${node.id}`"
              :value="node.id"
            />
          </el-option-group>
          <el-option-group v-if="runwayPoints.length > 0" label="跑道点">
            <el-option
              v-for="node in runwayPoints"
              :key="'start-' + node.id"
              :label="`跑道点 #${node.id}`"
              :value="node.id"
            />
          </el-option-group>
        </el-select>
      </div>

      <div class="selection-group">
        <label class="selection-label">🟠 选择终点:</label>
        <el-select
          v-model="selectedGoalNodeId"
          @change="handleGoalNodeChange"
          filterable
          placeholder="请输入节点ID搜索"
          class="node-select-el"
          clearable
        >
          <el-option-group v-if="standPoints.length > 0" label="机位点">
            <el-option
              v-for="node in standPoints"
              :key="'goal-' + node.id"
              :label="`机位点 #${node.id}`"
              :value="node.id"
            />
          </el-option-group>
          <el-option-group v-if="runwayPoints.length > 0" label="跑道点">
            <el-option
              v-for="node in runwayPoints"
              :key="'goal-' + node.id"
              :label="`跑道点 #${node.id}`"
              :value="node.id"
            />
          </el-option-group>
        </el-select>
      </div>

      <button @click="$emit('runCustomPath', selectedStartNode, selectedGoalNode)"
              :disabled="!selectedStartNode || !selectedGoalNode || isLoading"
              class="demo-btn custom-path-btn">
        {{ isLoading ? '计算中...' : '🚀 计算自定义路径' }}
      </button>

      <button @click="clearSelection" :disabled="!selectedStartNode && !selectedGoalNode" class="demo-btn clear-btn">
        清除选择
      </button>
    </div>

    <div v-if="error" class="info error">
      ❌ {{ error }}
    </div>

    <div v-if="nodesLoaded" class="info success">
      ✅ 已加载路网数据（{{ nodeCounts.stands }}个机位 + {{ edges.length }}条道路）
    </div>

    <div class="canvas-container">
      <canvas
        ref="networkCanvas"
        width="1200"
        height="800"
        @wheel="handleWheel"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        @mouseleave="handleMouseUp"
      ></canvas>
      <div class="canvas-controls">
        <button @click="zoomIn" class="zoom-btn">放大 +</button>
        <button @click="zoomOut" class="zoom-btn">缩小 -</button>
        <button @click="resetView" class="zoom-btn">重置</button>
        <span class="zoom-level">缩放: {{ (zoomLevel * 100).toFixed(0) }}%</span>
      </div>
    </div>

    <div v-if="pathStats" class="path-stats">
      <h4>路径统计信息</h4>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-label">路径长度:</span>
          <span class="stat-value">{{ (pathStats.total_distance / 1000).toFixed(2) }} km</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">预计时间:</span>
          <span class="stat-value">{{ (pathStats.total_time / 60).toFixed(2) }} 分钟</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">燃料消耗:</span>
          <span class="stat-value">{{ pathStats.fuel_consumption.toFixed(2) }} 单位</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">路径节点数:</span>
          <span class="stat-value">{{ pathStats.num_nodes }}</span>
        </div>
      </div>
    </div>

    <div class="legend">
      <div class="legend-section">
        <h4>📍 节点</h4>
        <span class="legend-item"><span class="legend-box standpoint-box"></span>机位 ({{ nodeCounts.stands }}个)</span>
        <span class="legend-item"><span class="legend-box runway-box"></span>跑道点 ({{ nodeCounts.runways }}个)</span>
        <span class="legend-item"><span class="legend-box observation-box"></span>观察点 ({{ nodeCounts.observations }}个)</span>
      </div>
      <div class="legend-section">
        <h4>🛣️ 道路连接</h4>
        <span class="legend-item"><span class="legend-line aircraftroad-line"></span>滑行道 ({{ edgeCounts.aircraftRoad }}条)</span>
        <span class="legend-item"><span class="legend-line networkroad-line"></span>路网道路 ({{ edgeCounts.networkRoad }}条)</span>
        <span class="legend-item"><span class="legend-line externalroad-line"></span>场外道路 ({{ edgeCounts.externalRoad }}条)</span>
        <span class="legend-item"><span class="legend-line servicevehicle-line"></span>保障车辆道路 ({{ edgeCounts.serviceVehicle }}条)</span>
        <span class="legend-item"><span class="legend-line perimeterroad-line"></span>围场路 ({{ edgeCounts.perimeterRoad }}条)</span>
      </div>
      <div class="legend-section">
        <h4>🎯 算法结果</h4>
        <span class="legend-item"><span class="legend-line path-line"></span>{{ resultPathName }}（绿色）</span>
      </div>
      <div class="legend-section hint-section">
        <span class="legend-item hint-text">💡 {{ hint }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NetworkVisualization',
  props: {
    demo1ButtonName: {
      type: String,
      default: '演示1: 最远机位路径'
    },
    demo2ButtonName: {
      type: String,
      default: '演示2: 机位到跑道'
    },
    toggleButtonText: {
      type: Object,
      default: () => ({ showMore: '显示跑道点和观察点', showOnly: '只显示机位' })
    },
    hint: {
      type: String,
      default: '💡 点击"显示跑道点和观察点"查看更多节点'
    },
    resultPathName: {
      type: String,
      default: 'A*优化路径'
    }
  },
  data() {
    return {
      nodes: [],
      edges: [],
      currentPath: null,
      nodesLoaded: false,
      isLoading: false,
      error: null,
      pathStats: null,
      canvas: null,
      ctx: null,
      transform: null,
      zoomLevel: 1.0,
      panOffset: { x: 0, y: 0 },
      isDragging: false,
      lastMousePos: { x: 0, y: 0 },
      baseScale: 1.0,
      baseOffsetX: 0,
      baseOffsetY: 0,
      showCoreNodesOnly: true, // 默认只显示机位
      selectedStartNodeId: null, // 选中的起点ID
      selectedGoalNodeId: null, // 选中的终点ID
      selectedStartNode: null, // 选中的起点对象
      selectedGoalNode: null // 选中的终点对象
    }
  },
  computed: {
    nodeCounts() {
      const counts = {
        stands: 0,
        runways: 0,
        observations: 0
      };
      this.nodes.forEach(node => {
        if (node.type.includes('Stand')) counts.stands++;
        else if (node.type.includes('Runway')) counts.runways++;
        else if (node.type.includes('Observation')) counts.observations++;
      });
      return counts;
    },
    edgeCounts() {
      const counts = {
        aircraftRoad: 0,
        networkRoad: 0,
        externalRoad: 0,
        serviceVehicle: 0,
        perimeterRoad: 0
      };
      this.edges.forEach(edge => {
        if (counts[edge.type] !== undefined) {
          counts[edge.type]++;
        }
      });
      return counts;
    },
    standPoints() {
      return this.nodes.filter(node => node.type.includes('Stand')).sort((a, b) => a.id - b.id);
    },
    runwayPoints() {
      return this.nodes.filter(node => node.type.includes('Runway')).sort((a, b) => a.id - b.id);
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initCanvas();
    });
  },
  methods: {
    initCanvas() {
      console.log('Initializing canvas...');
      this.canvas = this.$refs.networkCanvas;
      console.log('Canvas element:', this.canvas);

      if (this.canvas) {
        this.ctx = this.canvas.getContext('2d');
        console.log('Canvas context:', this.ctx);
        console.log('Canvas size:', this.canvas.width, 'x', this.canvas.height);

        // 绘制一个测试背景
        this.ctx.fillStyle = '#0a1428';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.fillStyle = '#4facfe';
        this.ctx.font = '20px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Canvas已就绪，请加载路网数据', this.canvas.width / 2, this.canvas.height / 2);
      } else {
        console.error('Canvas element not found!');
      }
    },

    setNodes(nodes) {
      this.nodes = nodes;
      this.nodesLoaded = true;
      this.$nextTick(() => {
        this.initCanvas();
        this.drawNetwork();
      });
    },

    setEdges(edges) {
      this.edges = edges;
    },

    setLoading(loading) {
      this.isLoading = loading;
    },

    setError(error) {
      this.error = error;
    },

    setPath(path, stats) {
      this.currentPath = path;
      this.pathStats = stats;
      this.isLoading = false; // 重置loading状态
      if (path && stats) {
        this.$nextTick(() => {
          this.drawNetwork();
          this.drawPath();
          this.drawSelectedNodes(); // 确保选中的节点也显示
        });
      }
    },

    resetPath() {
      this.currentPath = null;
      this.pathStats = null;
      this.drawNetwork();
    },

    drawNetwork() {
      console.log('drawNetwork called');
      console.log('ctx:', this.ctx);
      console.log('canvas:', this.canvas);
      console.log('nodes:', this.nodes.length);

      if (!this.ctx) {
        console.error('Canvas context not initialized!');
        return;
      }

      if (!this.nodes.length) {
        console.error('No nodes to draw!');
        return;
      }

      const canvas = this.canvas;
      const ctx = this.ctx;

      console.log('Canvas dimensions:', canvas.width, 'x', canvas.height);

      // 清空画布
      ctx.fillStyle = '#0a1428';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 计算坐标范围
      const xCoords = this.nodes.map(n => n.x);
      const yCoords = this.nodes.map(n => n.y);
      const minX = Math.min(...xCoords);
      const maxX = Math.max(...xCoords);
      const minY = Math.min(...yCoords);
      const maxY = Math.max(...yCoords);

      console.log('Coordinate range:');
      console.log('  X:', minX, 'to', maxX, 'width:', maxX - minX);
      console.log('  Y:', minY, 'to', maxY, 'height:', maxY - minY);

      // 基础缩放和偏移
      const padding = 50;
      const scaleX = (canvas.width - 2 * padding) / (maxX - minX);
      const scaleY = (canvas.height - 2 * padding) / (maxY - minY);
      this.baseScale = Math.min(scaleX, scaleY);

      this.baseOffsetX = padding + (canvas.width - 2 * padding - (maxX - minX) * this.baseScale) / 2 - minX * this.baseScale;
      this.baseOffsetY = padding + (canvas.height - 2 * padding - (maxY - minY) * this.baseScale) / 2 - minY * this.baseScale;

      console.log('Base scale:', this.baseScale);
      console.log('Base offset:', this.baseOffsetX, this.baseOffsetY);

      // 保存转换函数（应用缩放和平移）
      this.transform = (x, y) => {
        const scaledX = x * this.baseScale + this.baseOffsetX;
        const scaledY = canvas.height - (y * this.baseScale + this.baseOffsetY);

        // 应用用户缩放和平移
        return {
          x: (scaledX - canvas.width / 2) * this.zoomLevel + this.panOffset.x + canvas.width / 2,
          y: (scaledY - canvas.height / 2) * this.zoomLevel + this.panOffset.y + canvas.height / 2
        };
      };

      // 绘制边
      console.log('Drawing edges...');
      let edgeCount = 0;

      const edgeStyles = {
        'AircraftRoad': { color: 'rgba(79, 172, 254, 0.4)', width: 2 },
        'NetworkRoad': { color: 'rgba(156, 39, 176, 0.3)', width: 1.5 },
        'ServiceVehicleRoad': { color: 'rgba(255, 193, 7, 0.2)', width: 1 },
        'PerimeterRoad': { color: 'rgba(96, 125, 139, 0.3)', width: 1 },
        'ExternalRoad': { color: 'rgba(255, 87, 34, 0.25)', width: 1.2 },
        'PROXIMITY': { color: 'rgba(76, 175, 80, 0.15)', width: 1 }
      };

      const edgeTypeCount = {};

      const drawnEdges = new Set();

      this.edges.forEach(edge => {
        const edgeKey = `${Math.min(edge.from_node_id, edge.to_node_id)}-${Math.max(edge.from_node_id, edge.to_node_id)}`;
        if (drawnEdges.has(edgeKey)) return;
        drawnEdges.add(edgeKey);

        const startPos = this.transform(edge.from_x, edge.from_y);
        const endPos = this.transform(edge.to_x, edge.to_y);

        const style = edgeStyles[edge.type] || { color: 'rgba(255, 255, 255, 0.1)', width: 1 };

        ctx.beginPath();
        ctx.moveTo(startPos.x, startPos.y);
        ctx.lineTo(endPos.x, endPos.y);
        ctx.strokeStyle = style.color;
        ctx.lineWidth = style.width * Math.max(0.5, Math.min(1.5, this.zoomLevel));
        ctx.stroke();

        edgeCount++;
        edgeTypeCount[edge.type] = (edgeTypeCount[edge.type] || 0) + 1;
      });

      console.log('Drew', edgeCount, 'edges');
      console.log('Edge types:', edgeTypeCount);

      // 绘制节点
      let drawnCount = 0;
      this.nodes.forEach(node => {
        // 根据显示模式决定绘制哪些节点
        let shouldDraw = false;

        if (this.showCoreNodesOnly) {
          // 只显示机位
          shouldDraw = node.type.includes('Stand');
        } else {
          // 显示核心节点：机位、跑道点、观察点
          shouldDraw = node.type.includes('Stand') ||
                      node.type.includes('Runway') ||
                      node.type.includes('Observation');
        }

        if (!shouldDraw) {
          return;
        }

        const pos = this.transform(node.x, node.y);

        let color = '#2196f3';
        let size = 3;

        if (node.type.includes('Stand')) {
          color = '#00bcd4';
          size = 1.5;
        } else if (node.type.includes('Runway')) {
          color = '#ff9800';
          size = 1.5;
        } else if (node.type.includes('Observation')) {
          color = '#9c27b0';
          size = 1.5;
        }

        const adjustedSize = size * Math.max(0.5, Math.min(2, this.zoomLevel));

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, adjustedSize, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
        drawnCount++;
      });

      const mode = this.showCoreNodesOnly ? '只显示机位' : '显示机位+跑道点+观察点';
      console.log('Drew', drawnCount, `nodes (${mode})`);

      // 绘制标题
      ctx.fillStyle = '#4facfe';
      ctx.font = '16px Arial';
      ctx.textAlign = 'center';
      const titleMode = this.showCoreNodesOnly ? '(只显示机位)' : '(机位+跑道点+观察点)';
      ctx.fillText(`西安机场路网 ${titleMode}`, canvas.width / 2, 25);

      // 如果有选中的节点，绘制它们
      if (this.selectedStartNode || this.selectedGoalNode) {
        this.drawSelectedNodes();
      }

      console.log('drawNetwork completed');
    },

    drawPath() {
      console.log('drawPath called');
      console.log('currentPath length:', this.currentPath?.length);

      if (!this.ctx) {
        console.error('Canvas context not initialized!');
        return;
      }

      if (!this.currentPath || !this.currentPath.length) {
        console.error('No path to draw!');
        return;
      }

      if (!this.transform) {
        console.error('Transform function not defined!');
        return;
      }

      const ctx = this.ctx;
      console.log('Drawing path with', this.currentPath.length, 'nodes');

      // 绘制路径
      ctx.beginPath();
      ctx.strokeStyle = '#4caf50';
      ctx.lineWidth = 3;
      ctx.shadowColor = '#4caf50';
      ctx.shadowBlur = 10;

      this.currentPath.forEach((node, index) => {
        const pos = this.transform(node.x, node.y);

        if (index === 0) {
          ctx.moveTo(pos.x, pos.y);
        } else {
          ctx.lineTo(pos.x, pos.y);
        }
      });

      ctx.stroke();
      ctx.shadowBlur = 0;
      console.log('Path stroke completed');

      // 绘制起点
      const startPos = this.transform(this.currentPath[0].x, this.currentPath[0].y);
      ctx.beginPath();
      ctx.arc(startPos.x, startPos.y, 6, 0, 2 * Math.PI);
      ctx.fillStyle = '#4caf50';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 10px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('起', startPos.x, startPos.y + 3.5);

      // 绘制终点
      const endPos = this.transform(this.currentPath[this.currentPath.length - 1].x, this.currentPath[this.currentPath.length - 1].y);
      ctx.beginPath();
      ctx.arc(endPos.x, endPos.y, 6, 0, 2 * Math.PI);
      ctx.fillStyle = '#ff9800';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 10px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('终', endPos.x, endPos.y + 3.5);

      // 绘制选中的节点（确保显示在路径之上）
      this.drawSelectedNodes();

      console.log('drawPath completed');
    },

    // 缩放功能
    handleWheel(event) {
      event.preventDefault();

      const delta = event.deltaY > 0 ? 0.9 : 1.1;
      const newZoom = this.zoomLevel * delta;

      if (newZoom >= 0.1 && newZoom <= 10) {
        this.zoomLevel = newZoom;
        this.drawNetwork();
        if (this.currentPath) {
          this.drawPath();
        }
      }
    },

    zoomIn() {
      if (this.zoomLevel < 10) {
        this.zoomLevel *= 1.2;
        this.drawNetwork();
        if (this.currentPath) {
          this.drawPath();
        }
      }
    },

    zoomOut() {
      if (this.zoomLevel > 0.1) {
        this.zoomLevel /= 1.2;
        this.drawNetwork();
        if (this.currentPath) {
          this.drawPath();
        }
      }
    },

    resetView() {
      this.zoomLevel = 1.0;
      this.panOffset = { x: 0, y: 0 };
      this.drawNetwork();
      if (this.currentPath) {
        this.drawPath();
      }
    },

    // 拖拽功能
    handleMouseDown(event) {
      this.isDragging = true;
      this.lastMousePos = {
        x: event.clientX,
        y: event.clientY
      };
      this.canvas.style.cursor = 'grabbing';
    },

    handleMouseMove(event) {
      if (!this.isDragging) return;

      this.panOffset.x += event.clientX - this.lastMousePos.x;
      this.panOffset.y += event.clientY - this.lastMousePos.y;

      this.lastMousePos = {
        x: event.clientX,
        y: event.clientY
      };

      this.drawNetwork();
      if (this.currentPath) {
        this.drawPath();
      }
    },

    handleMouseUp() {
      this.isDragging = false;
      this.canvas.style.cursor = 'grab';
    },

    toggleDisplay() {
      this.showCoreNodesOnly = !this.showCoreNodesOnly;
      console.log('Toggle display:', this.showCoreNodesOnly ? '只显示机位' : '显示机位+跑道点+观察点');
      this.drawNetwork();
      if (this.currentPath) {
        this.drawPath();
      }
      this.$emit('displayToggled', this.showCoreNodesOnly);
    },

    // 处理起点选择变化
    handleStartNodeChange() {
      this.selectedStartNode = this.nodes.find(n => n.id === parseInt(this.selectedStartNodeId)) || null;
      this.selectedGoalNode = null;
      this.selectedGoalNodeId = null;
      this.currentPath = null;
      this.pathStats = null;
      this.drawNetwork();
    },

    // 处理终点选择变化
    handleGoalNodeChange() {
      this.selectedGoalNode = this.nodes.find(n => n.id === parseInt(this.selectedGoalNodeId)) || null;
      this.drawNetwork();
    },

    // 绘制选中的节点
    drawSelectedNodes() {
      if (!this.ctx || !this.transform) return;

      const ctx = this.ctx;

      // 绘制起点
      if (this.selectedStartNode) {
        const pos = this.transform(this.selectedStartNode.x, this.selectedStartNode.y);

        // 外圈
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 10, 0, 2 * Math.PI);
        ctx.fillStyle = '#4caf50';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 3;
        ctx.stroke();

        // 文字
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('起', pos.x, pos.y + 4);
      }

      // 绘制终点
      if (this.selectedGoalNode) {
        const pos = this.transform(this.selectedGoalNode.x, this.selectedGoalNode.y);

        // 外圈
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 10, 0, 2 * Math.PI);
        ctx.fillStyle = '#ff9800';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 3;
        ctx.stroke();

        // 文字
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('终', pos.x, pos.y + 4);
      }
    },

    // 清除选中
    clearSelection() {
      this.selectedStartNode = null;
      this.selectedGoalNode = null;
      this.drawNetwork();
    }
  }
}
</script>

<style scoped>
.network-visualization {
  width: 100%;
}

.demo-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 1rem;
  justify-content: center;
}

.node-selection-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  padding: 1rem 1.2rem;
  background: rgba(20, 30, 60, 0.6);
  border-radius: 8px;
  border: 1px solid rgba(64, 224, 255, 0.3);
  margin-bottom: 1.5rem;
  justify-content: center;
}

.selection-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.selection-label {
  color: #4facfe;
  font-weight: bold;
  font-size: 0.9rem;
  white-space: nowrap;
}

/* Element Plus Select 自定义样式 */
.node-select-el {
  width: 200px;
}

.node-select-el .el-input__wrapper {
  background: rgba(30, 40, 70, 0.8);
  box-shadow: 0 0 0 1px rgba(64, 224, 255, 0.4) inset;
  transition: all 0.3s ease;
}

.node-select-el .el-input__wrapper:hover {
  box-shadow: 0 0 0 1px rgba(64, 224, 255, 0.6) inset;
}

.node-select-el .el-input__wrapper.is-focus {
  box-shadow: 0 0 0 1px #4facfe inset;
}

.node-select-el .el-input__inner {
  color: #e0e0e0;
  font-size: 0.9rem;
}

.node-select-el .el-input__inner::placeholder {
  color: rgba(224, 224, 224, 0.5);
}

/* 下拉面板样式 */
.el-select-dropdown {
  background: rgba(30, 40, 70, 0.95) !important;
  border: 1px solid rgba(64, 224, 255, 0.3) !important;
}

.el-select-dropdown__item {
  color: #e0e0e0;
  background: transparent;
}

.el-select-dropdown__item:hover {
  background: rgba(64, 224, 255, 0.2) !important;
}

.el-select-dropdown__item.is-selected {
  color: #4facfe;
  background: rgba(64, 224, 255, 0.15) !important;
}

.el-select-group__title {
  color: #4facfe;
  font-weight: bold;
}

.el-select-dropdown__empty {
  color: rgba(224, 224, 224, 0.5);
}

.demo-btn {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.demo-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

.demo-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-btn {
  background: linear-gradient(90deg, #9c27b0 0%, #673ab7 100%);
}

.custom-path-btn {
  background: linear-gradient(90deg, #4caf50 0%, #45a049 100%);
  padding: 0.6rem 1.5rem;
  font-weight: bold;
}

.custom-path-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.clear-btn {
  background: linear-gradient(90deg, #f44336 0%, #e91e63 100%);
}

.info {
  padding: 0.8rem 1.2rem;
  border-radius: 5px;
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 1rem;
}

.info.success {
  background: rgba(76, 175, 80, 0.2);
  border: 1px solid rgba(76, 175, 80, 0.5);
  color: #4caf50;
}

.info.error {
  background: rgba(244, 67, 54, 0.2);
  border: 1px solid rgba(244, 67, 54, 0.5);
  color: #f44336;
}

.info.loading {
  background: rgba(33, 150, 243, 0.2);
  border: 1px solid rgba(33, 150, 243, 0.5);
  color: #2196f3;
}

.canvas-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 1.5rem 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 8px;
  padding: 1rem;
  overflow: auto;
  min-height: 620px;
}

.canvas-container canvas {
  max-width: 100%;
  height: auto;
  border: 2px solid rgba(64, 224, 255, 0.5);
  border-radius: 4px;
  background: #0a1428;
  box-shadow: 0 0 20px rgba(64, 224, 255, 0.3);
  cursor: grab;
}

.canvas-container canvas:active {
  cursor: grabbing;
}

.canvas-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: rgba(20, 30, 60, 0.6);
  border-radius: 5px;
  border: 1px solid rgba(64, 224, 255, 0.3);
}

.zoom-btn {
  padding: 0.5rem 1rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.zoom-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

.zoom-level {
  color: #4facfe;
  font-size: 0.9rem;
  margin-left: 0.5rem;
  padding: 0.5rem;
  background: rgba(64, 224, 255, 0.1);
  border-radius: 3px;
  min-width: 80px;
  text-align: center;
}

.path-stats {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: rgba(20, 30, 60, 0.6);
  border-radius: 8px;
  border: 1px solid rgba(64, 224, 255, 0.2);
}

.path-stats h4 {
  color: #4facfe;
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.8rem;
  background: rgba(30, 40, 70, 0.4);
  border-radius: 5px;
}

.stat-label {
  color: #a0b3c6;
  font-size: 0.9rem;
}

.stat-value {
  color: #4facfe;
  font-size: 1.2rem;
  font-weight: bold;
}

.legend {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.2rem;
  padding: 1.5rem;
  background: rgba(20, 30, 60, 0.4);
  border-radius: 5px;
}

.legend-section {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding: 0.8rem;
  background: rgba(30, 40, 70, 0.3);
  border-radius: 5px;
  border: 1px solid rgba(64, 224, 255, 0.1);
}

.legend-section h4 {
  color: #4facfe;
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
  margin-top: 0.5rem;
}

.legend-section:first-child h4 {
  margin-top: 0;
}

.hint-section {
  margin-top: 1rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(64, 224, 255, 0.2);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #a0b3c6;
}

.hint-text {
  color: #4facfe;
  font-style: italic;
  font-size: 0.8rem;
}

.legend-box {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid currentColor;
  flex-shrink: 0;
}

.standpoint-box {
  background: rgba(0, 188, 212, 0.8);
  border-color: #00bcd4;
}

.runway-box {
  background: rgba(255, 152, 0, 0.8);
  border-color: #ff9800;
}

.observation-box {
  background: rgba(156, 39, 176, 0.8);
  border-color: #9c27b0;
}

.legend-line {
  width: 30px;
  height: 3px;
  flex-shrink: 0;
}

.aircraftroad-line {
  background: rgba(79, 172, 254, 0.5);
  height: 2px;
}

.networkroad-line {
  background: rgba(156, 39, 176, 0.5);
  height: 1.5px;
}

.externalroad-line {
  background: rgba(255, 87, 34, 0.5);
  height: 1.2px;
}

.servicevehicle-line {
  background: rgba(255, 193, 7, 0.4);
  height: 1px;
}

.perimeterroad-line {
  background: rgba(96, 125, 139, 0.4);
  height: 1px;
}

.path-line {
  background: rgba(76, 175, 80, 1);
  height: 3px;
  box-shadow: 0 0 5px rgba(76, 175, 80, 0.8);
}

@media (max-width: 768px) {
  .demo-controls {
    flex-direction: column;
  }

  .node-selection-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .selection-group {
    flex-direction: column;
    align-items: stretch;
  }

  .node-select-el {
    width: 100%;
  }

  .legend {
    grid-template-columns: 1fr;
    gap: 0.8rem;
    padding: 1rem;
  }

  .canvas-container canvas {
    width: 100%;
    height: auto;
  }

  .canvas-controls {
    flex-wrap: wrap;
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
