<template>
  <div class="algorithm-detail">
    <div class="grid-background"></div>
    <div class="particles"></div>
    <div class="container">
      <div class="algorithm-content">
        <!-- 顶部主Tab栏 -->
        <div class="main-tab-container">
          <div class="main-tab-buttons">
            <button
              class="main-tab-btn"
              :class="{ active: activeMainTab === 'details' }"
              @click="activeMainTab = 'details'">
              <span class="main-tab-icon">📖</span>
              算法详情
            </button>
            <button
              class="main-tab-btn"
              :class="{ active: activeMainTab === 'demo' }"
              @click="activeMainTab = 'demo'">
              <span class="main-tab-icon">🎮</span>
              算法演示
            </button>
          </div>
        </div>

        <!-- 算法详情 -->
        <div v-show="activeMainTab === 'details'">
          <AlgorithmDetails />
        </div>

        <!-- 算法演示 -->
        <div v-show="activeMainTab === 'demo'">

        <div class="visualization-section">
          <h3>算法演示 - 西安机场路网</h3>

          <!-- Tab 切换 -->
          <div class="tab-container">
            <div class="tab-buttons">
              <button
                class="tab-btn"
                :class="{ active: activeTab === 'single' }"
                @click="switchTab('single')">
                <span class="tab-icon">✈️</span>
                单航班演示
              </button>
              <button
                class="tab-btn"
                :class="{ active: activeTab === 'multi' }"
                @click="switchTab('multi')">
                <span class="tab-icon">🛫</span>
                多航班调度
              </button>
            </div>

            <div class="tab-content">
              <!-- 单航班演示 -->
              <div v-show="activeTab === 'single'" class="tab-panel">
                <NetworkVisualization
                  ref="networkViz"
                  demo1ButtonName="演示1: 最远机位路径"
                  demo2ButtonName="演示2: 机位到跑道"
                  :toggleButtonText="{ showMore: '显示跑道点和观察点', showOnly: '只显示机位' }"
                  hint="💡 滚轮缩放，拖拽移动 | 使用下方下拉列表选择起点和终点"
                  resultPathName="A*优化路径"
                  @loadData="loadDemo"
                  @runDemo1="runFarthestStand"
                  @runDemo2="runStandToRunway"
                  @displayToggled="handleDisplayToggled"
                  @runCustomPath="calculateCustomPath"
                />
              </div>

              <!-- 多航班调度 -->
              <div v-show="activeTab === 'multi'" class="tab-panel multi-aircraft-panel">
                <!-- Excel文件上传区域 -->
                <div class="upload-section">
                  <div class="upload-header">
                    <h4>📁 数据来源</h4>
                    <div class="source-tabs">
                      <button
                        class="source-tab"
                        :class="{ active: dataSource === 'random' }"
                        @click="switchDataSource('random')">
                        随机生成
                      </button>
                      <button
                        class="source-tab"
                        :class="{ active: dataSource === 'upload' }"
                        @click="switchDataSource('upload')">
                        上传文件
                      </button>
                    </div>
                  </div>

                  <!-- 随机生成模式 -->
                  <div v-show="dataSource === 'random'" class="source-content">
                    <div class="multi-controls">
                      <div class="control-group">
                        <label>航班数量:</label>
                        <select v-model="flightCount" :disabled="isScheduling">
                          <option :value="3">3 架</option>
                          <option :value="5">5 架</option>
                          <option :value="6">6 架</option>
                          <option :value="8">8 架</option>
                          <option :value="10">10 架</option>
                        </select>
                      </div>

                      <div class="control-group">
                        <button
                          @click="generateFlights"
                          class="action-btn"
                          :disabled="isScheduling">
                          <span class="btn-icon">🎲</span> 生成航班
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- 文件上传模式 -->
                  <div v-show="dataSource === 'upload'" class="source-content">
                    <!-- 数据格式提示 -->
                    <div class="format-hint">
                      <h5>📋 Excel文件格式要求</h5>
                      <p>请上传包含以下列的Excel文件：</p>
                      <div class="format-table">
                        <div class="format-row">
                          <span class="format-column">flight_id</span>
                          <span class="format-desc">航班ID（如：FL1001）</span>
                        </div>
                        <div class="format-row">
                          <span class="format-column">aircraft_type</span>
                          <span class="format-desc">机型（如：A320、B737）</span>
                        </div>
                        <div class="format-row">
                          <span class="format-column">operation</span>
                          <span class="format-desc">操作类型（departure/arrival）</span>
                        </div>
                        <div class="format-row">
                          <span class="format-column">scheduled_time</span>
                          <span class="format-desc">计划时间（格式：2024-01-20 14:00:00）</span>
                        </div>
                        <div class="format-row">
                          <span class="format-column">start_node_id</span>
                          <span class="format-desc">起始节点ID（数字）</span>
                        </div>
                        <div class="format-row">
                          <span class="format-column">end_node_id</span>
                          <span class="format-desc">目标节点ID（数字）</span>
                        </div>
                        <div class="format-row">
                          <span class="format-column">priority</span>
                          <span class="format-desc">优先级（1-10，数字越大优先级越高）</span>
                        </div>
                      </div>
                    </div>

                    <!-- 文件上传区域 -->
                    <div class="upload-area">
                      <div class="upload-controls">
                        <input
                          type="file"
                          ref="fileInput"
                          @change="handleFileChange"
                          accept=".xlsx,.xls"
                          style="display: none"
                        />
                        <button
                          @click="$refs.fileInput?.click()"
                          class="action-btn upload-btn"
                          :disabled="isScheduling">
                          <span class="btn-icon">📤</span> 选择文件
                        </button>
                        <span v-if="selectedFile" class="file-name">
                          {{ selectedFile.name }}
                        </span>
                      </div>
                      <button
                        @click="extractFlightsFromExcel"
                        class="action-btn primary extract-btn"
                        :disabled="isScheduling || !selectedFile">
                        <span class="btn-icon">📥</span> 提取航班信息
                      </button>
                    </div>

                    <!-- 错误提示 -->
                    <div v-if="uploadError" class="error-message">
                      ⚠️ {{ uploadError }}
                    </div>
                  </div>
                </div>

                <!-- 调度控制 -->
                <div class="multi-controls">
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
                      @click="scheduleFlights"
                      class="action-btn primary"
                      :disabled="isScheduling || !flights.length">
                      <span class="btn-icon">▶️</span> {{ isScheduling ? '调度中...' : '开始调度' }}
                    </button>
                    <button
                      @click="resetMulti"
                      class="action-btn danger"
                      :disabled="isScheduling">
                      <span class="btn-icon">🔄</span> 重置
                    </button>
                  </div>
                </div>

                <!-- 当前时段状态指示器 -->
                <div v-if="flights.length > 0 && weights" class="period-status-indicator">
                  <div class="period-status-content" :class="weights.time > weights.fuel ? 'peak' : (weights.fuel > weights.time ? 'off-peak' : 'normal')">
                    <div class="period-status-icon">
                      {{ weights.time > weights.fuel ? '🔴' : (weights.fuel > weights.time ? '🟢' : '🟡') }}
                    </div>
                    <div class="period-status-text">
                      <div class="period-status-title">
                        {{ weights.time > weights.fuel ? '当前处于高峰时段' : (weights.fuel > weights.time ? '当前处于低峰时段' : '当前处于正常时段') }}
                      </div>
                      <div class="period-status-desc">
                        {{ weights.time > weights.fuel ? 'A*算法将优先优化滑行时间（提升准点率）' : (weights.fuel > weights.time ? 'A*算法将优先优化燃料消耗（提升经济性）' : 'A*算法平衡考虑时间和燃料消耗') }}
                      </div>
                      <div class="period-weights-detail">
                        <span>时间权重: <strong>{{ weights.time.toFixed(1) }}</strong></span>
                        <span class="weight-separator">|</span>
                        <span>燃料权重: <strong>{{ weights.fuel.toFixed(1) }}</strong></span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 统计信息 -->
                <div v-if="statistics" class="multi-stats">
                  <div class="stat-card">
                    <div class="stat-label">航班总数</div>
                    <div class="stat-value">{{ statistics.flight_count }}</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-label">总距离</div>
                    <div class="stat-value">{{ (statistics.total_distance / 1000).toFixed(2) }} km</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-label">总时间</div>
                    <div class="stat-value">{{ (statistics.total_time / 60).toFixed(1) }} 分钟</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-label">总延误</div>
                    <div class="stat-value delay">{{ (statistics.total_delay / 60).toFixed(1) }} 分钟</div>
                  </div>
                  <div class="stat-card" :class="statistics.total_conflicts > 0 ? 'has-conflicts' : 'no-conflicts'">
                    <div class="stat-label">冲突数</div>
                    <div class="stat-value">{{ statistics.total_conflicts }}</div>
                  </div>
                </div>

                <!-- 时间段与权重信息 -->
                <div v-if="timePeriodAnalysis || weights" class="period-weight-section">
                  <h4>📊 时间段分析与权重配置</h4>
                  <div class="period-weight-content">
                    <!-- 时间段分析 -->
                    <div v-if="timePeriodAnalysis" class="period-analysis">
                      <div class="period-summary">
                        <div class="period-item">
                          <span class="period-label">航班密度分析：</span>
                          <span class="period-value">{{ timePeriodAnalysis.flight_count }} 个航班</span>
                        </div>
                        <div class="period-item">
                          <span class="period-label">时间范围：</span>
                          <span class="period-value">{{ formatDateTime(timePeriodAnalysis.time_range.start) }} - {{ formatDateTime(timePeriodAnalysis.time_range.end) }}</span>
                        </div>
                        <div class="period-item">
                          <span class="period-label">平均密度：</span>
                          <span class="period-value">{{ timePeriodAnalysis.average_density.toFixed(2) }} 航班/小时</span>
                        </div>
                        <div class="period-item">
                          <span class="period-label">高峰期窗口：</span>
                          <span class="period-value">{{ timePeriodAnalysis.peak_windows.length }} 个</span>
                        </div>
                        <div class="period-item">
                          <span class="period-label">低峰期窗口：</span>
                          <span class="period-value">{{ timePeriodAnalysis.off_peak_windows.length }} 个</span>
                        </div>
                      </div>
                    </div>

                    <!-- 权重配置 -->
                    <div class="weight-config">
                      <div class="weight-header">
                        <div class="weight-title">
                          <span>⚖️ 多目标A*算法权重</span>
                          <span class="weight-mode">{{ weightAdjustmentMode === 'auto' ? '（自动调整）' : '（手动调整）' }}</span>
                        </div>
                        <div class="weight-controls">
                          <button @click="adjustWeightsAuto" class="weight-btn auto" :disabled="weightAdjustmentMode === 'auto'">自动</button>
                          <button @click="adjustWeightsManually" class="weight-btn manual" :disabled="weightAdjustmentMode === 'manual'">手动</button>
                        </div>
                      </div>
                      <div class="weight-values">
                        <div class="weight-item">
                          <span class="weight-label">距离权重：</span>
                          <span class="weight-value">{{ weights.distance.toFixed(1) }}</span>
                          <span class="weight-desc">（最短路径）</span>
                        </div>
                        <div class="weight-item">
                          <span class="weight-label">时间权重：</span>
                          <span class="weight-value">{{ weights.time.toFixed(1) }}</span>
                          <span class="weight-desc">（滑行时间）</span>
                        </div>
                        <div class="weight-item">
                          <span class="weight-label">燃料权重：</span>
                          <span class="weight-value">{{ weights.fuel.toFixed(1) }}</span>
                          <span class="weight-desc">（燃料消耗）</span>
                        </div>
                      </div>
                      <div class="weight-description">
                        <p v-if="weightAdjustmentMode === 'auto'">
                          🚦 当前根据航班密度自动调整权重：
                          <span v-if="weights.time > weights.fuel" class="period-indicator peak">高峰时段 - 优先准点率（时间权重较高）</span>
                          <span v-else-if="weights.fuel > weights.time" class="period-indicator off-peak">低峰时段 - 优先经济性（燃料权重较高）</span>
                          <span v-else class="period-indicator normal">正常时段 - 平衡考虑</span>
                        </p>
                        <p v-else>⚙️ 手动调整模式：权重值固定，不随航班密度变化</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 可视化画布 -->
                <div v-if="schedules.length || multiNodesLoaded" class="multi-visualization">
                  <canvas
                    ref="multiCanvas"
                    width="1200"
                    height="600"
                    @wheel="handleMultiWheel"
                    @mousedown="handleMultiMouseDown"
                    @mousemove="handleMultiMouseMove"
                    @mouseup="handleMultiMouseUp"
                    @mouseleave="handleMultiMouseUp"
                    class="multi-canvas"></canvas>

                  <div class="canvas-controls">
                    <button @click="multiZoomIn" class="zoom-btn">放大 +</button>
                    <button @click="multiZoomOut" class="zoom-btn">缩小 -</button>
                    <button @click="multiResetView" class="zoom-btn">重置</button>
                    <span class="zoom-level">缩放: {{ (multiZoomLevel * 100).toFixed(0) }}%</span>
                  </div>

                  <div class="canvas-controls-mini" v-if="multiNodesLoaded">
                    <button @click="toggleMultiDisplay" class="mini-btn">
                      {{ showCoreNodesOnly ? '显示所有节点' : '只显示机位' }}
                    </button>
                    <span class="info-text">已加载 {{ multiNodes.length }} 个节点 + {{ multiEdges.length }} 条边</span>
                  </div>

                  <div class="canvas-legend">
                    <div class="legend-section">
                      <div class="legend-title">路径颜色</div>
                      <div class="legend-item">
                        <span class="legend-dot departure"></span>
                        <span>离港路径（粉色系）</span>
                      </div>
                      <div class="legend-item">
                        <span class="legend-dot arrival"></span>
                        <span>进港路径（蓝色系）</span>
                      </div>
                    </div>
                    <div class="legend-section">
                      <div class="legend-title">航班标注</div>
                      <div class="legend-item">
                        <span class="legend-circle-filled"></span>
                        <span>实心圆 = 起点位置</span>
                      </div>
                      <div class="legend-item">
                        <span class="legend-circle-hollow"></span>
                        <span>空心圆 = 终点位置</span>
                      </div>
                      <div class="legend-item">
                        <span class="legend-text">FL1000</span>
                        <span>航班ID标签</span>
                      </div>
                    </div>
                    <div class="legend-section">
                      <div class="legend-title">其他</div>
                      <div class="legend-item">
                        <span class="legend-dot conflict"></span>
                        <span>冲突点（红色光晕+感叹号）</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 航班列表 -->
                <div v-if="flights.length" class="flights-list">
                  <div class="flights-list-header">
                    <h4>航班列表</h4>
                    <div class="flight-controls">
                      <span class="selected-count" v-if="schedules.length">
                        已选择: {{ selectedFlightIds.length }} / {{ flights.length }}
                      </span>
                      <button
                        v-if="schedules.length"
                        @click="toggleSelectAll"
                        class="select-btn">
                        {{ selectedFlightIds.length === flights.length ? '取消全选' : '全选' }}
                      </button>
                      <button
                        v-if="selectedFlightIds.length > 0"
                        @click="clearSelection"
                        class="select-btn clear">
                        清除选择
                      </button>
                    </div>
                  </div>
                  <div class="flight-table-container">
                    <table class="flight-table">
                      <thead>
                        <tr>
                          <th class="col-checkbox">选择</th>
                          <th class="col-flight-id">航班ID</th>
                          <th class="col-type">机型</th>
                          <th class="col-operation">任务</th>
                          <th class="col-time">时间</th>
                          <th class="col-distance">距离</th>
                          <th class="col-delay">延误</th>
                          <th class="col-action">操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="flight in flights"
                          :key="flight.flight_id"
                          :class="[getFlightStatusClass(flight), { 'selected': selectedFlightIds.includes(flight.flight_id) }]"
                          @click="toggleFlightSelection(flight.flight_id)">
                          <td class="col-checkbox">
                            <input
                              type="checkbox"
                              :checked="selectedFlightIds.includes(flight.flight_id)"
                              @click.stop="toggleFlightSelection(flight.flight_id)"
                              :disabled="!schedules.length" />
                          </td>
                          <td class="col-flight-id">{{ flight.flight_id }}</td>
                          <td class="col-type">{{ flight.aircraft_type }}</td>
                          <td class="col-operation" :class="flight.operation">
                            {{ flight.operation === 'departure' ? '离港' : '进港' }}
                          </td>
                          <td class="col-time">{{ formatTime(flight.scheduled_time) }}</td>
                          <td class="col-distance">
                            {{ getScheduleResult(flight.flight_id) ? (getScheduleResult(flight.flight_id).total_distance / 1000).toFixed(2) + ' km' : '-' }}
                          </td>
                          <td class="col-delay" :class="{ 'has-delay': getScheduleResult(flight.flight_id) && getScheduleResult(flight.flight_id).delay > 0 }">
                            {{ getScheduleResult(flight.flight_id) ? (getScheduleResult(flight.flight_id).delay / 60).toFixed(1) + ' 分钟' : '-' }}
                          </td>
                          <td class="col-action">
                            <button
                              v-if="getScheduleResult(flight.flight_id)"
                              @click.stop="showPathAlternatives(flight)"
                              class="view-alternatives-btn">
                              🛤️ 备选路径
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- 冲突列表 -->
                <div v-if="allConflicts.length" class="conflicts-list">
                  <h4>检测到的冲突 ({{ allConflicts.length }})</h4>
                  <div class="conflict-cards">
                    <div
                      v-for="conflict in allConflicts"
                      :key="conflict.conflict_id"
                      class="conflict-card"
                      :class="conflict.severity">
                      <div class="conflict-header">
                        <span class="conflict-type">{{ getConflictTypeText(conflict.conflict_type) }}</span>
                        <span class="conflict-severity">{{ conflict.severity }}</span>
                      </div>
                      <div class="conflict-info">
                        <div>航班: {{ conflict.flight_ids.join(', ') }}</div>
                        <div>时间: {{ formatTime(conflict.time) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>

        <button class="back-btn" @click="goBack">返回首页</button>
      </div>
    </div>

    <!-- 备选路径侧边栏（移到最外层，fixed定位） -->
    <transition name="slide">
      <div v-if="showPathAlternativesPanel" class="path-alternatives-sidebar">
        <div class="sidebar-header">
          <h3>🛤️ 路径选项</h3>
          <button @click="closePathAlternatives" class="close-btn">×</button>
        </div>

        <div class="sidebar-content">
          <div v-if="selectedFlight" class="selected-flight-info">
            <h4>{{ selectedFlight.flight_id }}</h4>
            <div class="flight-details">
              <span class="detail-item">{{ selectedFlight.aircraft_type }}</span>
              <span class="detail-item" :class="selectedFlight.operation">
                {{ selectedFlight.operation === 'departure' ? '离港' : '进港' }}
              </span>
            </div>
            <div class="route-info">
              <span>节点{{ selectedFlight.start_node_id }} → 节点{{ selectedFlight.end_node_id }}</span>
            </div>
          </div>

          <!-- 取消预览按钮 -->
          <div v-if="isPreviewingPath" class="preview-controls">
            <button @click="cancelPreview" class="cancel-preview-btn">
              ✕ 取消预览
            </button>
          </div>

          <div v-if="loadingAlternatives" class="loading">
            <div class="spinner"></div>
            <p>正在查找备选路径...</p>
          </div>

          <div v-else-if="pathAlternatives.length > 0" class="alternatives-list">
            <div
              v-for="alt in pathAlternatives"
              :key="alt.path_id"
              class="alternative-card"
              :class="{
                'active': alt.path_id === activePathId,
                'recommended': alt.rank === 1
              }"
            >
              <div class="alt-header">
                <div class="alt-rank">
                  <input
                    type="radio"
                    :id="alt.path_id"
                    :value="alt.path_id"
                    v-model="activePathId"
                    @change="selectAlternativePath(alt)"
                  />
                  <label :for="alt.path_id">
                    路径 {{ alt.rank }}
                    <span v-if="alt.rank === 1" class="badge recommended">推荐</span>
                    <span v-if="alt.differences_from_best.distance > 0" class="badge detour">
                      +{{ (alt.differences_from_best.distance).toFixed(0) }}m
                    </span>
                  </label>
                </div>
              </div>

              <div class="alt-stats">
                <div class="stat-row">
                  <span class="stat-label">📏 距离:</span>
                  <span class="stat-value">{{ (alt.distance / 1000).toFixed(2) }} km</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">⏱️ 时间:</span>
                  <span class="stat-value">{{ (alt.time / 60).toFixed(1) }} min</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">🛢️ 节点数:</span>
                  <span class="stat-value">{{ alt.num_nodes }}</span>
                </div>
              </div>

              <div class="alt-actions">
                <button
                  @click="previewPath(alt)"
                  class="preview-btn"
                  :disabled="alt.path_id === activePathId"
                >
                  👁️ 预览
                </button>
                <button
                  @click="applyAlternativePath(alt)"
                  class="apply-btn"
                  :disabled="alt.path_id === activePathId"
                >
                  ✓ 使用此路径
                </button>
              </div>
            </div>
          </div>

          <div v-else-if="!loadingAlternatives && pathAlternatives.length === 0" class="no-alternatives">
            <p>未找到备选路径</p>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from 'axios';
import NetworkVisualization from './NetworkVisualization.vue';
import AlgorithmDetails from './AlgorithmDetails.vue';
import * as XLSX from 'xlsx';
import { ElMessage } from 'element-plus';

const API_BASE = 'http://localhost:5001/api';

export default {
  name: 'AStarAlgorithm',
  components: {
    NetworkVisualization,
    AlgorithmDetails
  },
  data() {
    return {
      activeTab: 'single', // 'single' 或 'multi'
      activeMainTab: 'details', // 'details' 或 'demo'
      nodes: [],
      edges: [],

      // 多航班相关
      flightCount: 6,
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
      multiBaseScale: 1.0,
      multiBaseOffsetX: 0,
      multiBaseOffsetY: 0,

      // 航班密度分析和权重动态调整
      flightDensity: null,
      peakPeriods: [],
      offPeakPeriods: [],
      timePeriodAnalysis: null,
      weights: {
        distance: 1.0,
        time: 1.0,      // 滑行时间权重
        fuel: 0.5       // 燃料损耗权重
      },
      weightAdjustmentMode: 'auto', // 'auto' 或 'manual'
      peakThreshold: 0.6, // 高峰期阈值（密度百分比）
      timeWindowSize: 30, // 时间窗口大小（分钟）
    }
  },
  computed: {
    allConflicts() {
      const conflicts = [];
      this.schedules.forEach(schedule => {
        schedule.conflicts.forEach(conflict => {
          if (!conflicts.find(c => c.conflict_id === conflict.conflict_id)) {
            conflicts.push(conflict);
          }
        });
      });
      return conflicts;
    }
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

    async generateFlights() {
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

    drawMultiAircraftPaths() {
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

      // 如果正在预览路径，重绘预览路径
      if (this.isPreviewingPath && this.previewPathData) {
        this.$nextTick(() => {
          this.drawPreviewPath(this.previewPathData);
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
      // 如果手动清除了选择，不显示任何航班；否则如果没有选择任何航班，显示所有航班；如果选择了航班，只显示选中的航班
      let schedulesToDraw;
      if (this.manuallyCleared) {
        schedulesToDraw = [];
      } else if (this.selectedFlightIds.length === 0) {
        schedulesToDraw = this.schedules;
      } else {
        schedulesToDraw = this.schedules.filter(s => this.selectedFlightIds.includes(s.flight_id));
      }

      // 绘制路径
      schedulesToDraw.forEach((schedule) => {
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
      if (this.manuallyCleared) {
        conflictsToDraw = [];
      } else if (this.selectedFlightIds.length === 0) {
        conflictsToDraw = this.allConflicts;
      } else {
        conflictsToDraw = this.allConflicts.filter(conflict =>
          conflict.flight_ids.some(id => this.selectedFlightIds.includes(id))
        );
      }

      conflictsToDraw.forEach(conflict => {
        const schedule = this.schedules.find(s =>
          s.path.some(p => p.id === conflict.node_id)
        );

        if (schedule) {
          const point = schedule.path.find(p => p.id === conflict.node_id);
          if (point) {
            const pos = this.multiTransform(point.x, point.y);
            const conflictSize = Math.max(4, Math.min(10, 6 * Math.sqrt(this.multiZoomLevel)));

            // 红色光晕
            const gradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, conflictSize);
            gradient.addColorStop(0, conflict.severity === 'high' ? 'rgba(255, 0, 0, 0.9)' : 'rgba(255, 165, 0, 0.9)');
            gradient.addColorStop(1, 'rgba(255, 0, 0, 0)');
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, conflictSize, 0, Math.PI * 2);
            ctx.fill();

            // 白色边框
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = Math.max(1, 1.5 * Math.sqrt(this.multiZoomLevel));
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, conflictSize * 0.6, 0, Math.PI * 2);
            ctx.stroke();

            // 感叹号
            ctx.fillStyle = '#ffffff';
            const alertSize = Math.max(7, Math.min(12, 9 * Math.sqrt(this.multiZoomLevel)));
            ctx.font = 'bold ' + alertSize + 'px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('!', pos.x, pos.y);
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
      if (!this.multiIsDragging) return;

      const dx = event.clientX - this.multiDragStart.x;
      const dy = event.clientY - this.multiDragStart.y;

      this.multiPanOffset.x += dx;
      this.multiPanOffset.y += dy;

      this.multiDragStart = {
        x: event.clientX,
        y: event.clientY
      };

      this.drawMultiAircraftPaths();
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

      // 清除手动清除标记
      this.manuallyCleared = false;

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

    // ========== 备选路径相关方法 ==========
    async showPathAlternatives(flight) {
      this.selectedFlight = flight;
      this.showPathAlternativesPanel = true;
      this.loadingAlternatives = true;
      this.pathAlternatives = [];
      this.activePathId = 'path_1';

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
          this.pathAlternatives = response.data.paths;
          // 将当前路径添加到列表中作为第一条
          this.pathAlternatives.unshift({
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
            rank: 0,
            differences_from_best: { distance: 0, time: 0, fuel: 0 },
            is_original: true
          });
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
    },

    async previewPath(altPath) {
      // 预览选中的路径（在画布中高亮显示）
      try {
        // 保存预览状态和数据
        this.isPreviewingPath = true;
        this.previewPathData = altPath;

        // 绘制预览路径
        await this.drawPreviewPath(altPath);
        ElMessage.success(`正在预览路径${altPath.rank || '原始'}`);
      } catch (error) {
        console.error('预览路径失败:', error);
        ElMessage.error('预览路径失败');
      }
    },

    async drawPreviewPath(altPath) {
      if (!this.multiTransform) return;

      const ctx = this.multiCtx;

      // 先重绘所有已选择的航班路径（半透明）
      let schedulesToDraw;
      if (this.manuallyCleared) {
        schedulesToDraw = [];
      } else if (this.selectedFlightIds.length === 0) {
        schedulesToDraw = this.schedules;
      } else {
        schedulesToDraw = this.schedules.filter(s => this.selectedFlightIds.includes(s.flight_id));
      }

      schedulesToDraw.forEach((schedule) => {
        if (schedule.flight_id === this.selectedFlight.flight_id) {
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
      this.drawMultiAircraftPaths();
      ElMessage.info('已取消预览');
    },

    async applyAlternativePath(altPath) {
      // 应用选择的路径（更新调度结果）
      try {
        // 这里应该调用后端API来更新路径
        // 暂时只显示提示信息
        if (altPath.is_original) {
          ElMessage.info('这是当前正在使用的路径');
          return;
        }

        const distanceDiff = altPath.differences_from_best.distance;
        const timeDiff = altPath.differences_from_best.time;

        let message = `已选择路径${altPath.rank}（绕行）`;
        if (distanceDiff > 0) {
          message += `\n绕行距离: ${distanceDiff.toFixed(0)}m`;
        }
        if (timeDiff > 0) {
          message += `\n时间增加: ${(timeDiff / 60).toFixed(1)}分钟`;
        }

        ElMessage.success({
          message: message,
          duration: 5000,
          showClose: true
        });

        // TODO: 调用后端API更新调度结果
        // await this.updateFlightPath(this.selectedFlight.flight_id, altPath);

        // 刷新视图
        await this.drawPreviewPath(altPath);

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
          this.weightAdjustmentMode = 'auto';

          // 显示提示信息
          ElMessage.success({
            message: `当前时间段: ${weightInfo.description}`,
            duration: 3000,
            showClose: true
          });
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
    updateWeightParams() {
      this.analyzeFlightDensity();
    }
  }
}
</script>

<style scoped>
.algorithm-detail {
  position: relative;
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
  overflow-x: hidden;
}

.grid-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(64, 224, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(64, 224, 255, 0.08) 1px, transparent 1px);
  background-size: 40px 40px;
  z-index: -2;
}

.particles {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}

.particles::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(circle at 10% 20%, rgba(135, 206, 250, 0.05) 0%, transparent 20%),
    radial-gradient(circle at 90% 80%, rgba(135, 206, 250, 0.05) 0%, transparent 20%),
    radial-gradient(circle at 50% 50%, rgba(135, 206, 250, 0.03) 0%, transparent 15%);
  animation: float 15s infinite linear;
}

@keyframes float {
  0% { transform: translate(0, 0); }
  25% { transform: translate(5px, 5px); }
  50% { transform: translate(0, 5px); }
  75% { transform: translate(-5px, 0); }
  100% { transform: translate(0, 0); }
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.algorithm-title {
  font-size: 2rem;
  text-align: center;
  margin-bottom: 2rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.algorithm-content {
  background: rgba(20, 30, 60, 0.6);
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(64, 224, 255, 0.2);
  backdrop-filter: blur(5px);
}

.intro-section, .features-section, .application-section, .visualization-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(30, 40, 70, 0.4);
  border-radius: 8px;
}

.intro-section h3, .features-section h3, .application-section h3, .visualization-section h3 {
  font-size: 1.4rem;
  margin-bottom: 1rem;
  color: #4facfe;
}

.intro-section p, .features-section ul, .application-section ul {
  color: #a0b3c6;
  line-height: 1.6;
}

.features-section li, .application-section li {
  margin: 0.5rem 0;
  padding-left: 1rem;
}

/* 主Tab样式 */
.main-tab-container {
  margin-bottom: 2rem;
}

.main-tab-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.main-tab-btn {
  padding: 1rem 2.5rem;
  background: rgba(30, 40, 70, 0.6);
  color: #a0b3c6;
  border: 2px solid rgba(64, 224, 255, 0.3);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.main-tab-btn:hover {
  background: rgba(40, 50, 80, 0.8);
  border-color: rgba(64, 224, 255, 0.5);
  transform: translateY(-2px);
}

.main-tab-btn.active {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

.main-tab-icon {
  font-size: 1.3rem;
}

/* Tab 样式 */
.tab-container {
  background: rgba(10, 20, 40, 0.5);
  border-radius: 8px;
  padding: 1rem;
}

.tab-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  justify-content: center;
}

.tab-btn {
  padding: 0.8rem 2rem;
  background: rgba(30, 40, 70, 0.6);
  color: #a0b3c6;
  border: 2px solid rgba(64, 224, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-btn:hover {
  background: rgba(40, 50, 80, 0.8);
  border-color: rgba(64, 224, 255, 0.5);
}

.tab-btn.active {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

.tab-icon {
  font-size: 1.2rem;
}

.tab-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 上传区域样式 */
.upload-section {
  background: rgba(20, 30, 60, 0.6);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(64, 224, 255, 0.3);
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.upload-header h4 {
  color: #4facfe;
  margin: 0;
  font-size: 1.2rem;
}

.source-tabs {
  display: flex;
  gap: 0.5rem;
}

.source-tab {
  padding: 0.5rem 1rem;
  background: rgba(30, 40, 70, 0.6);
  color: #a0b3c6;
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.source-tab:hover {
  background: rgba(40, 50, 80, 0.8);
  border-color: rgba(64, 224, 255, 0.5);
}

.source-tab.active {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border-color: transparent;
}

.source-content {
  animation: fadeIn 0.3s ease;
}

/* 格式提示 */
.format-hint {
  background: rgba(10, 20, 40, 0.5);
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid rgba(79, 172, 254, 0.2);
}

.format-hint h5 {
  color: #4facfe;
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.format-hint p {
  color: #a0b3c6;
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.format-table {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.8rem;
}

.format-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.4rem 0.8rem;
  background: rgba(30, 40, 70, 0.4);
  border-radius: 4px;
}

.format-column {
  color: #4facfe;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  min-width: 140px;
  font-size: 0.85rem;
}

.format-desc {
  color: #a0b3c6;
  font-size: 0.85rem;
}

/* 上传区域 */
.upload-area {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  padding: 1rem;
  background: rgba(30, 40, 70, 0.4);
  border-radius: 6px;
}

.upload-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex: 1;
}

.upload-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.file-name {
  color: #4ade80;
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
  background: rgba(74, 222, 128, 0.1);
  border-radius: 4px;
  border: 1px solid rgba(74, 222, 128, 0.3);
}

.extract-btn {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.error-message {
  margin-top: 1rem;
  padding: 0.8rem 1rem;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.5);
  border-radius: 6px;
  color: #f87171;
  font-size: 0.9rem;
  white-space: pre-line;
}

/* 多航班控制面板 */
.multi-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  padding: 1rem;
  background: rgba(20, 30, 60, 0.6);
  border-radius: 8px;
  margin-bottom: 1.5rem;
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

.control-group select {
  padding: 0.5rem 1rem;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 6px;
  color: #e0e0e0;
  cursor: pointer;
}

.control-group select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn {
  padding: 0.5rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(100, 116, 139, 0.8);
  color: #ffffff;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.primary {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.action-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

.action-btn.danger {
  background: rgba(239, 68, 68, 0.8);
}

.btn-icon {
  font-size: 1rem;
}

/* 统计卡片 */
.multi-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: rgba(30, 40, 70, 0.6);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}

.stat-label {
  font-size: 0.85rem;
  color: #a0b3c6;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
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

/* 多航班可视化 */
.multi-visualization {
  background: rgba(10, 20, 40, 0.7);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.multi-canvas {
  max-width: 100%;
  height: auto;
  border: 2px solid rgba(64, 224, 255, 0.5);
  border-radius: 4px;
  background: #0a1428;
  box-shadow: 0 0 20px rgba(64, 224, 255, 0.3);
  cursor: grab;
}

.multi-canvas:active {
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

.canvas-controls-mini {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: center;
  margin-top: 0.8rem;
  padding: 0.5rem 1rem;
  background: rgba(20, 30, 60, 0.6);
  border-radius: 5px;
  border: 1px solid rgba(64, 224, 255, 0.3);
}

.mini-btn {
  padding: 0.4rem 0.8rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mini-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(79, 172, 254, 0.4);
}

.info-text {
  color: #a0b3c6;
  font-size: 0.9rem;
}

.canvas-legend {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 20, 40, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(79, 172, 254, 0.2);
}

.legend-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.legend-title {
  color: #4facfe;
  font-size: 0.85rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #a0b3c6;
  font-size: 0.85rem;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.standpoint {
  background: #00bcd4;
}

.legend-dot.runway {
  background: #ff9800;
}

.legend-dot.departure {
  background: #ff69b4;
}

.legend-dot.arrival {
  background: #4facfe;
}

.legend-dot.conflict {
  background: rgba(255, 0, 0, 0.6);
  box-shadow: 0 0 8px rgba(255, 0, 0, 0.8);
}

.legend-circle-filled {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #4facfe;
}

.legend-circle-hollow {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #4facfe;
  background: transparent;
}

.legend-text {
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: bold;
  font-family: Arial, sans-serif;
  background: rgba(79, 172, 254, 0.3);
  padding: 2px 6px;
  border-radius: 3px;
}

/* 航班列表 */
.flights-list {
  margin-bottom: 1.5rem;
}

.flights-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.flights-list h4 {
  color: #4facfe;
  margin: 0;
}

.flight-controls {
  display: flex;
  gap: 0.8rem;
  align-items: center;
}

.selected-count {
  color: #4facfe;
  font-size: 0.9rem;
  padding: 0.4rem 0.8rem;
  background: rgba(79, 172, 254, 0.1);
  border-radius: 4px;
  font-weight: 500;
}

.select-btn {
  padding: 0.4rem 0.8rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.select-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(79, 172, 254, 0.4);
}

.select-btn.clear {
  background: rgba(100, 116, 139, 0.8);
}

.select-btn.clear:hover {
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.4);
}

/* 航班表格容器 */
.flight-table-container {
  width: 800px;
  max-width: 100%;
  max-height: 300px;
  overflow: auto;
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 8px;
  background: rgba(10, 20, 40, 0.5);
}

/* 航班表格 */
.flight-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.flight-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
}

.flight-table th {
  background: rgba(30, 40, 70, 0.9);
  color: #4facfe;
  font-weight: 600;
  text-align: left;
  padding: 0.8rem 0.6rem;
  border-bottom: 2px solid rgba(64, 224, 255, 0.5);
  white-space: nowrap;
}

.flight-table th.col-checkbox {
  width: 40px;
  text-align: center;
}

.flight-table th.col-flight-id {
  width: 80px;
}

.flight-table th.col-type {
  width: 60px;
}

.flight-table th.col-operation {
  width: 50px;
}

.flight-table th.col-time {
  width: 60px;
}

.flight-table th.col-distance {
  width: 70px;
}

.flight-table th.col-delay {
  width: 70px;
}

.flight-table th.col-action {
  width: 90px;
}

.flight-table tbody tr {
  background: rgba(20, 30, 60, 0.6);
  border-bottom: 1px solid rgba(64, 224, 255, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.flight-table tbody tr:hover {
  background: rgba(30, 40, 70, 0.8);
  border-color: rgba(64, 224, 255, 0.4);
}

.flight-table tbody tr.selected {
  background: rgba(79, 172, 254, 0.15);
  border-left: 3px solid #4facfe;
}

.flight-table tbody tr.has-conflict {
  border-left: 3px solid #f87171;
}

.flight-table tbody tr.has-delay {
  border-left: 3px solid #fbbf24;
}

.flight-table tbody tr.success {
  border-left: 3px solid #4ade80;
}

.flight-table td {
  padding: 0.6rem;
  color: #e0e0e0;
  border-bottom: 1px solid rgba(64, 224, 255, 0.1);
}

.flight-table td.col-checkbox {
  text-align: center;
}

.flight-table input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #4facfe;
}

.flight-table input[type="checkbox"]:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.flight-table .col-flight-id {
  font-weight: 600;
  color: #ffffff;
}

.flight-table .col-operation.departure {
  color: #4facfe;
}

.flight-table .col-operation.arrival {
  color: #4ade80;
}

.flight-table .col-delay.has-delay {
  color: #fbbf24;
}

.flight-table .col-distance,
.flight-table .col-delay {
  text-align: right;
  font-family: 'Courier New', monospace;
}

/* 查看备选路径按钮 */
.view-alternatives-btn {
  padding: 0.3rem 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.view-alternatives-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4);
}

/* 冲突列表 */
.conflicts-list {
  margin-bottom: 1.5rem;
}

.conflicts-list h4 {
  color: #f87171;
  margin-bottom: 1rem;
}

.conflict-cards {
  display: grid;
  gap: 0.8rem;
}

.conflict-card {
  background: rgba(30, 40, 70, 0.6);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 8px;
  padding: 1rem;
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
  margin-bottom: 0.5rem;
}

.conflict-type {
  font-weight: 600;
  color: #ffffff;
}

.conflict-severity {
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
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

.conflict-info {
  color: #a0b3c6;
  font-size: 0.85rem;
}

.back-btn {
  display: block;
  margin: 1.5rem auto;
  padding: 0.8rem 2rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
}

@media (max-width: 768px) {
  .algorithm-title {
    font-size: 1.5rem;
  }

  .algorithm-content {
    padding: 1rem;
  }

  .tab-buttons {
    flex-direction: column;
  }

  .main-tab-buttons {
    flex-direction: column;
  }

  .main-tab-btn {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
  }

  .multi-controls {
    flex-direction: column;
  }

  .multi-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .flight-table-container {
    width: 100%;
    max-height: 300px;
  }

  .flight-table {
    font-size: 0.75rem;
  }

  .flight-table th,
  .flight-table td {
    padding: 0.4rem 0.3rem;
  }

  .path-alternatives-sidebar {
    width: 100%;
    max-height: 50vh;
    top: auto;
    bottom: 0;
    transform: none;
    border-radius: 12px 12px 0 0;
    border-left: none;
    border-top: 1px solid rgba(64, 224, 255, 0.3);
  }

  .slide-enter-from,
  .slide-leave-to {
    transform: translateY(100%);
  }
}

/* 备选路径侧边栏 */
.path-alternatives-sidebar {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  width: 300px;
  max-height: 70vh;
  background: rgba(20, 30, 60, 0.95);
  border-left: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 12px 0 0 12px;
  backdrop-filter: blur(10px);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  box-shadow: -5px 0 20px rgba(0, 0, 0, 0.3);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(64, 224, 255, 0.3);
  background: rgba(30, 40, 70, 0.5);
}

.sidebar-header h3 {
  color: #4facfe;
  margin: 0;
  font-size: 1.1rem;
}

.close-btn {
  background: none;
  border: none;
  color: #a0b3c6;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.selected-flight-info {
  margin-bottom: 1rem;
  padding: 0.8rem;
  background: rgba(30, 40, 70, 0.6);
  border-radius: 8px;
  border: 1px solid rgba(64, 224, 255, 0.3);
}

.selected-flight-info h4 {
  color: #4facfe;
  margin: 0 0 0.6rem 0;
  font-size: 1rem;
}

.flight-details {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 0.4rem;
  flex-wrap: wrap;
}

.detail-item {
  padding: 0.2rem 0.5rem;
  background: rgba(64, 224, 255, 0.1);
  border-radius: 4px;
  font-size: 0.75rem;
  color: #4facfe;
}

.route-info {
  color: #a0b3c6;
  font-size: 0.8rem;
}

.preview-controls {
  padding: 0.6rem 0.8rem;
  margin-bottom: 0.8rem;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  border-radius: 6px;
  text-align: center;
}

.cancel-preview-btn {
  padding: 0.4rem 0.8rem;
  background: rgba(248, 113, 113, 0.8);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.cancel-preview-btn:hover {
  background: rgba(248, 113, 113, 1);
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(248, 113, 113, 0.4);
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  color: #a0b3c6;
  font-size: 0.85rem;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(79, 172, 254, 0.3);
  border-top-color: #4facfe;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.8rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.alternatives-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.alternative-card {
  background: rgba(30, 40, 70, 0.6);
  border: 2px solid rgba(64, 224, 255, 0.3);
  border-radius: 8px;
  padding: 0.8rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.alternative-card:hover {
  border-color: rgba(64, 224, 255, 0.5);
  background: rgba(30, 40, 70, 0.8);
}

.alternative-card.active {
  border-color: #4facfe;
  background: rgba(79, 172, 254, 0.15);
  box-shadow: 0 0 15px rgba(79, 172, 254, 0.3);
}

.alternative-card.recommended {
  border-color: rgba(74, 222, 128, 0.5);
}

.alt-header {
  margin-bottom: 0.6rem;
}

.alt-rank {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.alt-rank input[type="radio"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #4facfe;
}

.alt-rank label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 500;
  font-size: 0.85rem;
  color: #ffffff;
  cursor: pointer;
}

.badge {
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
}

.badge.recommended {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
  border: 1px solid rgba(74, 222, 128, 0.5);
}

.badge.detour {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.5);
}

.alt-stats {
  margin-bottom: 0.6rem;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 0.3rem 0;
  font-size: 0.8rem;
}

.stat-label {
  color: #a0b3c6;
}

.stat-value {
  color: #ffffff;
  font-weight: 500;
}

.alt-actions {
  display: flex;
  gap: 0.4rem;
}

.preview-btn,
.apply-btn {
  flex: 1;
  padding: 0.4rem 0.6rem;
  border: none;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.preview-btn {
  background: rgba(100, 116, 139, 0.8);
  color: #ffffff;
}

.preview-btn:hover:not(:disabled) {
  background: rgba(100, 116, 139, 1);
  transform: translateY(-1px);
}

.preview-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.apply-btn {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.apply-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

.apply-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-alternatives {
  text-align: center;
  padding: 2rem 1rem;
  color: #a0b3c6;
  font-size: 0.85rem;
}

/* 侧边栏动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translate(100%, -50%);
  opacity: 0;
}

/* 滚动条样式 */
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: rgba(20, 30, 60, 0.3);
  border-radius: 4px;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: rgba(64, 224, 255, 0.3);
  border-radius: 4px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: rgba(64, 224, 255, 0.5);
}

/* 航班表格滚动条样式 */
.flight-table-container::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.flight-table-container::-webkit-scrollbar-track {
  background: rgba(20, 30, 60, 0.3);
  border-radius: 4px;
}

.flight-table-container::-webkit-scrollbar-thumb {
  background: rgba(64, 224, 255, 0.3);
  border-radius: 4px;
}

.flight-table-container::-webkit-scrollbar-thumb:hover {
  background: rgba(64, 224, 255, 0.5);
}

@media (max-width: 768px) {
  .path-alternatives-sidebar {
    width: 100%;
    right: 0;
  }
}

/* 时间段与权重信息样式 */
.period-weight-section {
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: rgba(20, 30, 60, 0.6);
  border: 1px solid rgba(64, 224, 255, 0.3);
  border-radius: 8px;
}

.period-weight-section h4 {
  color: #4facfe;
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
}

.period-weight-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.period-analysis {
  background: rgba(30, 40, 70, 0.4);
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid rgba(79, 172, 254, 0.2);
}

.period-summary {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.period-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(64, 224, 255, 0.1);
}

.period-item:last-child {
  border-bottom: none;
}

.period-label {
  color: #a0b3c6;
  font-size: 0.9rem;
}

.period-value {
  color: #ffffff;
  font-weight: 500;
  font-size: 0.9rem;
}

.weight-config {
  background: rgba(30, 40, 70, 0.4);
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid rgba(79, 172, 254, 0.2);
}

.weight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.weight-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4facfe;
  font-size: 1rem;
  font-weight: 600;
}

.weight-mode {
  color: #a0b3c6;
  font-size: 0.85rem;
  font-weight: 400;
}

.weight-controls {
  display: flex;
  gap: 0.5rem;
}

.weight-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.weight-btn.auto {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.weight-btn.auto:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

.weight-btn.auto:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.weight-btn.manual {
  background: rgba(100, 116, 139, 0.8);
  color: #ffffff;
}

.weight-btn.manual:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(100, 116, 139, 0.4);
}

.weight-btn.manual:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.weight-values {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-bottom: 1rem;
}

.weight-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 6px;
  border: 1px solid rgba(64, 224, 255, 0.2);
}

.weight-label {
  color: #a0b3c6;
  font-size: 0.9rem;
  min-width: 80px;
}

.weight-value {
  color: #ffffff;
  font-weight: 600;
  font-size: 1.1rem;
  min-width: 40px;
  text-align: center;
}

.weight-desc {
  color: #4facfe;
  font-size: 0.85rem;
  margin-left: auto;
}

.weight-description {
  padding: 0.8rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 6px;
  border: 1px solid rgba(64, 224, 255, 0.1);
}

.weight-description p {
  color: #a0b3c6;
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.5;
}

/* 当前时段状态指示器 */
.period-status-indicator {
  margin: 1rem 0;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.period-status-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  border: 2px solid;
  transition: all 0.3s ease;
}

.period-status-content.peak {
  background: linear-gradient(135deg, rgba(248, 113, 113, 0.15) 0%, rgba(239, 68, 68, 0.1) 100%);
  border-color: rgba(248, 113, 113, 0.5);
  box-shadow: 0 4px 15px rgba(248, 113, 113, 0.2);
}

.period-status-content.off-peak {
  background: linear-gradient(135deg, rgba(74, 222, 128, 0.15) 0%, rgba(34, 197, 94, 0.1) 100%);
  border-color: rgba(74, 222, 128, 0.5);
  box-shadow: 0 4px 15px rgba(74, 222, 128, 0.2);
}

.period-status-content.normal {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.1) 100%);
  border-color: rgba(251, 191, 36, 0.5);
  box-shadow: 0 4px 15px rgba(251, 191, 36, 0.2);
}

.period-status-icon {
  font-size: 2rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.period-status-text {
  flex: 1;
}

.period-status-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.period-status-content.peak .period-status-title {
  color: #f87171;
}

.period-status-content.off-peak .period-status-title {
  color: #4ade80;
}

.period-status-content.normal .period-status-title {
  color: #fbbf24;
}

.period-status-desc {
  font-size: 0.9rem;
  color: #a0b3c6;
  margin-bottom: 0.5rem;
}

.period-weights-detail {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.85rem;
  color: #cbd5e1;
}

.period-weights-detail strong {
  color: #ffffff;
  font-weight: 600;
}

.weight-separator {
  color: #64748b;
}

.period-indicator {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-left: 0.5rem;
}

.period-indicator.peak {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
  border: 1px solid rgba(248, 113, 113, 0.5);
}

.period-indicator.off-peak {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
  border: 1px solid rgba(74, 222, 128, 0.5);
}

.period-indicator.normal {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.5);
}

@media (max-width: 768px) {
  .period-weight-content {
    flex-direction: column;
  }

  .period-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.3rem;
  }

  .weight-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
