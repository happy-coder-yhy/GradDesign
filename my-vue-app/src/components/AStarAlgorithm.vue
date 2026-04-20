<template>
  <div class="dashboard">
    <!-- Background FX -->
    <div class="grid-bg"></div>
    <div class="particles-bg"></div>

    <!-- Header -->
    <header class="dash-header">
      <div class="header-left">
        <div class="logo">✈️</div>
        <div class="title-group">
          <h1 class="main-title">A*路径规划算法</h1>
          <p class="sub-title">机场场面滑行轨迹优化系统</p>
        </div>
      </div>
      <div class="header-center">
        <div class="kpi-bar">
          <div class="kpi-item">
            <span class="kpi-label">航班数</span>
            <span class="kpi-value">{{ statistics ? statistics.flight_count : flights.length || 0 }}</span>
          </div>
          <div class="kpi-item">
            <span class="kpi-label">冲突数</span>
            <span class="kpi-value" :class="{ danger: allConflicts.length > 0 }">{{ allConflicts.length }}</span>
          </div>
          <div class="kpi-item">
            <span class="kpi-label">计算耗时</span>
            <span class="kpi-value">{{ computeTime }}<small>ms</small></span>
          </div>
          <div class="kpi-item">
            <span class="kpi-label">总距离</span>
            <span class="kpi-value">{{ statistics ? (statistics.total_distance/1000).toFixed(2) : '0.00' }}<small>km</small></span>
          </div>
        </div>
      </div>
      <div class="header-right">
        <div class="live-badge">
          <span class="live-dot"></span>
          <span>LIVE</span>
        </div>
        <div class="clock">{{ currentTime }}</div>
        <WeatherWidget />
        <div class="sys-status" :class="getSystemStatusClass()">{{ getSystemStatusText() }}</div>
      </div>
    </header>

    <!-- Tab Switcher -->
    <div class="tab-bar">
      <div class="tab-pills">
        <button :class="{ active: activeTab === 'single' }" @click="switchTab('single')">单航班演示</button>
        <button :class="{ active: activeTab === 'multi' }" @click="switchTab('multi')">多航班调度</button>
      </div>
    </div>

    <!-- Main Grid -->
    <main class="main-grid">
      <!-- Left Sidebar -->
      <aside class="sidebar left">
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">控制面板</span>
          </div>
          <div class="panel-body compact">
            <!-- Single-flight controls -->
            <div v-if="activeTab === 'single'" class="icon-row">
              <button class="icon-btn" @click="loadDemo" title="加载路网">
                <span class="ico">🗺️</span><span>路网</span>
              </button>
              <button class="icon-btn" @click="runFarthestStand" title="最远机位">
                <span class="ico">📍</span><span>最远</span>
              </button>
              <button class="icon-btn" @click="runStandToRunway" title="机位到跑道">
                <span class="ico">✈️</span><span>跑道</span>
              </button>
            </div>
            <!-- Multi-flight controls -->
            <div v-else class="icon-row">
              <button class="icon-btn" @click="showUploadModal = true" title="上传航班">
                <span class="ico">📤</span><span>上传</span>
              </button>
              <button class="icon-btn" @click="showSettingsPanel = !showSettingsPanel" title="参数设置">
                <span class="ico">⚙️</span><span>设置</span>
              </button>
              <button class="icon-btn" @click="generateFlights" :disabled="isScheduling" title="随机生成">
                <span class="ico">🎲</span><span>生成</span>
              </button>
            </div>
            <div v-show="showSettingsPanel && activeTab === 'multi'" class="settings-drawer">
              <div class="field">
                <label>调度策略</label>
                <select v-model="strategy" :disabled="isScheduling">
                  <option value="fcfs">FCFS</option>
                  <option value="priority">优先级</option>
                  <option value="time_window">时间窗</option>
                </select>
              </div>
              <div class="field">
                <label>航班数量</label>
                <input type="number" v-model.number="flightCount" :disabled="isScheduling" min="10" max="200" />
                <div v-if="flightCountError" class="err">{{ flightCountError }}</div>
              </div>
              <div class="field actions">
                <button class="btn primary" @click="scheduleFlights" :disabled="isScheduling || !flights.length">
                  {{ isScheduling ? '调度中...' : '开始调度' }}
                </button>
                <button class="btn danger" @click="resetMulti" :disabled="isScheduling">重置</button>
              </div>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header"><span class="panel-title">时段状态</span></div>
          <div class="panel-body">
            <div class="period-badge" :class="currentPeriodType">
              <div class="dot"></div>
              <div class="txt">
                <div class="period-title">
                  {{ currentPeriodType==='peak'?'高峰时段':(currentPeriodType==='off_peak'?'低峰时段':'正常时段') }}
                </div>
                <div class="period-sub">时间权重 {{ weights.time.toFixed(1) }} | 燃料权重 {{ weights.fuel.toFixed(1) }}</div>
              </div>
            </div>
            <div class="density-bar-wrap" v-if="flightDensity">
              <div class="density-label">
                <span>航班密度</span>
                <span class="density-val">{{ flightDensity.average_density.toFixed(1) }} 架次/小时</span>
              </div>
              <div class="density-track">
                <div class="density-fill" :class="currentPeriodType" :style="{ width: Math.min(100, (flightDensity.average_density / 60) * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header"><span class="panel-title">航班状态</span></div>
          <div class="panel-body center">
            <div class="pie-wrap">
              <div class="pie">
                <div class="pie-half left" :style="{ background: pieColors.departure }"></div>
                <div class="pie-half right" :style="{ background: pieColors.arrival }"></div>
              </div>
              <div class="pie-legend">
                <div v-for="s in getOperationStats()" :key="s.label" class="pie-lv">
                  <span class="dot" :style="{ background: s.color }"></span>
                  <span>{{ s.label }} {{ s.value }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header"><span class="panel-title">当前策略</span></div>
          <div class="panel-body center">
            <div class="strategy-ring" :class="strategy">
              <div class="ring-inner">
                <div class="ring-label">{{ strategy==='fcfs'?'FCFS':(strategy==='priority'?'优先级':'时间窗') }}</div>
                <div class="ring-sub">调度策略</div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- Center Area -->
      <section class="center-area">
        <div class="map-panel">
          <!-- Single Flight -->
          <div v-show="activeTab === 'single'" class="single-map-wrap">
            <NetworkVisualization
              ref="networkViz"
              demo1ButtonName="最远机位路径"
              demo2ButtonName="机位到跑道"
              :toggleButtonText="{ showMore: '显示跑道点和观察点', showOnly: '只显示机位' }"
              hint="滚轮缩放，拖拽移动 | 使用下方下拉列表选择起点和终点"
              resultPathName="A*优化路径"
              @loadData="loadDemo"
              @runDemo1="runFarthestStand"
              @runDemo2="runStandToRunway"
              @displayToggled="handleDisplayToggled"
              @runCustomPath="calculateCustomPath"
            />
          </div>
          <!-- Multi Flight -->
          <div v-show="activeTab === 'multi'" class="multi-map-wrap">
            <div class="canvas-box">
              <canvas
                ref="multiCanvas"
                width="1200"
                height="800"
                @wheel="handleMultiWheel"
                @mousedown="handleMultiMouseDown"
                @mousemove="handleMultiMouseMove"
                @mouseup="handleMultiMouseUp"
                @mouseleave="handleMultiMouseUp"
              ></canvas>
              <div v-if="conflictTooltip.show" class="conflict-tooltip"
                :style="{ left: conflictTooltip.x + 'px', top: conflictTooltip.y + 'px' }">
                <div class="tt-title">⚠️ 冲突信息</div>
                <div class="tt-row"><span>航班1:</span><b>{{ conflictTooltip.conflict.flight_ids[0] }}</b></div>
                <div class="tt-row"><span>航班2:</span><b>{{ conflictTooltip.conflict.flight_ids[1] }}</b></div>
                <div class="tt-row"><span>节点:</span><b>{{ (conflictTooltip.conflict.node_ids||[conflictTooltip.conflict.node_id]).join(', ') }}</b></div>
                <div class="tt-row"><span>时间:</span><b>{{ formatTime(conflictTooltip.conflict.time) }}</b></div>
              </div>
            </div>
            <div class="canvas-toolbar">
              <button @click="multiZoomIn">+</button>
              <button @click="multiZoomOut">−</button>
              <button @click="multiResetView">重置</button>
              <button @click="toggleMultiDisplay">{{ showCoreNodesOnly ? '显示全部' : '仅机位' }}</button>
              <span class="zoom-txt">{{ (multiZoomLevel*100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Right Sidebar -->
      <aside class="sidebar right">
        <!-- Flight List -->
        <div class="panel flight-panel">
          <div class="panel-header">
            <span class="panel-title">航班列表</span>
            <div class="flight-ops" v-if="schedules.length">
              <span class="sel-text">{{ selectedFlightIds.length }}/{{ flights.length }}</span>
              <button class="mini-btn" @click="toggleSelectAll">{{ selectedFlightIds.length === flights.length ? '取消' : '全选' }}</button>
            </div>
          </div>
          <div class="panel-body">
            <div class="flight-list">
              <div v-for="flight in flights" :key="flight.flight_id"
                class="flight-card"
                :class="[getFlightStatusClass(flight), { selected: selectedFlightIds.includes(flight.flight_id) }]"
                @click="toggleFlightSelection(flight.flight_id)">
                <div class="flight-main">
                  <input type="checkbox" :checked="selectedFlightIds.includes(flight.flight_id)"
                    @click.stop="toggleFlightSelection(flight.flight_id)" :disabled="!schedules.length" class="fc-check" />
                  <div class="flight-info">
                    <div class="flight-top">
                      <span class="fid">{{ flight.flight_id }}</span>
                      <span class="ftype">{{ flight.aircraft_type }}</span>
                      <span class="fop" :class="flight.operation">{{ flight.operation==='departure'?'离港':'进港' }}</span>
                    </div>
                    <div class="flight-mid" v-if="getScheduleResult(flight.flight_id)">
                      <span>📏 {{ (getScheduleResult(flight.flight_id).total_distance/1000).toFixed(2) }}km</span>
                      <span>⏱ {{ (getScheduleResult(flight.flight_id).total_time/60).toFixed(1) }}min</span>
                      <span :class="{ warn: getScheduleResult(flight.flight_id).delay > 0 }">
                        延误 {{ (getScheduleResult(flight.flight_id).delay/60).toFixed(1) }}min
                      </span>
                    </div>
                    <div class="flight-mid" v-else>
                      <span>计划 {{ formatTime(flight.scheduled_time) }}</span>
                      <span>优先级 {{ flight.priority }}</span>
                    </div>
                  </div>
                </div>
                <div class="flight-actions" v-if="getScheduleResult(flight.flight_id)">
                  <button v-if="getScheduleResult(flight.flight_id).conflict_count > 0"
                    class="alt-btn danger"
                    @click.stop="showPathAlternatives(flight)">
                    ⚠️ 冲突消解
                  </button>
                  <button v-else class="alt-btn safe" disabled>
                    ✓ 无冲突
                  </button>
                </div>
              </div>
              <div v-if="!flights.length" class="alarm-empty">暂无航班数据</div>
            </div>
          </div>
        </div>

        <!-- Conflict List -->
        <div class="panel alarm-panel">
          <div class="panel-header">
            <span class="panel-title">实况报警</span>
            <span class="alarm-badge" :class="{ danger: allConflicts.length > 0 }">{{ allConflicts.length }}</span>
          </div>
          <div class="panel-body">
            <div class="alarm-list">
              <div v-for="c in allConflicts.slice(0, 6)" :key="c.conflict_id" class="alarm-card" :class="c.severity" @click="selectConflictFlights(c)">
                <div class="alarm-row">
                  <span class="alarm-type">{{ getConflictTypeText(c.conflict_type) }}</span>
                  <span class="alarm-time">{{ formatTime(c.time) }}</span>
                </div>
                <div class="alarm-flights">{{ c.flight_ids.join(' / ') }}</div>
                <div class="alarm-node">节点 {{ (c.node_ids||[c.node_id]).join(', ') }}</div>
              </div>
              <div v-if="!allConflicts.length" class="alarm-empty">暂无冲突</div>
            </div>
          </div>
        </div>
      </aside>
    </main>

    <!-- Footer -->
    <footer class="dash-footer">
      <div class="footer-card">
        <div class="f-title">冲突等级分布</div>
        <div class="ring-chart-wrap">
          <div class="ring-chart">
            <div class="ring-segment high" :style="{ flex: Math.max(1, allConflicts.filter(c=>c.severity==='high').length) }"></div>
            <div class="ring-segment medium" :style="{ flex: Math.max(1, allConflicts.filter(c=>c.severity==='medium').length) }"></div>
            <div class="ring-segment safe" :style="{ flex: Math.max(1, flights.length - allConflicts.length) }"></div>
          </div>
          <div class="ring-legend-v">
            <div><span class="lg-dot" style="background:#f44336"></span>高危 {{ allConflicts.filter(c=>c.severity==='high').length }}</div>
            <div><span class="lg-dot" style="background:#ff9800"></span>中危 {{ allConflicts.filter(c=>c.severity==='medium').length }}</div>
            <div><span class="lg-dot" style="background:#4ade80"></span>正常 {{ Math.max(0, flights.length - allConflicts.length) }}</div>
          </div>
        </div>
      </div>
      <div class="footer-card stats-footer">
        <div class="f-title">概况统计</div>
        <div class="big-stat-grid footer-stats">
          <div class="big-stat">
            <div class="big-num">{{ statistics ? statistics.flight_count : flights.length || 0 }}</div>
            <div class="big-label">航班总数</div>
          </div>
          <div class="big-stat">
            <div class="big-num">{{ statistics ? (statistics.total_distance/1000).toFixed(2) : '0.00' }}</div>
            <div class="big-label">总距离(km)</div>
          </div>
          <div class="big-stat">
            <div class="big-num">{{ statistics ? (statistics.total_time/60).toFixed(1) : '0.0' }}</div>
            <div class="big-label">总时间(min)</div>
          </div>
          <div class="big-stat">
            <div class="big-num" :class="{ warn: statistics && statistics.total_delay > 0 }">
              {{ statistics ? (statistics.total_delay/60).toFixed(1) : '0.0' }}
            </div>
            <div class="big-label">总延误(min)</div>
          </div>
        </div>
      </div>
      <div class="footer-card">
        <div class="f-title">延误概览</div>
        <div class="delay-overview">
          <div class="d-circle" :class="{ warn: statistics && statistics.total_delay > 0 }">
            <div class="d-num">{{ statistics ? (statistics.total_delay/60).toFixed(1) : '0.0' }}</div>
            <div class="d-unit">分钟</div>
          </div>
          <div class="d-bars">
            <div class="d-row">
              <span :title="statistics ? '平均延误: ' + (statistics.total_delay/statistics.flight_count/60).toFixed(2) + ' 分钟' : '平均延误: 0.00 分钟'">平均延误</span>
              <div class="d-track"><div class="d-fill" :style="{ width: Math.min(100, (statistics?(statistics.total_delay/statistics.flight_count/60):0)*10)+'%' }"></div><div class="d-tooltip-layer" :title="statistics ? '平均延误: ' + (statistics.total_delay/statistics.flight_count/60).toFixed(2) + ' 分钟' : '平均延误: 0.00 分钟'"></div></div>
            </div>
            <div class="d-row">
              <span :title="statistics ? '平均距离: ' + (statistics.total_distance/statistics.flight_count/1000).toFixed(2) + ' km' : '平均距离: 0.00 km'">平均距离</span>
              <div class="d-track"><div class="d-fill blue" :style="{ width: Math.min(100, (statistics?(statistics.total_distance/statistics.flight_count/100):0))+'%' }"></div><div class="d-tooltip-layer" :title="statistics ? '平均距离: ' + (statistics.total_distance/statistics.flight_count/1000).toFixed(2) + ' km' : '平均距离: 0.00 km'"></div></div>
            </div>
            <div class="d-row">
              <span :title="statistics ? '平均时间: ' + (statistics.total_time/statistics.flight_count/60).toFixed(2) + ' 分钟' : '平均时间: 0.00 分钟'">平均时间</span>
              <div class="d-track"><div class="d-fill cyan" :style="{ width: Math.min(100, (statistics?(statistics.total_time/statistics.flight_count/60):0)*3)+'%' }"></div><div class="d-tooltip-layer" :title="statistics ? '平均时间: ' + (statistics.total_time/statistics.flight_count/60).toFixed(2) + ' 分钟' : '平均时间: 0.00 分钟'"></div></div>
            </div>
          </div>
        </div>
      </div>
    </footer>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal-box">
        <div class="modal-head">
          <h3>📁 上传航班数据</h3>
          <button class="modal-close" @click="showUploadModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="source-tabs">
            <button :class="{ active: dataSource === 'random' }" @click="switchDataSource('random')">随机生成</button>
            <button :class="{ active: dataSource === 'upload' }" @click="switchDataSource('upload')">上传文件</button>
          </div>
          <div v-show="dataSource === 'random'" class="source-content">
            <label>航班数量: <input type="number" v-model.number="flightCount" min="10" max="200" /></label>
            <button class="btn primary" @click="generateFlights" :disabled="isScheduling">🎲 生成航班</button>
          </div>
          <div v-show="dataSource === 'upload'" class="source-content">
            <input type="file" ref="fileInput" @change="handleFileChange" accept=".xlsx,.xls" style="display:none" />
            <button class="btn" @click="$refs.fileInput?.click()">📤 选择文件</button>
            <span v-if="selectedFile" class="file-tag">{{ selectedFile.name }}</span>
            <button class="btn primary" @click="extractFlightsFromExcel" :disabled="!selectedFile">📥 提取航班</button>
            <div v-if="uploadError" class="err">{{ uploadError }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Path Alternatives Sidebar -->
    <transition name="slide">
      <div v-if="showPathAlternativesPanel" class="alt-sidebar">
        <div class="alt-head">
          <h3>🛤️ 路径选项</h3>
          <button @click="closePathAlternatives" class="close-btn">×</button>
        </div>
        <div class="alt-body">
          <div v-if="selectedFlight" class="alt-info">
            <h4>{{ selectedFlight.flight_id }}</h4>
            <div class="alt-tags">
              <span>{{ selectedFlight.aircraft_type }}</span>
              <span :class="selectedFlight.operation">{{ selectedFlight.operation==='departure'?'离港':'进港' }}</span>
            </div>
          </div>
          <div v-if="loadingAlternatives" class="loading"><div class="spinner"></div><p>查找中...</p></div>
          <div v-else-if="pathAlternatives.length" class="alt-list">
            <div v-for="alt in pathAlternatives" :key="alt.path_id" class="alt-card" :class="{ active: alt.path_id === activePathId, conflict: alt.has_conflict }">
              <div class="alt-rank">路径 {{ alt.rank }}
                <span v-if="alt.is_original" class="tag">当前</span>
                <span v-if="alt.has_conflict" class="tag conflict">冲突</span>
              </div>
              <div class="alt-stat">📏 {{ (alt.distance/1000).toFixed(2) }} km | ⏱ {{ (alt.time/60).toFixed(1) }} min</div>
              <div class="alt-actions">
                <button @click="togglePreview(alt)" :disabled="alt.path_id===activePathId || alt.disabled">{{ isPreviewingPath && previewPathData && previewPathData.path_id === alt.path_id ? '取消预览' : '预览' }}</button>
                <button class="primary" @click="applyAlternativePath(alt)" :disabled="alt.path_id===activePathId || alt.disabled">应用</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from 'axios';
import NetworkVisualization from './NetworkVisualization.vue';
import WeatherWidget from './WeatherWidget.vue';
import * as XLSX from 'xlsx';
import { ElMessage } from 'element-plus';

const API_BASE = 'http://localhost:5001/api';

export default {
  name: 'AStarAlgorithm',
  components: {
    NetworkVisualization,
    WeatherWidget
  },
  mounted() {
    this.startTimer();
  },
  beforeUnmount() {
    if (this.timeTimer) clearInterval(this.timeTimer);
  },
  data() {
    return {
      activeTab: 'single', // 'single' 或 'multi'
      activeMainTab: 'details', // 'details' 或 'demo'
      nodes: [],
      edges: [],

      // 多航班相关
      flightCount: 10,
      flightCountError: '', // 航班数量输入错误提示
      strategy: 'fcfs',
      flights: [],
      schedules: [],
      statistics: null,
      isScheduling: false,

      // 文件上传相关
      dataSource: 'random', // 'random' 或 'upload'
      selectedFile: null,
      uploadError: '',

      // 航班选择相关
      selectedFlightIds: [], // 选中的航班ID列表
      manuallyCleared: false, // 标记是否手动清除了选择

      // 备选路径相关
      showPathAlternativesPanel: false,
      selectedFlight: null,
      pathAlternatives: [],
      activePathId: 'path_1',
      loadingAlternatives: false,
      originalPathData: null, // 保存原始路径数据用于对比
      isPreviewingPath: false, // 标记是否正在预览路径
      previewPathData: null, // 保存预览路径的数据

      // 多航班可视化数据
      multiNodes: [],
      multiEdges: [],
      multiNodesLoaded: false,
      showCoreNodesOnly: false,
      multiCanvas: null,
      multiCtx: null,

      // 多航班画布缩放和平移
      multiZoomLevel: 1.0,
      multiPanOffset: { x: 0, y: 0 },
      multiIsDragging: false,
      multiDragStart: { x: 0, y: 0 },
      
      // 冲突点悬浮提示
      conflictTooltip: {
        show: false,
        x: 0,
        y: 0,
        conflict: null
      },
      // 缓存冲突点位置信息用于精确检测
      conflictPointPositions: [],
      multiBaseScale: 1.0,
      multiBaseOffsetX: 0,
      multiBaseOffsetY: 0,

      // 航班密度分析和权重动态调整
      flightDensity: null,
      peakPeriods: [],
      offPeakPeriods: [],
      timePeriodAnalysis: null,
      currentPeriodType: 'normal', // 当前时段类型: 'peak', 'off_peak', 'normal'
      weights: {
        distance: 1.0,
        time: 1.0,      // 滑行时间权重
        fuel: 0.5       // 燃料损耗权重
      },
      weightAdjustmentMode: 'auto', // 'auto' 或 'manual'
      peakThreshold: 0.6, // 高峰期阈值（密度百分比）
      timeWindowSize: 30, // 时间窗口大小（分钟）

      // Dashboard additions
      currentTime: '',
      computeTime: 0,
      showUploadModal: false,
      showSettingsPanel: false,
      systemStatus: 'online',
      timeTimer: null,
      startTime: null,
    }
  },
  computed: {
    allConflicts() {
      // 使用 Map 去重，key 为 "航班对+时间"（忽略具体节点，同一时间的多个节点合并显示）
      const conflictMap = new Map();

      this.schedules.forEach(schedule => {
        schedule.conflicts.forEach(conflict => {
          // 确保航班ID排序
          const sortedFlightIds = [...conflict.flight_ids].sort();
          // 提取时间的关键部分（忽略秒）
          let timeKey = conflict.time;
          if (typeof conflict.time === 'string' && conflict.time.includes(':')) {
            const parts = conflict.time.split(':');
            timeKey = `${parts[0]}:${parts[1]}`;
          }
          // 使用航班对+时间作为唯一键（同一时间的冲突合并）
          const uniqueKey = `${sortedFlightIds.join(',')}_${timeKey}`;

          if (!conflictMap.has(uniqueKey)) {
            // 创建新对象，不修改原始数据
            const normalizedConflict = {
              ...conflict,
              flight_ids: sortedFlightIds,
              node_ids: [conflict.node_id] // 存储所有冲突节点
            };
            conflictMap.set(uniqueKey, normalizedConflict);
          } else {
            // 已存在相同航班对和时间的冲突，添加节点ID到列表
            const existing = conflictMap.get(uniqueKey);
            if (!existing.node_ids.includes(conflict.node_id)) {
              existing.node_ids.push(conflict.node_id);
            }
            // 保留最高严重级别
            if (conflict.severity === 'high' || existing.severity === 'high') {
              existing.severity = 'high';
            } else if (conflict.severity === 'medium' && existing.severity !== 'high') {
              existing.severity = 'medium';
            }
          }
        });
      });

      return Array.from(conflictMap.values());
    },
    pieColors() {
      const stats = this.getOperationStats();
      if (!stats.length) return { departure: '#ff69b4', arrival: '#00f2fe' };
      const dep = stats.find(s => s.label === '离港');
      const arr = stats.find(s => s.label === '进港');
      return {
        departure: dep ? dep.color : '#ff69b4',
        arrival: arr ? arr.color : '#00f2fe'
      };
    },
  },

  methods: {
    goBack() {
      this.$router.push('/');
    },

    switchTab(tab) {
      this.activeTab = tab;
      if (tab === 'single') {
        this.$nextTick(() => {
          if (this.$refs.networkViz && this.nodes.length > 0) {
            this.$refs.networkViz.setNodes(this.nodes);
            this.$refs.networkViz.setEdges(this.edges);
          }
        });
      } else if (tab === 'multi') {
        this.$nextTick(() => {
          if (this.multiNodesLoaded) {
            this.drawMultiAircraftPaths();
          }
        });
      }
    },

    // ========== 单航班方法 ==========
    async loadDemo() {
      this.$refs.networkViz.setLoading(true);

      try {
        const response = await axios.get(`${API_BASE}/nodes`);

        if (response.data.success) {
          this.nodes = response.data.nodes;
          this.edges = response.data.edges || [];

          this.$refs.networkViz.setNodes(this.nodes);
          this.$refs.networkViz.setEdges(this.edges);
          this.$refs.networkViz.setLoading(false);
        } else {
          this.$refs.networkViz.setError('API返回失败状态');
          this.$refs.networkViz.setLoading(false);
        }
      } catch (err) {
        this.$refs.networkViz.setError('加载路网数据失败: ' + err.message);
        this.$refs.networkViz.setLoading(false);
        console.error('Load error:', err);
      }
    },

    async runFarthestStand() {
      this.$refs.networkViz.setLoading(true);
      this.$refs.networkViz.resetPath();

      try {
        const demoResponse = await axios.get(`${API_BASE}/demo/farthest-stand`);

        if (!demoResponse.data.success) {
          throw new Error(demoResponse.data.error);
        }

        const { start_node, goal_node } = demoResponse.data;

        const pathResponse = await axios.post(`${API_BASE}/path`, {
          start_node_id: start_node.id,
          goal_node_id: goal_node.id
        });

        if (pathResponse.data.success) {
          const path = pathResponse.data.path;
          const stats = pathResponse.data.stats;

          if (this.nodes.length === 0) {
            await this.loadDemo();
          }

          this.$refs.networkViz.setPath(path, stats);
        } else {
          this.$refs.networkViz.setError('未找到路径: ' + pathResponse.data.error);
          this.$refs.networkViz.setLoading(false);
        }
      } catch (err) {
        this.$refs.networkViz.setError('计算路径失败: ' + err.message);
        this.$refs.networkViz.setLoading(false);
        console.error('Run farthest stand error:', err);
      }
    },

    async runStandToRunway() {
      this.$refs.networkViz.setLoading(true);
      this.$refs.networkViz.resetPath();

      try {
        const demoResponse = await axios.get(`${API_BASE}/demo/stand-to-runway`);

        if (!demoResponse.data.success) {
          throw new Error(demoResponse.data.error);
        }

        const { start_node, goal_node } = demoResponse.data;

        const pathResponse = await axios.post(`${API_BASE}/path`, {
          start_node_id: start_node.id,
          goal_node_id: goal_node.id
        });

        if (pathResponse.data.success) {
          const path = pathResponse.data.path;
          const stats = pathResponse.data.stats;

          if (this.nodes.length === 0) {
            await this.loadDemo();
          }

          this.$refs.networkViz.setPath(path, stats);
        } else {
          this.$refs.networkViz.setError('未找到路径: ' + pathResponse.data.error);
          this.$refs.networkViz.setLoading(false);
        }
      } catch (err) {
        this.$refs.networkViz.setError('计算路径失败: ' + err.message);
        this.$refs.networkViz.setLoading(false);
        console.error('Run stand to runway error:', err);
      }
    },

    handleDisplayToggled(showCoreOnly) {
      console.log('Display toggled:', showCoreOnly ? '只显示机位' : '显示机位+跑道点+观察点');
    },

    async calculateCustomPath(startNode, goalNode) {
      if (!startNode || !goalNode) {
        return;
      }

      this.$refs.networkViz.setLoading(true);
      this.$refs.networkViz.resetPath();

      try {
        const pathResponse = await axios.post(`${API_BASE}/path`, {
          start_node_id: startNode.id,
          goal_node_id: goalNode.id
        });

        if (pathResponse.data.success) {
          const path = pathResponse.data.path;
          const stats = pathResponse.data.stats;

          this.$refs.networkViz.setPath(path, stats);
        } else {
          this.$refs.networkViz.setError('未找到路径: ' + pathResponse.data.error);
          this.$refs.networkViz.setLoading(false);
        }
      } catch (err) {
        this.$refs.networkViz.setError('计算路径失败: ' + err.message);
        this.$refs.networkViz.setLoading(false);
        console.error('Calculate custom path error:', err);
      }
    },

    // ========== 多航班方法 ==========
    switchDataSource(source) {
      this.dataSource = source;
      if (source === 'random') {
        this.selectedFile = null;
        this.uploadError = '';
      }
    },

    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
        this.uploadError = '';
      }
    },

    async extractFlightsFromExcel() {
      if (!this.selectedFile) {
        this.uploadError = '请先选择一个Excel文件';
        return;
      }

      try {
        this.isScheduling = true;
        this.uploadError = '';
        this.resetMultiResults();

        // 读取Excel文件
        const data = await this.selectedFile.arrayBuffer();
        const workbook = XLSX.read(data);
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];

        // 转换为JSON
        const jsonData = XLSX.utils.sheet_to_json(worksheet);

        if (!jsonData || jsonData.length === 0) {
          throw new Error('Excel文件为空或格式不正确');
        }

        // 验证并转换数据
        const validatedFlights = [];
        const errors = [];

        jsonData.forEach((row, index) => {
          try {
            // 验证必填字段
            const requiredFields = ['flight_id', 'aircraft_type', 'operation', 'scheduled_time', 'start_node_id', 'end_node_id', 'priority'];
            const missingFields = requiredFields.filter(field => !Object.prototype.hasOwnProperty.call(row, field) || row[field] === undefined || row[field] === '');

            if (missingFields.length > 0) {
              errors.push(`第${index + 2}行: 缺少字段 ${missingFields.join(', ')}`);
              return;
            }

            // 验证operation字段
            if (!['departure', 'arrival'].includes(row.operation)) {
              errors.push(`第${index + 2}行: operation必须是'departure'或'arrival'`);
              return;
            }

            // 验证节点ID
            const startNodeId = parseInt(row.start_node_id);
            const endNodeId = parseInt(row.end_node_id);

            if (isNaN(startNodeId) || isNaN(endNodeId)) {
              errors.push(`第${index + 2}行: 节点ID必须是数字`);
              return;
            }

            // 验证优先级
            const priority = parseInt(row.priority);
            if (isNaN(priority) || priority < 1 || priority > 10) {
              errors.push(`第${index + 2}行: 优先级必须是1-10之间的数字`);
              return;
            }

            // 验证时间格式
            const scheduledTime = new Date(row.scheduled_time);
            if (isNaN(scheduledTime.getTime())) {
              errors.push(`第${index + 2}行: 时间格式不正确，应为 YYYY-MM-DD HH:MM:SS`);
              return;
            }

            // 直接使用原始时间字符串，避免时区转换
            const originalTimeString = String(row.scheduled_time).trim();

            // 添加到验证通过的航班列表
            validatedFlights.push({
              flight_id: String(row.flight_id).trim(),
              aircraft_type: String(row.aircraft_type).trim(),
              operation: row.operation.trim(),
              scheduled_time: originalTimeString,
              start_node_id: startNodeId,
              end_node_id: endNodeId,
              priority: priority
            });
          } catch (err) {
            errors.push(`第${index + 2}行: ${err.message}`);
          }
        });

        if (errors.length > 0) {
          this.uploadError = `数据验证失败：\n${errors.slice(0, 5).join('\n')}${errors.length > 5 ? '\n...' : ''}`;
          return;
        }

        if (validatedFlights.length === 0) {
          throw new Error('没有有效的航班数据');
        }

        // 成功提取航班信息
        this.flights = validatedFlights;
        this.uploadError = '';

        // 显示成功消息
        ElMessage.success({
          message: `成功提取 ${validatedFlights.length} 条航班信息！`,
          duration: 3000,
          showClose: true
        });

      } catch (error) {
        console.error('提取航班信息失败:', error);
        this.uploadError = `提取失败: ${error.message}`;
      } finally {
        this.isScheduling = false;
      }
    },

    validateFlightCount() {
      const value = this.flightCount;
      if (value === '' || value === null || value === undefined) {
        this.flightCountError = '';
        return;
      }
      if (!Number.isInteger(value)) {
        this.flightCountError = '请输入10-200的整数';
        return;
      }
      if (value < 10 || value > 200) {
        this.flightCountError = '请输入10-200的整数';
        return;
      }
      this.flightCountError = '';
    },

    async generateFlights() {
      // 生成前再次验证
      this.validateFlightCount();
      if (this.flightCountError) {
        return;
      }
      try {
        this.isScheduling = true;
        this.resetMultiResults();

        const response = await axios.post(`${API_BASE}/multi-aircraft/generate-simulation`, {
          num_flights: parseInt(this.flightCount),
          base_time: '2024-01-20 14:00:00'
        });

        if (response.data.success) {
          this.flights = response.data.flights;
          // 分析航班密度
          await this.analyzeFlightDensity();
        }
      } catch (error) {
        console.error('生成航班失败:', error);
        ElMessage.error({
          message: '生成航班失败: ' + error.message,
          duration: 5000,
          showClose: true
        });
      } finally {
        this.isScheduling = false;
      }
    },

    async scheduleFlights() {
      try {
        this.isScheduling = true;

        // 先加载路网数据（如果还没有加载）
        if (!this.multiNodesLoaded) {
          await this.loadMultiNetwork();
        }

        const response = await axios.post(`${API_BASE}/multi-aircraft/schedule`, {
          strategy: this.strategy,
          flights: this.flights
        });

        if (response.data.success) {
          this.schedules = response.data.schedules;
          this.statistics = {
            flight_count: response.data.flight_count,
            total_distance: response.data.total_distance,
            total_time: response.data.total_time,
            total_delay: response.data.total_delay,
            total_conflicts: response.data.total_conflicts
          };

          // 自动选中所有航班
          this.selectedFlightIds = this.flights.map(f => f.flight_id);
          this.manuallyCleared = false; // 重置手动清除标记

          this.$nextTick(() => {
            this.drawMultiAircraftPaths();
          });
        }
      } catch (error) {
        console.error('调度失败:', error);
        ElMessage.error({
          message: '调度失败: ' + error.message,
          duration: 5000,
          showClose: true
        });
      } finally {
        this.isScheduling = false;
      }
    },

    resetMulti() {
      this.flights = [];
      this.schedules = [];
      this.statistics = null;
      this.selectedFlightIds = [];  // 清空选择状态
      this.manuallyCleared = false;  // 重置手动清除标记

      // 重置时段分析
      this.currentPeriodType = 'normal';
      this.flightDensity = null;
      this.peakPeriods = [];
      this.offPeakPeriods = [];
      this.timePeriodAnalysis = null;

      // 重置缩放和平移
      this.multiZoomLevel = 1.0;
      this.multiPanOffset = { x: 0, y: 0 };

      const canvas = this.$refs.multiCanvas;
      if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    },

    resetMultiResults() {
      this.schedules = [];
      this.statistics = null;
      this.selectedFlightIds = [];  // 清空选择状态
      this.manuallyCleared = false;  // 重置手动清除标记
    },

    async loadMultiNetwork() {
      try {
        const response = await axios.get(`${API_BASE}/nodes`);
        if (response.data.success) {
          this.multiNodes = response.data.nodes;
          this.multiEdges = response.data.edges || [];
          this.multiNodesLoaded = true;
        }
      } catch (error) {
        console.error('加载路网失败:', error);
      }
    },

    toggleMultiDisplay() {
      this.showCoreNodesOnly = !this.showCoreNodesOnly;
      this.drawMultiAircraftPaths();
    },

    drawMultiAircraftPaths(skipPreview = false) {
      const canvas = this.$refs.multiCanvas;
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      this.multiCtx = ctx;
      this.multiCanvas = canvas;

      // 清空画布
      ctx.fillStyle = '#0a1428';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 如果有路网数据，先绘制路网
      if (this.multiNodes.length > 0) {
        this.drawMultiNetwork();
      }

      // 如果有调度结果，绘制路径
      if (this.schedules.length > 0) {
        this.drawMultiFlightPaths();
      }

      // 如果正在预览路径，重绘预览路径（skipPreview 用于避免 drawPreviewPath 内部调用时的递归）
      if (!skipPreview && this.isPreviewingPath && this.previewPathData) {
        this.$nextTick(() => {
          try {
            if (this.isPreviewingPath && this.previewPathData) {
              this.drawPreviewPath(this.previewPathData);
            }
          } catch (err) {
            console.error('预览路径重绘失败:', err);
          }
        });
      }
    },

    drawMultiNetwork() {
      const ctx = this.multiCtx;
      const canvas = this.multiCanvas;

      // 计算坐标范围
      const xCoords = this.multiNodes.map(n => n.x);
      const yCoords = this.multiNodes.map(n => n.y);
      const minX = Math.min(...xCoords);
      const maxX = Math.max(...xCoords);
      const minY = Math.min(...yCoords);
      const maxY = Math.max(...yCoords);

      // 基础缩放和偏移
      const padding = 50;
      const scaleX = (canvas.width - 2 * padding) / (maxX - minX);
      const scaleY = (canvas.height - 2 * padding) / (maxY - minY);
      this.multiBaseScale = Math.min(scaleX, scaleY);

      this.multiBaseOffsetX = padding + (canvas.width - 2 * padding - (maxX - minX) * this.multiBaseScale) / 2 - minX * this.multiBaseScale;
      this.multiBaseOffsetY = padding + (canvas.height - 2 * padding - (maxY - minY) * this.multiBaseScale) / 2 - minY * this.multiBaseScale;

      // 保存转换函数（支持缩放和平移）
      this.multiTransform = (x, y) => {
        const scaledX = x * this.multiBaseScale + this.multiBaseOffsetX;
        const scaledY = canvas.height - (y * this.multiBaseScale + this.multiBaseOffsetY);

        // 应用用户缩放和平移
        return {
          x: (scaledX - canvas.width / 2) * this.multiZoomLevel + this.multiPanOffset.x + canvas.width / 2,
          y: (scaledY - canvas.height / 2) * this.multiZoomLevel + this.multiPanOffset.y + canvas.height / 2
        };
      };

      // 绘制边
      const edgeStyles = {
        'AircraftRoad': { color: 'rgba(79, 172, 254, 0.3)', width: 2 },
        'NetworkRoad': { color: 'rgba(156, 39, 176, 0.25)', width: 1.5 },
        'ServiceVehicleRoad': { color: 'rgba(255, 193, 7, 0.2)', width: 1 },
        'PerimeterRoad': { color: 'rgba(96, 125, 139, 0.25)', width: 1 },
        'ExternalRoad': { color: 'rgba(255, 87, 34, 0.2)', width: 1.2 },
        'PROXIMITY': { color: 'rgba(76, 175, 80, 0.15)', width: 1 }
      };

      const drawnEdges = new Set();
      this.multiEdges.forEach(edge => {
        const edgeKey = `${Math.min(edge.from_node_id, edge.to_node_id)}-${Math.max(edge.from_node_id, edge.to_node_id)}`;
        if (drawnEdges.has(edgeKey)) return;
        drawnEdges.add(edgeKey);

        const startPos = this.multiTransform(edge.from_x, edge.from_y);
        const endPos = this.multiTransform(edge.to_x, edge.to_y);

        const style = edgeStyles[edge.type] || { color: 'rgba(255, 255, 255, 0.1)', width: 1 };

        ctx.beginPath();
        ctx.moveTo(startPos.x, startPos.y);
        ctx.lineTo(endPos.x, endPos.y);
        ctx.strokeStyle = style.color;
        ctx.lineWidth = style.width * Math.max(0.5, Math.min(1.5, this.multiZoomLevel));
        ctx.stroke();
      });

      // 绘制节点
      this.multiNodes.forEach(node => {
        let shouldDraw = false;

        if (this.showCoreNodesOnly) {
          shouldDraw = node.type.includes('Stand');
        } else {
          shouldDraw = node.type.includes('Stand') ||
                      node.type.includes('Runway') ||
                      node.type.includes('Observation');
        }

        if (!shouldDraw) return;

        const pos = this.multiTransform(node.x, node.y);

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

        const adjustedSize = size * Math.max(0.5, Math.min(2, this.multiZoomLevel));

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, adjustedSize, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
      });
    },

    drawMultiFlightPaths() {
      if (!this.multiTransform) return;

      const ctx = this.multiCtx;

      // 离港颜色（粉色系）
      const departureColors = [
        '#ff69b4', '#ff1493', '#db7093', '#ff7f9e',
        '#ff6b9d', '#ff4081', '#f50057', '#e91e63'
      ];

      // 进港颜色（蓝色系）
      const arrivalColors = [
        '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
        '#30cfd0', '#00bcd4', '#03a9f4', '#2196f3'
      ];

      // 确定要显示的航班
      let schedulesToDraw;
      if (this.selectedFlightIds.length === 0) {
        // 空选择时：用户主动清空则不显示；默认状态（调度刚完成）显示全部
        schedulesToDraw = this.manuallyCleared ? [] : this.schedules;
      } else {
        schedulesToDraw = this.schedules.filter(s => this.selectedFlightIds.includes(s.flight_id));
      }

      // 绘制路径
      schedulesToDraw.forEach((schedule) => {
        // 跳过没有路径数据的航班
        if (!schedule.path || schedule.path.length === 0) return;

        // 根据operation类型选择颜色
        const operation = schedule.operation || 'departure'; // 默认为departure
        const colorList = operation === 'departure' ? departureColors : arrivalColors;
        const colorIndex = this.schedules.filter(s =>
          (s.operation || 'departure') === operation
        ).indexOf(schedule);
        const color = colorList[colorIndex % colorList.length];
        schedule.color = color;

        ctx.strokeStyle = color;
        ctx.lineWidth = 3 * Math.max(0.5, Math.min(1.5, this.multiZoomLevel));
        ctx.setLineDash([8, 4]);

        ctx.beginPath();
        schedule.path.forEach((point, i) => {
          const pos = this.multiTransform(point.x, point.y);
          if (i === 0) {
            ctx.moveTo(pos.x, pos.y);
          } else {
            ctx.lineTo(pos.x, pos.y);
          }
        });
        ctx.stroke();
        ctx.setLineDash([]);

        // 起点圆点
        const startPos = this.multiTransform(schedule.path[0].x, schedule.path[0].y);
        const startSize = Math.max(3, Math.min(8, 4 * Math.sqrt(this.multiZoomLevel)));
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(startPos.x, startPos.y, startSize, 0, Math.PI * 2);
        ctx.fill();

        // 终点圆圈
        const endPos = this.multiTransform(
          schedule.path[schedule.path.length - 1].x,
          schedule.path[schedule.path.length - 1].y
        );
        const endSize = Math.max(3, Math.min(8, 4 * Math.sqrt(this.multiZoomLevel)));
        ctx.strokeStyle = color;
        ctx.lineWidth = Math.max(1, Math.min(3, 1.5 * Math.sqrt(this.multiZoomLevel)));
        ctx.beginPath();
        ctx.arc(endPos.x, endPos.y, endSize, 0, Math.PI * 2);
        ctx.stroke();

        // 航班ID标签
        ctx.fillStyle = '#ffffff';
        const fontSize = Math.max(8, Math.min(16, 8 * Math.sqrt(this.multiZoomLevel)));
        ctx.font = 'bold ' + fontSize + 'px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        // 将标签显示在起点圆点的正上方
        ctx.fillText(schedule.flight_id, startPos.x, startPos.y - startSize - fontSize * 0.5);
      });

      // 绘制冲突点（只绘制选中航班的冲突）
      let conflictsToDraw;
      if (this.selectedFlightIds.length === 0) {
        conflictsToDraw = this.manuallyCleared ? [] : this.allConflicts;
      } else {
        conflictsToDraw = this.allConflicts.filter(conflict =>
          conflict.flight_ids.some(id => this.selectedFlightIds.includes(id))
        );
      }

      // 清空冲突点位置缓存
      this.conflictPointPositions = [];

      conflictsToDraw.forEach(conflict => {
        // 获取该冲突涉及的所有节点ID（支持合并后的多节点冲突）
        const nodeIds = conflict.node_ids || [conflict.node_id];

        // 统一只绘制第一个节点的冲突点（代表整个冲突）
        const firstNodeId = nodeIds[0];
        const schedule = this.schedules.find(s =>
          s.path.some(p => p.id === firstNodeId)
        );

        if (schedule) {
          const point = schedule.path.find(p => p.id === firstNodeId);
          if (point) {
            const pos = this.multiTransform(point.x, point.y);

            // 计算冲突点大小（更大更显眼）
            const baseSize = conflict.severity === 'high' ? 12 : 10;
            const conflictSize = Math.max(6, Math.min(20, baseSize * Math.sqrt(this.multiZoomLevel)));

            // 外层红色/橙色光晕（更大范围）
            const outerGradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, conflictSize * 2.5);
            const mainColor = conflict.severity === 'high' ? '255, 0, 0' : '255, 140, 0';
            outerGradient.addColorStop(0, `rgba(${mainColor}, 0.8)`);
            outerGradient.addColorStop(0.4, `rgba(${mainColor}, 0.4)`);
            outerGradient.addColorStop(1, `rgba(${mainColor}, 0)`);
            ctx.fillStyle = outerGradient;
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, conflictSize * 2.5, 0, Math.PI * 2);
            ctx.fill();

            // 内层实心圆（告警色）
            ctx.fillStyle = conflict.severity === 'high' ? '#ff0000' : '#ff8c00';
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, conflictSize, 0, Math.PI * 2);
            ctx.fill();

            // 深红色边框（代替白色，更显眼）
            ctx.strokeStyle = conflict.severity === 'high' ? '#8b0000' : '#cc5500';
            ctx.lineWidth = Math.max(2, 2 * Math.sqrt(this.multiZoomLevel));
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, conflictSize, 0, Math.PI * 2);
            ctx.stroke();

            // 中心感叹号（白色但更大更粗）
            ctx.fillStyle = '#ffffff';
            const alertSize = Math.max(10, Math.min(16, 12 * Math.sqrt(this.multiZoomLevel)));
            ctx.font = 'bold ' + alertSize + 'px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            // 添加文字阴影增强可读性
            ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
            ctx.shadowBlur = 2;
            ctx.fillText('!', pos.x, pos.y);
            // 重置阴影
            ctx.shadowColor = 'transparent';
            ctx.shadowBlur = 0;

            // 记录冲突点位置信息，用于鼠标悬浮检测
            this.conflictPointPositions.push({
              x: pos.x,
              y: pos.y,
              size: conflictSize,
              conflict: conflict
            });
          }
        }
      });
    },

    // 多航班画布缩放和平移事件处理
    handleMultiWheel(event) {
      event.preventDefault();
      const delta = event.deltaY > 0 ? -0.1 : 0.1;
      const newZoomLevel = Math.max(0.1, Math.min(15, this.multiZoomLevel + delta));

      if (newZoomLevel !== this.multiZoomLevel) {
        this.multiZoomLevel = newZoomLevel;
        this.drawMultiAircraftPaths();
      }
    },

    handleMultiMouseDown(event) {
      this.multiIsDragging = true;
      this.multiDragStart = {
        x: event.clientX,
        y: event.clientY
      };
      this.multiCanvas.style.cursor = 'grabbing';
    },

    handleMultiMouseMove(event) {
      // 如果正在拖拽，处理拖拽逻辑
      if (this.multiIsDragging) {
        const dx = event.clientX - this.multiDragStart.x;
        const dy = event.clientY - this.multiDragStart.y;

        this.multiPanOffset.x += dx;
        this.multiPanOffset.y += dy;

        this.multiDragStart = {
          x: event.clientX,
          y: event.clientY
        };

        this.drawMultiAircraftPaths();
        return;
      }
      
      // 检测鼠标是否悬浮在冲突点上
      this.checkConflictHover(event);
    },
    
    checkConflictHover(event) {
      const canvas = this.$refs.multiCanvas;
      if (!canvas || !this.schedules.length || this.conflictPointPositions.length === 0) {
        this.conflictTooltip.show = false;
        if (canvas) canvas.style.cursor = this.multiIsDragging ? 'grabbing' : 'grab';
        return;
      }

      this.multiCanvas = canvas;
      const rect = canvas.getBoundingClientRect();

      // === 关键修复：考虑画布显示尺寸与内部像素尺寸的比例 ===
      // 画布内部尺寸
      const internalWidth = canvas.width;
      const internalHeight = canvas.height;
      // 画布显示尺寸
      const displayWidth = rect.width;
      const displayHeight = rect.height;
      // 缩放比例
      const scaleX = internalWidth / displayWidth;
      const scaleY = internalHeight / displayHeight;

      // 将鼠标坐标转换为内部像素坐标
      const mouseX = (event.clientX - rect.left) * scaleX;
      const mouseY = (event.clientY - rect.top) * scaleY;

      // 精确检测：遍历所有缓存的冲突点
      let hoveredConflict = null;
      let conflictPos = null;

      for (const pointInfo of this.conflictPointPositions) {
        const dx = mouseX - pointInfo.x;
        const dy = mouseY - pointInfo.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // 只有当鼠标在内层实心圆内才触发
        if (distance <= pointInfo.size) {
          hoveredConflict = pointInfo.conflict;
          conflictPos = { x: pointInfo.x / scaleX, y: pointInfo.y / scaleY }; // 转回显示坐标用于提示位置
          break;
        }
      }

      if (hoveredConflict && conflictPos) {
        this.conflictTooltip = {
          show: true,
          x: conflictPos.x + 15,
          y: conflictPos.y - 10,
          conflict: hoveredConflict
        };
        canvas.style.cursor = 'pointer';
      } else {
        this.conflictTooltip.show = false;
        canvas.style.cursor = this.multiIsDragging ? 'grabbing' : 'grab';
      }
    },

    handleMultiMouseUp() {
      this.multiIsDragging = false;
      if (this.multiCanvas) {
        this.multiCanvas.style.cursor = 'grab';
      }
    },
    
    multiZoomIn() {
      this.multiZoomLevel = Math.min(15, this.multiZoomLevel + 0.2);
      this.drawMultiAircraftPaths();
    },

    multiZoomOut() {
      this.multiZoomLevel = Math.max(0.1, this.multiZoomLevel - 0.2);
      this.drawMultiAircraftPaths();
    },

    multiResetView() {
      this.multiZoomLevel = 1.0;
      this.multiPanOffset = { x: 0, y: 0 };
      this.drawMultiAircraftPaths();
    },

    getScheduleResult(flightId) {
      return this.schedules.find(s => s.flight_id === flightId);
    },

    getFlightStatusClass(flight) {
      const schedule = this.getScheduleResult(flight.flight_id);
      if (!schedule) return '';
      if (schedule.conflict_count > 0) return 'has-conflict';
      if (schedule.delay > 0) return 'has-delay';
      return 'success';
    },

    formatTime(timeStr) {
      if (!timeStr) return '-';
      const date = new Date(timeStr);
      return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    },
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '-';
      const date = new Date(dateTimeStr);
      return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    },

    getConflictTypeText(type) {
      const map = {
        'node': '节点冲突',
        'edge': '边冲突',
        'crossing': '交叉冲突'
      };
      return map[type] || type;
    },

    // ========== 航班选择相关方法 ==========
    toggleFlightSelection(flightId) {
      // 只有在调度完成后才能选择
      if (!this.schedules.length) return;

      const index = this.selectedFlightIds.indexOf(flightId);
      if (index > -1) {
        // 取消选择
        this.selectedFlightIds.splice(index, 1);
      } else {
        // 添加选择
        this.selectedFlightIds.push(flightId);
      }

      // 重新绘制画布
      this.drawMultiAircraftPaths();
    },

    toggleSelectAll() {
      if (this.selectedFlightIds.length === this.flights.length) {
        // 取消全选
        this.selectedFlightIds = [];
        this.manuallyCleared = true; // 标记为手动清除
      } else {
        // 全选
        this.selectedFlightIds = this.flights.map(f => f.flight_id);
        this.manuallyCleared = false;
      }

      // 重新绘制画布
      this.drawMultiAircraftPaths();
    },

    clearSelection() {
      this.selectedFlightIds = [];
      this.manuallyCleared = true; // 标记为手动清除
      // 重新绘制画布
      this.drawMultiAircraftPaths();
    },

    // 点击告警信息，选中冲突航班
    selectConflictFlights(conflict) {
      if (!conflict || !conflict.flight_ids || conflict.flight_ids.length === 0) return;
      // 清空当前选中，只选中冲突涉及的航班
      this.selectedFlightIds = [...conflict.flight_ids];
      this.manuallyCleared = false;
      // 重新绘制画布
      this.drawMultiAircraftPaths();
    },

    // ========== 备选路径相关方法 ==========
    async showPathAlternatives(flight) {
      this.selectedFlight = flight;
      this.showPathAlternativesPanel = true;
      this.loadingAlternatives = true;
      this.pathAlternatives = [];
      this.activePathId = 'path_1';
      // 重置预览状态，避免切换航班时残留旧预览
      this.isPreviewingPath = false;
      this.previewPathData = null;

      try {
        const schedule = this.getScheduleResult(flight.flight_id);
        if (!schedule) {
          ElMessage.warning('该航班尚未调度');
          this.loadingAlternatives = false;
          return;
        }

        // 保存原始路径数据
        this.originalPathData = {
          path_id: 'path_original',
          nodes: schedule.path,
          distance: schedule.total_distance,
          time: schedule.total_time
        };

        // 调用API获取备选路径
        const response = await axios.post(`${API_BASE}/path/alternatives`, {
          start_node_id: flight.start_node_id,
          goal_node_id: flight.end_node_id,
          k: 3
        });

        if (response.data.success) {
          // 获取当前航班的冲突节点
          const schedule = this.getScheduleResult(flight.flight_id);
          const conflictNodeIds = new Set();
          if (schedule && schedule.conflicts) {
            schedule.conflicts.forEach(c => conflictNodeIds.add(c.node_id));
          }
          
          // 过滤备选路径：只保留能避开所有冲突节点的路径
          let filteredPaths = response.data.paths.filter(path => {
            const pathNodeIds = path.nodes.map(n => n.id);
            // 检查路径是否避开了所有冲突节点
            for (const conflictNodeId of conflictNodeIds) {
              if (pathNodeIds.includes(conflictNodeId)) {
                return false; // 路径仍经过冲突节点，过滤掉
              }
            }
            return true; // 路径避开了所有冲突节点，保留
          });
          
          // 如果没有可用的备选路径，显示提示
          if (filteredPaths.length === 0 && conflictNodeIds.size > 0) {
            ElMessage.warning({
              message: '未找到能完全避开冲突节点的备选路径，建议调整航班起飞时间',
              duration: 5000,
              showClose: true
            });
          }
          
          // 重新编号：原始路径为1，备选路径从2开始连续编号
          this.pathAlternatives = [
            // 将当前路径添加到列表中作为第一条
            {
              path_id: 'path_original',
              nodes: schedule.path.map(node => ({
                id: node.id,
                type: node.type || 'Node',
                x: node.x,
                y: node.y
              })),
              distance: schedule.total_distance,
              time: schedule.total_time,
              fuel: 0,
              num_nodes: schedule.path.length,
              rank: 1,
              differences_from_best: { distance: 0, time: 0, fuel: 0 },
              is_original: true,
              has_conflict: schedule.conflicts && schedule.conflicts.length > 0,
              disabled: false
            },
            // 过滤后的备选路径从2开始编号
            ...filteredPaths.map((path, index) => ({
              ...path,
              rank: index + 2,
              has_conflict: false,
              disabled: false
            }))
          ];
          this.activePathId = 'path_original';
        } else {
          ElMessage.error('获取备选路径失败: ' + response.data.error);
        }
      } catch (error) {
        console.error('获取备选路径失败:', error);
        ElMessage.error('获取备选路径失败: ' + error.message);
      } finally {
        this.loadingAlternatives = false;
      }
    },

    closePathAlternatives() {
      this.showPathAlternativesPanel = false;
      this.selectedFlight = null;
      this.pathAlternatives = [];
      this.activePathId = 'path_1';
      // 取消预览状态
      this.isPreviewingPath = false;
      this.previewPathData = null;
      // 重绘画布
      this.drawMultiAircraftPaths();
    },

    selectAlternativePath(altPath) {
      this.activePathId = altPath.path_id;
      // 自动应用选择的路径，替换原路径
      this.applyAlternativePath(altPath);
    },

    togglePreview(altPath) {
      if (this.isPreviewingPath && this.previewPathData && this.previewPathData.path_id === altPath.path_id) {
        this.cancelPreview();
      } else {
        this.previewPath(altPath);
      }
    },

    async previewPath(altPath) {
      // 预览选中的路径（在画布中高亮显示）
      try {
        // 如果正在预览其他路径，先取消之前的预览
        if (this.isPreviewingPath && this.previewPathData && this.previewPathData.path_id !== altPath.path_id) {
          this.isPreviewingPath = false;
          this.previewPathData = null;
        }

        // 保存预览状态和数据
        this.isPreviewingPath = true;
        this.previewPathData = altPath;

        // 绘制预览路径
        this.drawPreviewPath(altPath);
        ElMessage.success(`正在预览路径${altPath.rank || '原始'}`);
      } catch (error) {
        console.error('预览路径失败:', error);
        ElMessage.error('预览路径失败');
        // 预览失败时重置状态
        this.isPreviewingPath = false;
        this.previewPathData = null;
      }
    },

    drawPreviewPath(altPath) {
      if (!this.multiTransform || !altPath || !altPath.nodes) return;

      // 先清空画布并重绘基础状态，避免旧预览路径残留（传 true 防止递归调用）
      this.drawMultiAircraftPaths(true);

      const ctx = this.multiCtx;

      // 再重绘所有已选择的航班路径（半透明）
      let schedulesToDraw;
      if (this.selectedFlightIds.length === 0) {
        schedulesToDraw = this.manuallyCleared ? [] : this.schedules;
      } else {
        schedulesToDraw = this.schedules.filter(s => this.selectedFlightIds.includes(s.flight_id));
      }

      const currentFlightId = this.selectedFlight ? this.selectedFlight.flight_id : null;
      schedulesToDraw.forEach((schedule) => {
        if (currentFlightId && schedule.flight_id === currentFlightId) {
          // 当前查看的航班，用半透明显示
          this.drawPath(ctx, schedule.path, 'rgba(79, 172, 254, 0.2)', false);
        } else {
          // 其他航班正常显示
          this.drawPath(ctx, schedule.path, schedule.color, true);
        }
      });

      // 绘制预览路径（高亮）- 使用鲜艳的颜色
      const previewColor = altPath.path_id === 'path_original' ? '#00ff00' : '#ff00ff';
      this.drawPath(ctx, altPath.nodes, previewColor, false, true);
    },

    drawPath(ctx, path, color, dashed = false, thick = false) {
      if (!path || path.length === 0) return;

      ctx.strokeStyle = color;
      ctx.lineWidth = thick ? 5 : 3;
      ctx.setLineDash(dashed ? [8, 4] : []);

      ctx.beginPath();
      path.forEach((point, i) => {
        const pos = this.multiTransform(point.x, point.y);
        if (i === 0) {
          ctx.moveTo(pos.x, pos.y);
        } else {
          ctx.lineTo(pos.x, pos.y);
        }
      });
      ctx.stroke();
      ctx.setLineDash([]);

      // 绘制起点
      const startPos = this.multiTransform(path[0].x, path[0].y);
      const startSize = thick ? 6 : 4;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(startPos.x, startPos.y, startSize, 0, Math.PI * 2);
      ctx.fill();

      // 绘制终点
      const endPos = this.multiTransform(path[path.length - 1].x, path[path.length - 1].y);
      ctx.strokeStyle = color;
      ctx.lineWidth = thick ? 3 : 2;
      ctx.beginPath();
      ctx.arc(endPos.x, endPos.y, startSize, 0, Math.PI * 2);
      ctx.stroke();
    },

    cancelPreview() {
      // 取消预览，恢复正常显示
      this.isPreviewingPath = false;
      this.previewPathData = null;
      this.$nextTick(() => {
        this.drawMultiAircraftPaths();
      });
      ElMessage.info('已取消预览');
    },

    async applyAlternativePath(altPath) {
      // 应用选择的路径（更新调度结果）
      try {
        // 如果是原路径，不需要替换
        if (altPath.is_original) {
          ElMessage.info('这是当前正在使用的路径');
          return;
        }

        // 找到当前航班的调度结果
        const scheduleIndex = this.schedules.findIndex(s => s.flight_id === this.selectedFlight.flight_id);
        if (scheduleIndex === -1) {
          ElMessage.error('未找到航班调度信息');
          return;
        }

        const schedule = this.schedules[scheduleIndex];
        const scheduleConflicts = schedule.conflicts || [];
        
        // 获取当前航班的所有冲突节点
        const conflictNodeIds = new Set();
        scheduleConflicts.forEach(c => conflictNodeIds.add(c.node_id));
        
        // 检查新路径是否避开了所有冲突节点
        const newPathNodeIds = altPath.nodes.map(n => n.id);
        const stillHasConflicts = [];
        
        conflictNodeIds.forEach(nodeId => {
          if (newPathNodeIds.includes(nodeId)) {
            stillHasConflicts.push(nodeId);
          }
        });
        
        if (stillHasConflicts.length > 0) {
          ElMessage.warning({
            message: `该备选路径仍经过冲突节点（节点ID: ${stillHasConflicts.join(', ')}），无法消除冲突。请选择完全避开冲突节点的路径。`,
            duration: 5000,
            showClose: true
          });
          return;
        }

        // Vue 3 中直接赋值即可保持响应式
        const updatedSchedule = {
          ...schedule,
          path: altPath.nodes,
          total_distance: altPath.distance,
          total_time: altPath.time,
          conflicts: [],
          conflict_count: 0
        };
        this.schedules[scheduleIndex] = updatedSchedule;
        
        // 获取被解决的冲突节点
        const resolvedConflictNodes = new Set(scheduleConflicts.map(c => c.node_id));
        
        // 更新其他航班的冲突列表 - 移除涉及已解决冲突的条目
        this.schedules.forEach((otherSchedule, idx) => {
          if (otherSchedule.flight_id !== this.selectedFlight.flight_id) {
            const otherConflicts = otherSchedule.conflicts || [];
            const newConflicts = otherConflicts.filter(c => {
              // 如果冲突涉及当前航班且冲突节点已被解决，则移除
              const involvesCurrentFlight = c.flight_ids.includes(this.selectedFlight.flight_id);
              const isResolvedNode = resolvedConflictNodes.has(c.node_id);
              // 保留：不涉及当前航班 或 涉及但不是已解决的节点
              return !(involvesCurrentFlight && isResolvedNode);
            });
            if (newConflicts.length !== otherConflicts.length) {
              this.schedules[idx] = {
                ...otherSchedule,
                conflicts: newConflicts,
                conflict_count: newConflicts.length
              };
            }
          }
        });

        // 更新选中航班的路径
        this.selectedFlight.path = altPath.nodes;

        // 更新 pathAlternatives：新路径标记为当前，原始冲突路径禁用
        this.pathAlternatives = this.pathAlternatives.map(pa => ({
          ...pa,
          is_original: pa.path_id === altPath.path_id,
          disabled: pa.has_conflict && pa.path_id !== altPath.path_id
        }));

        // 更新 activePathId 为当前使用的路径
        this.activePathId = altPath.path_id;

        // 取消预览状态
        this.isPreviewingPath = false;
        this.previewPathData = null;

        // 强制更新视图，确保冲突列表和冲突点消失
        this.$forceUpdate();

        // 重新绘制所有路径（不包含已消解的冲突）
        this.$nextTick(() => {
          this.drawMultiAircraftPaths();

          // 更新统计数据中的冲突数（使用 allConflicts 计算属性的结果）
          if (this.statistics) {
            this.statistics.total_conflicts = this.allConflicts.length;
          }
        });

        // 关闭备选路径面板
        this.showPathAlternativesPanel = false;

        // 显示成功消息
        const diff = altPath.differences_from_best || { distance: 0, time: 0 };
        const distanceDiff = diff.distance || 0;
        const timeDiff = diff.time || 0;

        let message = '冲突已消解';
        message += `，已选择路径${altPath.rank}`;
        if (distanceDiff > 0) {
          message += `，绕行距离: ${distanceDiff.toFixed(0)}m`;
        }
        if (timeDiff > 0) {
          message += `，时间增加: ${(timeDiff / 60).toFixed(1)}分钟`;
        }

        ElMessage.success({
          message: message,
          duration: 5000,
          showClose: true
        });

      } catch (error) {
        console.error('应用路径失败:', error);
        ElMessage.error('应用路径失败');
      }
    },

    // ========== 航班密度分析和权重动态调整 ==========
    async analyzeFlightDensity() {
      if (!this.flights.length) {
        this.flightDensity = null;
        this.peakPeriods = [];
        this.offPeakPeriods = [];
        this.timePeriodAnalysis = null;
        return;
      }

      try {
        const response = await axios.post(`${API_BASE}/density/analyze`, {
          flights: this.flights,
          time_window_minutes: this.timeWindowSize,
          peak_threshold: this.peakThreshold
        });

        if (response.data.success) {
          this.flightDensity = response.data.analysis;
          this.peakPeriods = response.data.analysis.peak_windows;
          this.offPeakPeriods = response.data.analysis.off_peak_windows;
          this.timePeriodAnalysis = response.data.analysis;

          // 同时获取当前权重
          await this.updateCurrentWeights();
        }
      } catch (error) {
        console.error('航班密度分析失败:', error);
        ElMessage.error('航班密度分析失败: ' + error.message);
      }
    },

    async updateCurrentWeights(currentTime = null) {
      if (!this.flights.length) {
        this.weights = {
          distance: 1.0,
          time: 1.0,
          fuel: 0.5
        };
        this.currentPeriodType = 'normal';
        return;
      }

      try {
        const requestData = {
          flights: this.flights,
          time_window_minutes: this.timeWindowSize,
          peak_threshold: this.peakThreshold
        };

        if (currentTime) {
          requestData.current_time = currentTime;
        }

        const response = await axios.post(`${API_BASE}/density/current-weights`, requestData);

        if (response.data.success) {
          const weightInfo = response.data.weight_info;
          this.weights = weightInfo.weights;
          this.currentPeriodType = weightInfo.period_type;
          this.weightAdjustmentMode = 'auto';

          // 显示提示信息 - 根据不同时段显示不同颜色
          const messageConfig = {
            message: `当前时间段: ${weightInfo.description}`,
            duration: 3000,
            showClose: true
          };

          if (weightInfo.period_type === 'peak') {
            ElMessage.error(messageConfig); // 高峰期 - 红色
          } else if (weightInfo.period_type === 'normal') {
            ElMessage.warning(messageConfig); // 正常期 - 黄色
          } else {
            ElMessage.success(messageConfig); // 低峰期 - 绿色
          }
        }
      } catch (error) {
        console.error('获取当前权重失败:', error);
        ElMessage.error('获取当前权重失败: ' + error.message);
      }
    },

    // 手动调整权重
    adjustWeightsManually() {
      this.weightAdjustmentMode = 'manual';
      ElMessage.info('已切换到手动权重调整模式');
    },

    // 自动调整权重
    adjustWeightsAuto() {
      this.weightAdjustmentMode = 'auto';
      this.updateCurrentWeights();
    },

    // 更新权重参数

    // Dashboard helpers
    updateCurrentTime() {
      const now = new Date();
      this.currentTime = now.toLocaleString('zh-CN', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      });
    },
    startTimer() {
      this.updateCurrentTime();
      this.timeTimer = setInterval(() => {
        this.updateCurrentTime();
      }, 1000);
    },
    getSystemStatusText() {
      if (this.isScheduling) return '计算中';
      if (this.allConflicts.length > 0) return '有冲突';
      return '运行正常';
    },
    getSystemStatusClass() {
      if (this.isScheduling) return 'busy';
      if (this.allConflicts.length > 0) return 'warning';
      return 'online';
    },
    // Override scheduleFlights to track compute time
    async scheduleFlightsTracked() {
      const start = performance.now();
      await this.scheduleFlights();
      this.computeTime = Math.round(performance.now() - start);
    },
    // Pie chart data helpers
    getOperationStats() {
      if (!this.flights.length) return [];
      const dep = this.flights.filter(f => f.operation === 'departure').length;
      const arr = this.flights.filter(f => f.operation === 'arrival').length;
      return [
        { label: '离港', value: dep, color: '#ff69b4' },
        { label: '进港', value: arr, color: '#00f2fe' }
      ];
    },
    getConflictSeverityStats() {
      if (!this.allConflicts.length) return [];
      const high = this.allConflicts.filter(c => c.severity === 'high').length;
      const medium = this.allConflicts.filter(c => c.severity === 'medium').length;
      return [
        { label: '高危', value: high, color: '#f44336' },
        { label: '中危', value: medium, color: '#ff9800' }
      ];
    },
    getAircraftTypeStats() {
      if (!this.flights.length) return [];
      const map = {};
      this.flights.forEach(f => {
        map[f.aircraft_type] = (map[f.aircraft_type] || 0) + 1;
      });
      return Object.entries(map).map(([k, v]) => ({ label: k, value: v })).sort((a, b) => b.value - a.value);
    },
    updateWeightParams() {
      this.analyzeFlightDensity();
    }
  }
}
</script>
<style scoped>
/* ========== Base & Background ========== */
.dashboard {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #0a1428;
  color: #e0f7fa;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}
.grid-bg {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(79,172,254,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(79,172,254,0.06) 1px, transparent 1px);
  background-size: 30px 30px;
  pointer-events: none; z-index: 0;
}
.particles-bg {
  position: absolute; inset: 0;
  pointer-events: none; z-index: 0;
}
.particles-bg::after {
  content: "";
  position: absolute; inset: 0;
  background:
    radial-gradient(circle at 10% 20%, rgba(79,172,254,0.08) 0%, transparent 25%),
    radial-gradient(circle at 90% 80%, rgba(0,242,254,0.06) 0%, transparent 25%);
  animation: float 12s infinite linear;
}
@keyframes float {
  0% { transform: translate(0,0); }
  25% { transform: translate(4px,4px); }
  50% { transform: translate(0,4px); }
  75% { transform: translate(-4px,0); }
  100% { transform: translate(0,0); }
}

/* ========== Header ========== */
.dash-header {
  position: relative; z-index: 2;
  height: 60px;
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  align-items: center;
  padding: 0 20px;
  background: rgba(10,20,40,0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(79,172,254,0.25);
  box-shadow: 0 0 20px rgba(79,172,254,0.15);
}
.header-left { display: flex; align-items: center; gap: 12px; }
.logo { font-size: 28px; filter: drop-shadow(0 0 8px rgba(79,172,254,0.6)); }
.main-title {
  font-size: 20px; font-weight: 700; margin: 0;
  background: linear-gradient(90deg, #4facfe, #00f2fe);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  text-shadow: 0 0 12px rgba(79,172,254,0.4);
}
.sub-title { font-size: 11px; color: #8aa; margin: 2px 0 0; }
.header-center { display: flex; justify-content: center; }
.kpi-bar {
  display: flex; gap: 24px;
  background: rgba(0,0,0,0.25);
  border: 1px solid rgba(79,172,254,0.2);
  border-radius: 8px; padding: 6px 18px;
}
.kpi-item { text-align: center; }
.kpi-label { display: block; font-size: 11px; color: #8aa; }
.kpi-value {
  display: block; font-size: 22px; font-weight: 700; color: #4facfe;
  font-family: 'Courier New', monospace;
  text-shadow: 0 0 10px rgba(79,172,254,0.5);
}
.kpi-value small { font-size: 11px; color: #8aa; margin-left: 2px; }
.kpi-value.danger { color: #ff4d4f; text-shadow: 0 0 10px rgba(255,77,79,0.5); }
.header-right { display: flex; align-items: center; justify-content: flex-end; gap: 8px; white-space: nowrap; }
.live-badge {
  display: flex; align-items: center; gap: 6px;
  background: rgba(0,0,0,0.3); border-radius: 20px; padding: 4px 10px;
  font-size: 11px; font-weight: 700; color: #4ade80;
  border: 1px solid rgba(74,222,128,0.3);
}
.live-dot {
  width: 8px; height: 8px; border-radius: 50%; background: #4ade80;
  box-shadow: 0 0 8px #4ade80;
  animation: blink 1.5s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.clock { font-size: 12px; color: #c0d8e8; font-family: monospace; white-space: nowrap; }
.sys-status { width: 80px; height: 30px; font-size: 11px; padding: 3px 10px; border-radius: 4px; font-weight: 600; line-height: 21px; text-align: center;}
.sys-status.online { background: rgba(74,222,128,0.15); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
.sys-status.busy { background: rgba(79,172,254,0.15); color: #4facfe; border: 1px solid rgba(79,172,254,0.3); animation: pulse 1.2s infinite; }
.sys-status.warning { background: rgba(255,152,0,0.15); color: #ff9800; border: 1px solid rgba(255,152,0,0.3); }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }

/* ========== Tab Bar ========== */
.tab-bar {
  position: relative; z-index: 2;
  height: 40px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(10,20,40,0.7);
  border-bottom: 1px solid rgba(79,172,254,0.15);
}
.tab-pills {
  display: flex; gap: 8px;
  background: rgba(0,0,0,0.3); padding: 4px; border-radius: 20px;
  border: 1px solid rgba(79,172,254,0.15);
}
.tab-pills button {
  padding: 5px 20px; border: none; border-radius: 16px;
  background: transparent; color: #8aa; font-size: 13px; cursor: pointer;
  transition: all .3s;
}
.tab-pills button:hover { color: #e0f7fa; }
.tab-pills button.active {
  background: linear-gradient(90deg, #4facfe, #00f2fe);
  color: #fff; font-weight: 600;
  box-shadow: 0 0 12px rgba(79,172,254,0.4);
}

/* ========== Main Grid ========== */
.main-grid {
  position: relative; z-index: 1;
  flex: 1;
  display: grid;
  grid-template-columns: 18% 1fr 18%;
  gap: 10px;
  padding: 10px;
  min-height: 0;
}
.sidebar, .center-area { display: flex; flex-direction: column; gap: 10px; min-height: 0; }
.sidebar.left { padding-right: 0; }
.sidebar.right { padding-left: 0; }

/* ========== Panel ========== */
.panel {
  background: rgba(13,27,42,0.7);
  border: 1px solid rgba(79,172,254,0.2);
  border-radius: 10px;
  backdrop-filter: blur(8px);
  box-shadow: 0 0 20px rgba(79,172,254,0.08);
  display: flex; flex-direction: column;
  overflow: hidden;
}
.panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 12px;
  background: rgba(79,172,254,0.08);
  border-bottom: 1px solid rgba(79,172,254,0.15);
}
.panel-title {
  font-size: 13px; font-weight: 700; color: #4facfe;
  letter-spacing: 1px;
}
.panel-body {
  padding: 10px;
  flex: 1;
  overflow: auto;
}
.panel-body.compact { padding: 8px; }
.panel-body.center { display: flex; align-items: center; justify-content: center; }

/* Alarm panel specific */
.alarm-panel { flex: 1.5; }
.alarm-badge {
  font-size: 11px; padding: 2px 8px; border-radius: 10px; background: rgba(74,222,128,0.2); color: #4ade80;
}
.alarm-badge.danger { background: rgba(255,77,79,0.2); color: #ff4d4f; }
.alarm-list { display: flex; flex-direction: column; gap: 6px; }
.alarm-card {
  padding: 8px; border-radius: 6px;
  background: rgba(255,255,255,0.03);
  border-left: 3px solid rgba(79,172,254,0.4);
  font-size: 11px;
  cursor: pointer;
  transition: background .2s;
}
.alarm-card:hover { background: rgba(255,255,255,0.08); }
.alarm-card.high { border-left-color: #f44336; background: rgba(244,67,54,0.08); }
.alarm-card.medium { border-left-color: #ff9800; background: rgba(255,152,0,0.08); }
.alarm-row { display: flex; justify-content: space-between; margin-bottom: 3px; }
.alarm-type { font-weight: 700; }
.alarm-time { color: #8aa; }
.alarm-flights { color: #c0d8e8; }
.alarm-node { color: #8aa; }
.alarm-empty { text-align: center; color: #567; padding: 20px; font-size: 12px; }

/* Stats panel */
.stats-panel { flex: 1.2; }
.big-stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.big-stat {
  text-align: center; padding: 8px 4px;
  background: rgba(0,0,0,0.2); border-radius: 6px;
  border: 1px solid rgba(79,172,254,0.1);
}
.big-num {
  font-size: 20px; font-weight: 700; color: #4facfe;
  font-family: 'Courier New', monospace;
  text-shadow: 0 0 10px rgba(79,172,254,0.4);
}
.big-num.warn { color: #ff9800; text-shadow: 0 0 10px rgba(255,152,0,0.4); }
.big-label { font-size: 10px; color: #8aa; margin-top: 3px; }
.footer-stats { grid-template-columns: repeat(4, 1fr); gap: 10px; padding: 4px 0; }
.footer-stats .big-stat { padding: 6px 2px; }
.footer-stats .big-num { font-size: 18px; }

/* Period badge */
.period-badge {
  display: flex; align-items: center; gap: 10px;
  padding: 8px; border-radius: 6px; font-size: 12px;
  background: rgba(0,0,0,0.2); border: 1px solid rgba(79,172,254,0.15);
}
.period-badge .dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: #ff9800; box-shadow: 0 0 8px #ff9800;
  animation: blink 2s infinite;
}
.period-badge.peak .dot { background: #f44336; box-shadow: 0 0 8px #f44336; }
.period-badge.off_peak .dot { background: #4ade80; box-shadow: 0 0 8px #4ade80; }
.period-title { font-weight: 700; color: #e0f7fa; }
.period-sub { font-size: 10px; color: #8aa; }
.density-bar-wrap { margin-top: 8px; }
.density-label { display: flex; justify-content: space-between; font-size: 10px; color: #8aa; margin-bottom: 4px; }
.density-val { color: #e0f7fa; font-weight: 600; }
.density-track { height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden; }
.density-fill { height: 100%; border-radius: 2px; transition: width .6s ease; }
.density-fill.peak { background: linear-gradient(90deg, #f44336, #ff5722); }
.density-fill.normal { background: linear-gradient(90deg, #ff9800, #ffc107); }
.density-fill.off-peak { background: linear-gradient(90deg, #4ade80, #81c784); }

/* Icon controls */
.icon-row { display: flex; gap: 6px; justify-content: center; }
.icon-btn {
  display: flex; flex-direction: column; align-items: center; gap: 3px;
  padding: 8px 6px; flex: 1;
  background: rgba(79,172,254,0.1); border: 1px solid rgba(79,172,254,0.2);
  border-radius: 8px; color: #c0d8e8; font-size: 11px; cursor: pointer;
  transition: all .3s;
}
.icon-btn:hover { background: rgba(79,172,254,0.25); border-color: rgba(79,172,254,0.5); transform: translateY(-2px); }
.icon-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.ico { font-size: 18px; }

/* Settings drawer */
.settings-drawer { margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(79,172,254,0.15); }
.field { margin-bottom: 8px; }
.field label { display: block; font-size: 11px; color: #8aa; margin-bottom: 3px; }
.field select, .field input {
  width: 100%; padding: 5px 8px; font-size: 12px;
  background: rgba(0,0,0,0.3); border: 1px solid rgba(79,172,254,0.3);
  border-radius: 4px; color: #e0f7fa;
}
.field.actions { display: flex; gap: 6px; margin-top: 10px; }
.btn {
  padding: 6px 12px; border: none; border-radius: 5px; font-size: 12px; cursor: pointer;
  background: rgba(100,116,139,0.6); color: #fff; transition: all .3s;
}
.btn:hover:not(:disabled) { transform: translateY(-1px); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn.primary { background: linear-gradient(90deg, #4facfe, #00f2fe); }
.btn.danger { background: rgba(239,68,68,0.8); }
.err { color: #ff6b6b; font-size: 11px; margin-top: 4px; }

/* ========== Center Map ========== */
.center-area { flex: 1; }
.map-panel {
  flex: 1; display: flex; flex-direction: column;
  background: rgba(13,27,42,0.7);
  border: 1px solid rgba(79,172,254,0.25);
  border-radius: 10px;
  box-shadow: 0 0 25px rgba(79,172,254,0.12);
  overflow: hidden;
}
.single-map-wrap, .multi-map-wrap { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.canvas-box { flex: 1; position: relative; min-height: 0; }
.canvas-box canvas {
  width: 100%; height: 100%;
  background: #0a1428;
  display: block;
}
.canvas-toolbar {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 10px;
  background: rgba(0,0,0,0.3);
  border-top: 1px solid rgba(79,172,254,0.15);
}
.canvas-toolbar button {
  padding: 4px 10px; font-size: 12px;
  background: rgba(79,172,254,0.15); border: 1px solid rgba(79,172,254,0.3);
  border-radius: 4px; color: #c0d8e8; cursor: pointer;
}
.canvas-toolbar button:hover { background: rgba(79,172,254,0.3); }
.zoom-txt { font-size: 11px; color: #4facfe; margin-left: auto; font-family: monospace; }

/* Conflict tooltip */
.conflict-tooltip {
  position: absolute;
  background: rgba(10,15,30,0.95);
  border: 1px solid rgba(255,77,79,0.5);
  border-radius: 6px; padding: 8px 10px;
  min-width: 180px; font-size: 11px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.5);
  pointer-events: none; z-index: 100;
}
.tt-title { color: #ff6b6b; font-weight: 700; margin-bottom: 4px; border-bottom: 1px solid rgba(255,77,79,0.2); padding-bottom: 3px; }
.tt-row { display: flex; justify-content: space-between; color: #c0d8e8; margin: 2px 0; }
.tt-row b { color: #fff; }

/* ========== Pie Chart ========== */
.pie-wrap { display: flex; align-items: center; gap: 12px; }
.pie {
  width: 56px; height: 56px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.1);
  overflow: hidden;
  display: flex;
}
.pie-half { width: 50%; height: 100%; }
.pie-legend { display: flex; flex-direction: column; gap: 4px; }
.pie-lv { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #c0d8e8; }
.pie-lv .dot { width: 8px; height: 8px; border-radius: 50%; }

/* Strategy ring */
.strategy-ring {
  width: 70px; height: 70px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto;
  border: 3px solid rgba(79,172,254,0.3);
  box-shadow: 0 0 15px rgba(79,172,254,0.2);
}
.ring-inner { text-align: center; }
.ring-label { font-size: 14px; font-weight: 700; color: #4facfe; }
.ring-sub { font-size: 9px; color: #8aa; }

/* ========== Footer ========== */
.dash-footer {
  position: relative; z-index: 2;
  height: 130px;
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
  padding: 0 10px 10px;
}
.footer-card {
  background: rgba(13,27,42,0.7);
  border: 1px solid rgba(79,172,254,0.2);
  border-radius: 10px;
  backdrop-filter: blur(8px);
  padding: 10px;
  display: flex; flex-direction: column;
  box-shadow: 0 0 15px rgba(79,172,254,0.06);
}
.f-title { font-size: 12px; font-weight: 700; color: #4facfe; margin-bottom: 8px; letter-spacing: 1px; }

/* Ring chart */
.ring-chart-wrap { display: flex; align-items: center; gap: 12px; flex: 1; }
.ring-chart {
  width: 56px; height: 56px; border-radius: 50%;
  display: flex; overflow: hidden;
  border: 2px solid rgba(255,255,255,0.1);
  transform: rotate(-90deg);
}
.ring-segment { transition: all .3s; }
.ring-segment.high { background: conic-gradient(from 0deg, #f44336 0deg, #ff6b6b 360deg); }
.ring-segment.medium { background: conic-gradient(from 0deg, #ff9800 0deg, #ffb74d 360deg); }
.ring-segment.safe { background: conic-gradient(from 0deg, #4ade80 0deg, #81c784 360deg); }
.ring-legend-v { display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: #c0d8e8; }
.lg-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 4px; }

/* Bar chart */
.bar-chart { display: flex; flex-direction: column; gap: 5px; flex: 1; justify-content: center; }
.bar-row { display: grid; grid-template-columns: 50px 1fr 24px; align-items: center; gap: 6px; font-size: 11px; }
.bar-label { color: #8aa; text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bar-track { height: 8px; background: rgba(0,0,0,0.3); border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; background: linear-gradient(90deg, #4facfe, #00f2fe); border-radius: 4px; transition: width .6s ease; }
.bar-val { color: #c0d8e8; text-align: right; font-family: monospace; }
.bar-empty { text-align: center; color: #567; font-size: 12px; }

/* Delay overview */
.delay-overview { display: flex; align-items: center; gap: 14px; flex: 1; }
.d-circle {
  width: 56px; height: 56px; border-radius: 50%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border: 2px solid rgba(74,222,128,0.4);
  background: rgba(74,222,128,0.08);
}
.d-circle.warn { border-color: rgba(255,152,0,0.4); background: rgba(255,152,0,0.08); }
.d-num { font-size: 16px; font-weight: 700; color: #4ade80; font-family: monospace; }
.d-circle.warn .d-num { color: #ff9800; }
.d-unit { font-size: 9px; color: #8aa; }
.d-bars { flex: 1; display: flex; flex-direction: column; gap: 6px; }
.d-row { display: grid; grid-template-columns: 60px 1fr; align-items: center; gap: 6px; font-size: 11px; color: #8aa; }
.d-track { position: relative; height: 6px; background: rgba(0,0,0,0.3); border-radius: 3px; overflow: hidden; }
.d-fill { height: 100%; background: linear-gradient(90deg, #ff9800, #ffc107); border-radius: 3px; }
.d-tooltip-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; cursor: pointer; }
.d-fill.blue { background: linear-gradient(90deg, #4facfe, #00f2fe); }
.d-fill.cyan { background: linear-gradient(90deg, #00bcd4, #00f2fe); }

/* ========== Modal ========== */
.modal-overlay {
  position: fixed; inset: 0; z-index: 2000;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px);
}
.modal-box {
  width: 420px; max-width: 90vw;
  background: rgba(13,27,42,0.95);
  border: 1px solid rgba(79,172,254,0.3);
  border-radius: 10px;
  box-shadow: 0 0 30px rgba(79,172,254,0.2);
  overflow: hidden;
}
.modal-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  background: rgba(79,172,254,0.08);
  border-bottom: 1px solid rgba(79,172,254,0.15);
}
.modal-head h3 { margin: 0; font-size: 14px; color: #4facfe; }
.modal-close { background: none; border: none; color: #8aa; font-size: 20px; cursor: pointer; }
.modal-close:hover { color: #fff; }
.modal-body { padding: 14px; }
.source-tabs { display: flex; gap: 8px; margin-bottom: 12px; }
.source-tabs button {
  flex: 1; padding: 6px; font-size: 12px;
  background: rgba(0,0,0,0.2); border: 1px solid rgba(79,172,254,0.2);
  border-radius: 5px; color: #8aa; cursor: pointer;
}
.source-tabs button.active { background: rgba(79,172,254,0.2); color: #4facfe; border-color: rgba(79,172,254,0.4); }
.source-content { font-size: 12px; }
.source-content label { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.source-content input { flex: 1; padding: 5px; background: rgba(0,0,0,0.2); border: 1px solid rgba(79,172,254,0.2); color: #e0f7fa; border-radius: 4px; }
.file-tag { color: #4ade80; font-size: 11px; margin: 0 8px; }

/* ========== Alt Sidebar ========== */
.alt-sidebar {
  position: fixed; top: 60px; right: 0; bottom: 0; width: 280px; z-index: 1500;
  background: rgba(10,20,40,0.95);
  border-left: 1px solid rgba(79,172,254,0.3);
  backdrop-filter: blur(10px);
  box-shadow: -5px 0 20px rgba(0,0,0,0.4);
  display: flex; flex-direction: column;
}
.alt-head { display: flex; align-items: center; justify-content: space-between; padding: 12px; border-bottom: 1px solid rgba(79,172,254,0.15); }
.alt-head h3 { margin: 0; font-size: 14px; color: #4facfe; }
.alt-body { flex: 1; overflow: auto; padding: 12px; }
.alt-info { padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px; margin-bottom: 10px; }
.alt-info h4 { margin: 0 0 6px; color: #4facfe; }
.alt-tags { display: flex; gap: 6px; }
.alt-tags span { font-size: 10px; padding: 2px 8px; border-radius: 4px; background: rgba(79,172,254,0.15); color: #4facfe; }
.alt-tags span.departure { background: rgba(255,105,180,0.15); color: #ff69b4; }
.alt-list { display: flex; flex-direction: column; gap: 8px; }
.alt-card { padding: 10px; border-radius: 6px; border: 1px solid rgba(79,172,254,0.2); background: rgba(0,0,0,0.15); }
.alt-card.active { border-color: #4facfe; background: rgba(79,172,254,0.1); }
.alt-rank { font-size: 12px; font-weight: 700; color: #e0f7fa; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
.tag { font-size: 9px; padding: 1px 6px; border-radius: 4px; background: rgba(74,222,128,0.2); color: #4ade80; }
.tag.conflict { background: rgba(244,67,54,0.2); color: #f44336; }
.alt-stat { font-size: 11px; color: #8aa; margin-bottom: 8px; }
.alt-actions { display: flex; gap: 6px; }
.alt-actions button { flex: 1; padding: 5px; font-size: 11px; border: none; border-radius: 4px; cursor: pointer; background: rgba(100,116,139,0.5); color: #fff; }
.alt-actions button.primary { background: linear-gradient(90deg, #4facfe, #00f2fe); }
.alt-actions button:disabled { opacity: 0.4; cursor: not-allowed; }
.loading { display: flex; flex-direction: column; align-items: center; padding: 20px; color: #8aa; font-size: 12px; }
.spinner { width: 24px; height: 24px; border: 2px solid rgba(79,172,254,0.2); border-top-color: #4facfe; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 8px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Slide transition */
.slide-enter-active, .slide-leave-active { transition: all .3s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); opacity: 0; }

/* Flight list */
.flight-panel { flex: 1.8; }
.flight-ops { display: flex; align-items: center; gap: 6px; }
.sel-text { font-size: 10px; color: #8aa; }
.mini-btn { padding: 2px 8px; font-size: 10px; background: rgba(79,172,254,0.15); border: 1px solid rgba(79,172,254,0.3); border-radius: 4px; color: #4facfe; cursor: pointer; }
.flight-list { display: flex; flex-direction: column; gap: 6px; }
.flight-card {
  padding: 8px; border-radius: 6px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(79,172,254,0.1);
  border-left: 3px solid rgba(79,172,254,0.4);
  cursor: pointer; transition: all .2s; font-size: 11px;
}
.flight-card:hover { background: rgba(79,172,254,0.08); border-color: rgba(79,172,254,0.3); }
.flight-card.selected { background: rgba(79,172,254,0.12); border-left-color: #4facfe; }
.flight-card.has-conflict { border-left-color: #f44336; background: rgba(244,67,54,0.06); }
.flight-card.has-delay { border-left-color: #ff9800; background: rgba(255,152,0,0.05); }
.flight-card.success { border-left-color: #4ade80; }
.flight-main { display: flex; align-items: flex-start; gap: 8px; }
.fc-check { width: 14px; height: 14px; margin-top: 2px; accent-color: #4facfe; cursor: pointer; }
.flight-info { flex: 1; min-width: 0; }
.flight-top { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 4px; }
.fid { font-weight: 700; color: #fff; font-size: 12px; }
.ftype { font-size: 10px; color: #8aa; background: rgba(0,0,0,0.3); padding: 1px 6px; border-radius: 4px; }
.fop { font-size: 10px; padding: 1px 6px; border-radius: 4px; font-weight: 600; }
.fop.departure { background: rgba(255,105,180,0.15); color: #ff69b4; }
.fop.arrival { background: rgba(0,242,254,0.15); color: #00f2fe; }
.flight-mid { display: flex; gap: 8px; flex-wrap: wrap; color: #8aa; font-size: 10px; }
.flight-mid .warn { color: #ff9800; }
.flight-actions { margin-top: 6px; display: flex; justify-content: flex-end; }
.alt-btn { padding: 3px 10px; font-size: 10px; border: none; border-radius: 4px; cursor: pointer; transition: all .2s; }
.alt-btn.danger { background: rgba(244,67,54,0.2); color: #ff6b6b; border: 1px solid rgba(244,67,54,0.3); }
.alt-btn.danger:hover { background: rgba(244,67,54,0.35); transform: translateY(-1px); }
.alt-btn.safe { background: rgba(74,222,128,0.1); color: #4ade80; border: 1px solid rgba(74,222,128,0.2); cursor: default; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(79,172,254,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(79,172,254,0.4); }

/* NetworkVisualization deep adjustments */
.single-map-wrap { height: 100%; }
.single-map-wrap :deep(.network-visualization) { height: 100%; }
.single-map-wrap :deep(.path-stats) { display: none; }
</style>
