<template>
  <div class="multi-aircraft-scheduling">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">
          <i class="icon">✈️</i>
          多航班滑行路径优化与冲突调度
        </h1>
        <p class="page-description">
          基于FCFS、优先级调度策略的多航班实时冲突检测与路径优化系统
        </p>
      </div>

      <!-- 控制面板 -->
      <div class="control-panel">
        <div class="control-group">
          <label>航班数量:</label>
          <select v-model="flightCount" :disabled="isScheduling">
            <option value="3">3 架</option>
            <option value="5">5 架</option>
            <option value="6">6 架</option>
            <option value="8">8 架</option>
            <option value="10">10 架</option>
          </select>
        </div>

        <div class="control-group">
          <label>调度策略:</label>
          <select v-model="strategy" :disabled="isScheduling">
            <option value="fcfs">FCFS (先来先服务)</option>
            <option value="priority">优先级调度</option>
            <option value="time_window">时间窗调度</option>
          </select>
        </div>

        <div class="control-group">
          <button
            @click="generateFlights"
            class="btn btn-secondary"
            :disabled="isScheduling">
            <i class="icon">🎲</i> 生成航班
          </button>
          <button
            @click="scheduleFlights"
            class="btn btn-primary"
            :disabled="isScheduling || !flights.length">
            <i class="icon">▶️</i> {{ isScheduling ? '调度中...' : '开始调度' }}
          </button>
          <button
            @click="resetAll"
            class="btn btn-danger"
            :disabled="isScheduling">
            <i class="icon">🔄</i> 重置
          </button>
        </div>
      </div>

      <!-- 统计信息卡片 -->
      <div v-if="statistics" class="statistics-cards">
        <div class="stat-card">
          <div class="stat-label">航班总数</div>
          <div class="stat-value">{{ statistics.flight_count }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">总滑行距离</div>
          <div class="stat-value">{{ (statistics.total_distance / 1000).toFixed(2) }} km</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">总滑行时间</div>
          <div class="stat-value">{{ (statistics.total_time / 60).toFixed(1) }} 分钟</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">总延误时间</div>
          <div class="stat-value delay">{{ (statistics.total_delay / 60).toFixed(1) }} 分钟</div>
        </div>
        <div class="stat-card" :class="statistics.total_conflicts > 0 ? 'has-conflicts' : 'no-conflicts'">
          <div class="stat-label">冲突数量</div>
          <div class="stat-value">{{ statistics.total_conflicts }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">调度策略</div>
          <div class="stat-value strategy">{{ statistics.strategy }}</div>
        </div>
      </div>

      <!-- 航班列表 -->
      <div v-if="flights.length" class="flights-section">
        <h2 class="section-title">
          <i class="icon">📋</i> 航班列表
        </h2>
        <div class="flights-grid">
          <div
            v-for="flight in flights"
            :key="flight.flight_id"
            class="flight-card"
            :class="getFlightStatus(flight)">
            <div class="flight-header">
              <span class="flight-id">{{ flight.flight_id }}</span>
              <span class="flight-type">{{ flight.aircraft_type }}</span>
            </div>
            <div class="flight-details">
              <div class="detail-row">
                <span class="label">任务:</span>
                <span class="value" :class="flight.operation">
                  {{ flight.operation === 'departure' ? '离港' : '进港' }}
                </span>
              </div>
              <div class="detail-row">
                <span class="label">计划时间:</span>
                <span class="value">{{ formatTime(flight.scheduled_time) }}</span>
              </div>
              <div class="detail-row">
                <span class="label">优先级:</span>
                <span class="value" :class="flight.priority">
                  {{ getPriorityText(flight.priority) }}
                </span>
              </div>
              <div v-if="getScheduleResult(flight.flight_id)" class="flight-result">
                <div class="detail-row">
                  <span class="label">路径长度:</span>
                  <span class="value">{{ (getScheduleResult(flight.flight_id).total_distance / 1000).toFixed(2) }} km</span>
                </div>
                <div class="detail-row">
                  <span class="label">滑行时间:</span>
                  <span class="value">{{ (getScheduleResult(flight.flight_id).total_time / 60).toFixed(1) }} 分钟</span>
                </div>
                <div class="detail-row">
                  <span class="label">延误:</span>
                  <span class="value" :class="getScheduleResult(flight.flight_id).delay > 0 ? 'has-delay' : ''">
                    {{ (getScheduleResult(flight.flight_id).delay / 60).toFixed(1) }} 分钟
                  </span>
                </div>
                <div class="detail-row">
                  <span class="label">冲突:</span>
                  <span class="value" :class="getScheduleResult(flight.flight_id).conflict_count > 0 ? 'has-conflict' : ''">
                    {{ getScheduleResult(flight.flight_id).conflict_count }} 个
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2D 可视化 -->
      <div v-if="schedules.length" class="visualization-section">
        <h2 class="section-title">
          <i class="icon">🗺️</i> 路径可视化
        </h2>

        <!-- 2D Canvas -->
        <div class="canvas-container">
          <canvas
            ref="pathCanvas"
            :width="canvasWidth"
            :height="canvasHeight"
            class="path-canvas"></canvas>

          <!-- 图例 -->
          <div class="legend">
            <div class="legend-item">
              <span class="legend-color departure"></span>
              <span>离港航班</span>
            </div>
            <div class="legend-item">
              <span class="legend-color arrival"></span>
              <span>进港航班</span>
            </div>
            <div class="legend-item">
              <span class="legend-color conflict"></span>
              <span>冲突点</span>
            </div>
          </div>
        </div>

        <!-- 动画控制 -->
        <div class="animation-controls">
          <button
            @click="startAnimation"
            class="btn btn-primary"
            :disabled="isAnimating">
            <i class="icon">▶️</i> 播放动画
          </button>
          <button
            @click="stopAnimation"
            class="btn btn-secondary"
            :disabled="!isAnimating">
            <i class="icon">⏸️</i> 暂停
          </button>
          <div class="time-display">
            <span>当前时间: {{ animationTime }}</span>
          </div>
          <div class="speed-control">
            <label>播放速度:</label>
            <input
              type="range"
              v-model="animationSpeed"
              min="1"
              max="10"
              step="1">
            <span>{{ animationSpeed }}x</span>
          </div>
        </div>
      </div>

      <!-- 冲突列表 -->
      <div v-if="allConflicts.length" class="conflicts-section">
        <h2 class="section-title">
          <i class="icon">⚠️</i> 冲突详情 ({{ allConflicts.length }})
        </h2>
        <div class="conflicts-list">
          <div
            v-for="conflict in allConflicts"
            :key="conflict.conflict_id"
            class="conflict-card"
            :class="conflict.severity">
            <div class="conflict-header">
              <span class="conflict-type">{{ getConflictTypeText(conflict.conflict_type) }}</span>
              <span class="conflict-severity">{{ conflict.severity }}</span>
            </div>
            <div class="conflict-body">
              <div class="conflict-flights">
                涉及航班: {{ conflict.flight_ids.join(', ') }}
              </div>
              <div class="conflict-time">
                冲突时间: {{ formatTime(conflict.time) }}
              </div>
              <div class="conflict-node">
                节点ID: {{ conflict.node_id }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 甘特图 -->
      <div v-if="schedules.length" class="gantt-section">
        <h2 class="section-title">
          <i class="icon">📊</i> 时间甘特图
        </h2>
        <div class="gantt-chart">
          <svg ref="ganttSvg" :width="ganttWidth" :height="ganttHeight">
            <!-- 时间轴 -->
            <g v-for="(tick, index) in ganttTicks" :key="'tick-' + index">
              <line
                :x1="tick.x"
                :y1="0"
                :x2="tick.x"
                :y2="ganttHeight - 30"
                stroke="rgba(255,255,255,0.2)"
                stroke-dasharray="4"/>
              <text
                :x="tick.x"
                :y="ganttHeight - 10"
                fill="#a0b3c6"
                font-size="12"
                text-anchor="middle">{{ tick.label }}</text>
            </g>

            <!-- 航班条 -->
            <g v-for="(schedule, index) in schedules" :key="'flight-' + schedule.flight_id">
              <text
                :x="10"
                :y="index * 40 + 25"
                fill="#e0e0e0"
                font-size="12">{{ schedule.flight_id }}</text>

              <rect
                :x="getGanttBarX(schedule)"
                :y="index * 40 + 10"
                :width="getGanttBarWidth(schedule)"
                :height="25"
                :fill="getGanttBarColor(schedule)"
                :class="schedule.operation"/>

              <!-- 调整后的时间 -->
              <rect
                v-if="schedule.delay > 0"
                :x="getGanttBarX(schedule) + getDelayWidth(schedule)"
                :y="index * 40 + 10"
                :width="getDelayWidth(schedule)"
                :height="25"
                fill="rgba(255, 100, 100, 0.5)"
                fill-opacity="0.5"/>
            </g>
          </svg>
        </div>
      </div>
    </div>

    <!-- Toast 通知 -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE = 'http://localhost:5001'

export default {
  name: 'MultiAircraftScheduling',
  data() {
    return {
      flightCount: 6,
      strategy: 'fcfs',
      flights: [],
      schedules: [],
      statistics: null,
      isScheduling: false,

      // Canvas
      canvasWidth: 1200,
      canvasHeight: 700,

      // 动画
      isAnimating: false,
      animationSpeed: 5,
      animationFrame: null,
      animationStartTime: null,
      animationTime: '00:00:00',
      aircraftPositions: {},

      // 甘特图
      ganttWidth: 1200,
      ganttHeight: 300,
      ganttTicks: [],

      // Toast
      toast: {
        show: false,
        message: '',
        type: 'info',
        timeout: null
      }
    }
  },
  computed: {
    allConflicts() {
      const conflicts = []
      this.schedules.forEach(schedule => {
        schedule.conflicts.forEach(conflict => {
          if (!conflicts.find(c => c.conflict_id === conflict.conflict_id)) {
            conflicts.push(conflict)
          }
        })
      })
      return conflicts
    }
  },
  methods: {
    async generateFlights() {
      try {
        this.isScheduling = true
        this.resetSchedules()

        const response = await axios.post(`${API_BASE}/api/multi-aircraft/generate-simulation`, {
          num_flights: parseInt(this.flightCount),
          base_time: '2024-01-20 14:00:00'
        })

        if (response.data.success) {
          this.flights = response.data.flights
          this.showToast('航班数据生成成功！', 'success')
        }
      } catch (error) {
        console.error('生成航班失败:', error)
        this.showToast('生成航班失败: ' + error.message, 'error')
      } finally {
        this.isScheduling = false
      }
    },

    async scheduleFlights() {
      try {
        this.isScheduling = true
        this.stopAnimation()

        const response = await axios.post(`${API_BASE}/api/multi-aircraft/schedule`, {
          strategy: this.strategy,
          flights: this.flights
        })

        if (response.data.success) {
          this.schedules = response.data.schedules
          this.statistics = {
            flight_count: response.data.flight_count,
            total_distance: response.data.total_distance,
            total_time: response.data.total_time,
            total_delay: response.data.total_delay,
            total_conflicts: response.data.total_conflicts,
            strategy: response.data.strategy
          }

          this.prepareVisualization()
          this.showToast('调度完成！', 'success')
        }
      } catch (error) {
        console.error('调度失败:', error)
        this.showToast('调度失败: ' + error.message, 'error')
      } finally {
        this.isScheduling = false
      }
    },

    resetAll() {
      this.flights = []
      this.schedules = []
      this.statistics = null
      this.stopAnimation()
      this.clearCanvas()
    },

    resetSchedules() {
      this.schedules = []
      this.statistics = null
      this.stopAnimation()
    },

    prepareVisualization() {
      this.$nextTick(() => {
        this.drawNetwork()
        this.drawPaths()
        this.drawConflicts()
        this.prepareGanttChart()
      })
    },

    drawNetwork() {
      const canvas = this.$refs.pathCanvas
      if (!canvas) return

      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // 这里应该绘制机场路网
      // 暂时绘制简单的背景
      ctx.fillStyle = 'rgba(15, 23, 42, 0.9)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // 绘制网格
      ctx.strokeStyle = 'rgba(100, 200, 255, 0.1)'
      ctx.lineWidth = 1
      for (let x = 0; x < canvas.width; x += 50) {
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
      }
      for (let y = 0; y < canvas.height; y += 50) {
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(canvas.width, y)
        ctx.stroke()
      }
    },

    drawPaths() {
      const canvas = this.$refs.pathCanvas
      if (!canvas || !this.schedules.length) return

      const ctx = canvas.getContext('2d')

      // 收集所有点以确定缩放比例
      const allPoints = []
      this.schedules.forEach(schedule => {
        schedule.path.forEach(point => {
          allPoints.push([point.x, point.y])
        })
      })

      // 计算边界
      const xs = allPoints.map(p => p[0])
      const ys = allPoints.map(p => p[1])
      const minX = Math.min(...xs)
      const maxX = Math.max(...xs)
      const minY = Math.min(...ys)
      const maxY = Math.max(...ys)

      const padding = 100
      const scaleX = (canvas.width - padding * 2) / (maxX - minX)
      const scaleY = (canvas.height - padding * 2) / (maxY - minY)
      const scale = Math.min(scaleX, scaleY)

      const offsetX = (canvas.width - (maxX - minX) * scale) / 2 - minX * scale
      const offsetY = (canvas.height - (maxY - minY) * scale) / 2 - minY * scale

      // 保存转换函数
      this.transformPoint = (x, y) => ({
        x: x * scale + offsetX,
        y: y * scale + offsetY
      })

      // 为每个航班分配颜色
      const colors = [
        '#4facfe', '#00f2fe', '#f093fb', '#f5576c',
        '#43e97b', '#38f9d7', '#fa709a', '#fee140',
        '#30cfd0', '#330867'
      ]

      // 绘制路径
      this.schedules.forEach((schedule, index) => {
        const color = colors[index % colors.length]
        schedule.color = color

        ctx.strokeStyle = color
        ctx.lineWidth = 2
        ctx.setLineDash([5, 5])

        ctx.beginPath()
        schedule.path.forEach((point, i) => {
          const transformed = this.transformPoint(point.x, point.y)
          if (i === 0) {
            ctx.moveTo(transformed.x, transformed.y)
          } else {
            ctx.lineTo(transformed.x, transformed.y)
          }
        })
        ctx.stroke()
        ctx.setLineDash([])

        // 绘制起点和终点
        const startPoint = this.transformPoint(schedule.path[0].x, schedule.path[0].y)
        const endPoint = this.transformPoint(
          schedule.path[schedule.path.length - 1].x,
          schedule.path[schedule.path.length - 1].y
        )

        // 起点
        ctx.fillStyle = color
        ctx.beginPath()
        ctx.arc(startPoint.x, startPoint.y, 8, 0, Math.PI * 2)
        ctx.fill()

        // 终点
        ctx.strokeStyle = color
        ctx.lineWidth = 3
        ctx.beginPath()
        ctx.arc(endPoint.x, endPoint.y, 8, 0, Math.PI * 2)
        ctx.stroke()

        // 标签
        ctx.fillStyle = '#ffffff'
        ctx.font = '12px Arial'
        ctx.fillText(schedule.flight_id, startPoint.x - 20, startPoint.y - 15)
      })
    },

    drawConflicts() {
      const canvas = this.$refs.pathCanvas
      if (!canvas || !this.allConflicts.length) return

      const ctx = canvas.getContext('2d')

      // 绘制冲突点
      this.allConflicts.forEach(conflict => {
        // 找到冲突节点
        const schedule = this.schedules.find(s =>
          s.path.some(p => p.id === conflict.node_id)
        )

        if (schedule) {
          const point = schedule.path.find(p => p.id === conflict.node_id)
          if (point) {
            const transformed = this.transformPoint(point.x, point.y)

            // 绘制红色警告圆圈
            ctx.fillStyle = conflict.severity === 'high' ? 'rgba(255, 0, 0, 0.6)' : 'rgba(255, 165, 0, 0.6)'
            ctx.beginPath()
            ctx.arc(transformed.x, transformed.y, 15, 0, Math.PI * 2)
            ctx.fill()

            ctx.strokeStyle = '#ffffff'
            ctx.lineWidth = 2
            ctx.stroke()

            // 警告图标
            ctx.fillStyle = '#ffffff'
            ctx.font = 'bold 16px Arial'
            ctx.fillText('!', transformed.x - 4, transformed.y + 5)
          }
        }
      })
    },

    clearCanvas() {
      const canvas = this.$refs.pathCanvas
      if (!canvas) return

      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
    },

    startAnimation() {
      if (this.isAnimating) return

      this.isAnimating = true
      this.animationStartTime = Date.now()

      const animate = () => {
        if (!this.isAnimating) return

        const elapsed = Date.now() - this.animationStartTime
        const speedFactor = this.animationSpeed * 100
        const currentTime = elapsed * speedFactor

        // 更新时间显示
        const seconds = Math.floor(currentTime / 1000)
        const minutes = Math.floor(seconds / 60)
        const hours = Math.floor(minutes / 60)
        this.animationTime = `${String(hours).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`

        // 重绘
        this.drawNetwork()
        this.drawPaths()

        // 绘制飞机位置
        this.drawAircraftPositions(currentTime)

        this.animationFrame = requestAnimationFrame(animate)
      }

      animate()
    },

    stopAnimation() {
      this.isAnimating = false
      if (this.animationFrame) {
        cancelAnimationFrame(this.animationFrame)
        this.animationFrame = null
      }
    },

    drawAircraftPositions(currentTime) {
      const canvas = this.$refs.pathCanvas
      if (!canvas) return

      const ctx = canvas.getContext('2d')

      this.schedules.forEach(schedule => {
        const waypoints = schedule.waypoints
        if (!waypoints.length) return

        // 找到当前位置
        let position = null
        for (let i = 0; i < waypoints.length - 1; i++) {
          const start = new Date(waypoints[i].time).getTime()
          const end = new Date(waypoints[i + 1].time).getTime()

          if (currentTime >= start && currentTime <= end) {
            const progress = (currentTime - start) / (end - start)
            const startNode = waypoints[i]
            const endNode = waypoints[i + 1]

            const startPos = this.transformPoint(startNode.x, startNode.y)
            const endPos = this.transformPoint(endNode.x, endNode.y)

            position = {
              x: startPos.x + (endPos.x - startPos.x) * progress,
              y: startPos.y + (endPos.y - startPos.y) * progress
            }
            break
          }
        }

        if (position) {
          // 绘制飞机
          ctx.fillStyle = schedule.color
          ctx.beginPath()
          ctx.arc(position.x, position.y, 10, 0, Math.PI * 2)
          ctx.fill()

          ctx.strokeStyle = '#ffffff'
          ctx.lineWidth = 2
          ctx.stroke()
        }
      })
    },

    prepareGanttChart() {
      if (!this.schedules.length) return

      // 计算时间范围
      const times = this.schedules.map(s => ({
        start: new Date(s.start_time).getTime(),
        end: new Date(s.end_time).getTime()
      }))

      const minTime = Math.min(...times.map(t => t.start))
      const maxTime = Math.max(...times.map(t => t.end))
      const totalDuration = maxTime - minTime

      // 生成时间刻度
      this.ganttTicks = []
      const tickCount = 10
      for (let i = 0; i <= tickCount; i++) {
        const time = minTime + (totalDuration * i / tickCount)
        const date = new Date(time)
        this.ganttTicks.push({
          x: 100 + (this.ganttWidth - 120) * i / tickCount,
          label: `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
        })
      }

      // 调整高度
      this.ganttHeight = Math.max(300, this.schedules.length * 40 + 50)
    },

    getGanttBarX(schedule) {
      const minTime = Math.min(...this.schedules.map(s =>
        new Date(s.start_time).getTime()
      ))
      const maxTime = Math.max(...this.schedules.map(s =>
        new Date(s.end_time).getTime()
      ))
      const totalDuration = maxTime - minTime
      const startTime = new Date(schedule.start_time).getTime()

      return 100 + ((startTime - minTime) / totalDuration) * (this.ganttWidth - 120)
    },

    getGanttBarWidth(schedule) {
      const minTime = Math.min(...this.schedules.map(s =>
        new Date(s.start_time).getTime()
      ))
      const maxTime = Math.max(...this.schedules.map(s =>
        new Date(s.end_time).getTime()
      ))
      const totalDuration = maxTime - minTime
      const duration = new Date(schedule.end_time).getTime() -
                       new Date(schedule.start_time).getTime()

      return (duration / totalDuration) * (this.ganttWidth - 120)
    },

    getDelayWidth(schedule) {
      const minTime = Math.min(...this.schedules.map(s =>
        new Date(s.start_time).getTime()
      ))
      const maxTime = Math.max(...this.schedules.map(s =>
        new Date(s.end_time).getTime()
      ))
      const totalDuration = maxTime - minTime

      return (schedule.delay * 1000 / totalDuration) * (this.ganttWidth - 120)
    },

    getGanttBarColor(schedule) {
      return schedule.operation === 'departure' ? '#4facfe' : '#43e97b'
    },

    getScheduleResult(flightId) {
      return this.schedules.find(s => s.flight_id === flightId)
    },

    getFlightStatus(flight) {
      const schedule = this.getScheduleResult(flight.flight_id)
      if (!schedule) return 'pending'

      if (schedule.conflict_count > 0) return 'has-conflict'
      if (schedule.delay > 0) return 'has-delay'
      return 'success'
    },

    formatTime(timeStr) {
      if (!timeStr) return '-'
      const date = new Date(timeStr)
      return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    },

    getPriorityText(priority) {
      const map = {
        'high': '高',
        'medium': '中',
        'low': '低'
      }
      return map[priority] || priority
    },

    getConflictTypeText(type) {
      const map = {
        'node': '节点冲突',
        'edge': '边冲突',
        'crossing': '交叉冲突'
      }
      return map[type] || type
    },

    showToast(message, type = 'info') {
      if (this.toast.timeout) {
        clearTimeout(this.toast.timeout)
      }

      this.toast.message = message
      this.toast.type = type
      this.toast.show = true

      this.toast.timeout = setTimeout(() => {
        this.toast.show = false
      }, 3000)
    }
  },
  beforeUnmount() {
    this.stopAnimation()
  }
}
</script>

<style scoped>
.multi-aircraft-scheduling {
  padding: 2rem 0;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-description {
  font-size: 1.1rem;
  color: #a0b3c6;
}

.icon {
  margin-right: 0.5rem;
}

/* 控制面板 */
.control-panel {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.control-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.control-group label {
  color: #a0b3c6;
  font-weight: 500;
}

select {
  padding: 0.5rem 1rem;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 6px;
  color: #e0e0e0;
  cursor: pointer;
}

select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

.btn-secondary {
  background: rgba(100, 116, 139, 0.8);
  color: #ffffff;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(100, 116, 139, 1);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.8);
  color: #ffffff;
}

.btn-danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 1);
}

/* 统计卡片 */
.statistics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.stat-label {
  font-size: 0.9rem;
  color: #a0b3c6;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 600;
  color: #ffffff;
}

.stat-value.delay {
  color: #fbbf24;
}

.stat-card.has-conflicts .stat-value {
  color: #f87171;
}

.stat-card.no-conflicts .stat-value {
  color: #4ade80;
}

.stat-value.strategy {
  font-size: 1.2rem;
  text-transform: uppercase;
}

/* 航班列表 */
.section-title {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #e0e0e0;
}

.flights-section {
  margin-bottom: 2rem;
}

.flights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.flight-card {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.flight-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.flight-card.has-conflict {
  border-color: rgba(248, 113, 113, 0.5);
}

.flight-card.has-delay {
  border-color: rgba(251, 191, 36, 0.5);
}

.flight-card.success {
  border-color: rgba(74, 222, 128, 0.5);
}

.flight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.flight-id {
  font-size: 1.2rem;
  font-weight: 600;
  color: #ffffff;
}

.flight-type {
  font-size: 0.9rem;
  color: #a0b3c6;
  background: rgba(100, 116, 139, 0.5);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.flight-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.detail-row .label {
  color: #a0b3c6;
}

.detail-row .value {
  color: #e0e0e0;
  font-weight: 500;
}

.detail-row .value.departure {
  color: #4facfe;
}

.detail-row .value.arrival {
  color: #4ade80;
}

.detail-row .value.high {
  color: #f87171;
}

.detail-row .value.medium {
  color: #fbbf24;
}

.detail-row .value.low {
  color: #94a3b8;
}

.detail-row .value.has-delay {
  color: #fbbf24;
}

.detail-row .value.has-conflict {
  color: #f87171;
}

.flight-result {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 可视化 */
.visualization-section {
  margin-bottom: 2rem;
}

.canvas-container {
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  position: relative;
}

.path-canvas {
  width: 100%;
  height: auto;
  display: block;
}

.legend {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-top: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #a0b3c6;
  font-size: 0.9rem;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.legend-color.departure {
  background: #4facfe;
}

.legend-color.arrival {
  background: #43e97b;
}

.legend-color.conflict {
  background: rgba(255, 0, 0, 0.6);
}

.animation-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
}

.time-display {
  color: #e0e0e0;
  font-family: monospace;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 6px;
}

.speed-control {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  color: #a0b3c6;
}

.speed-control input[type="range"] {
  width: 100px;
}

/* 冲突列表 */
.conflicts-section {
  margin-bottom: 2rem;
}

.conflicts-list {
  display: grid;
  gap: 1rem;
}

.conflict-card {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
}

.conflict-card.high {
  border-color: rgba(248, 113, 113, 0.5);
  background: rgba(248, 113, 113, 0.1);
}

.conflict-card.medium {
  border-color: rgba(251, 191, 36, 0.5);
}

.conflict-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.conflict-type {
  font-weight: 600;
  color: #ffffff;
}

.conflict-severity {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.conflict-card.high .conflict-severity {
  background: rgba(248, 113, 113, 0.3);
  color: #f87171;
}

.conflict-card.medium .conflict-severity {
  background: rgba(251, 191, 36, 0.3);
  color: #fbbf24;
}

.conflict-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  color: #a0b3c6;
  font-size: 0.9rem;
}

/* 甘特图 */
.gantt-section {
  margin-bottom: 2rem;
}

.gantt-chart {
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 12px;
  padding: 1rem;
  overflow-x: auto;
}

.gantt-chart svg {
  display: block;
  margin: 0 auto;
}

/* Toast */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: #ffffff;
  font-weight: 500;
  z-index: 9999;
  animation: slideIn 0.3s ease;
}

.toast.success {
  background: rgba(74, 222, 128, 0.9);
}

.toast.error {
  background: rgba(248, 113, 113, 0.9);
}

.toast.info {
  background: rgba(79, 172, 254, 0.9);
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.8rem;
  }

  .control-panel {
    flex-direction: column;
  }

  .statistics-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .flights-grid {
    grid-template-columns: 1fr;
  }
}
</style>
