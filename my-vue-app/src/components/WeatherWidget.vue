<template>
  <div class="weather-widget" :class="weatherLevelClass" :title="weatherTooltip">
    <span class="weather-icon">{{ weatherIcon }}</span>
    <span class="weather-temp">{{ weather.temperature }}°C</span>
    <span class="weather-desc">{{ weather.weather }}</span>
    <span class="weather-wind">{{ weather.windpower }}级</span>
    <span v-if="showFactor" class="weather-factor">×{{ weather.weather_factor }}</span>
    <span v-if="loading" class="loading-dot"></span>
  </div>
</template>

<script>
const API_BASE = 'http://localhost:5001/api';

export default {
  name: 'WeatherWidget',
  props: {
    showFactor: { type: Boolean, default: true }
  },
  data() {
    return {
      weather: {
        city: '西安市',
        weather: '晴',
        temperature: '--',
        windpower: '≤3',
        humidity: '50',
        weather_factor: 1.0,
        weather_level: 'normal',
        visibility_impact: 'none'
      },
      loading: false,
      refreshTimer: null
    };
  },
  computed: {
    weatherLevelClass() {
      return `level-${this.weather.weather_level}`;
    },
    weatherIcon() {
      const map = {
        '晴': '☀️', '多云': '⛅', '阴': '☁️', '少云': '🌤️',
        '阵雨': '🌦️', '小雨': '🌧️', '中雨': '🌧️', '大雨': '⛈️',
        '暴雨': '⛈️', '大暴雨': '⛈️', '特大暴雨': '⛈️', '雷阵雨': '⛈️',
        '小雪': '🌨️', '中雪': '🌨️', '大雪': '❄️', '暴雪': '❄️',
        '雨夹雪': '🌨️', '雾': '🌫️', '霾': '🌫️', '浮尘': '🌫️',
        '扬沙': '🌫️', '沙尘暴': '🌫️', '冰雹': '🧊',
        '龙卷风': '🌪️', '台风': '🌀'
      };
      return map[this.weather.weather] || '🌡️';
    },
    weatherTooltip() {
      const f = this.weather.weather_factor;
      let impact = f >= 0.95 ? '天气良好，正常滑行' :
                   f >= 0.80 ? '轻度影响，建议减速' :
                   f >= 0.60 ? '中度影响，需降低滑行速度' :
                   f >= 0.40 ? '严重影响，大幅减速并提高警惕' :
                               '极端天气，建议暂停滑行';
      return `西安实时天气 | ${this.weather.weather} ${this.weather.temperature}°C | 风速${this.weather.windpower}级 | 折扣系数 ${f} | ${impact}`;
    }
  },
  mounted() {
    this.fetchWeather();
    this.refreshTimer = setInterval(() => this.fetchWeather(), 10 * 60 * 1000);
  },
  beforeUnmount() {
    if (this.refreshTimer) clearInterval(this.refreshTimer);
  },
  methods: {
    async fetchWeather() {
      this.loading = true;
      try {
        const res = await fetch(`${API_BASE}/weather/current`);
        const data = await res.json();
        if (data.success && data.weather) {
          this.weather = { ...this.weather, ...data.weather };
        }
      } catch (err) {
        console.warn('[WeatherWidget] 获取天气失败:', err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.weather-widget {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 10px;
  border-radius: 4px;
  background: rgba(20, 40, 70, 0.5);
  border: 1px solid rgba(64, 224, 255, 0.12);
  font-size: 11px;
  line-height: 1;
  white-space: nowrap;
  transition: all 0.3s ease;
  cursor: default;
}
.weather-widget:hover {
  background: rgba(30, 60, 100, 0.6);
  border-color: rgba(64, 224, 255, 0.3);
}

/* 天气等级左边框指示 */
.weather-widget.level-normal  { border-left: 2px solid #52c41a; }
.weather-widget.level-moderate{ border-left: 2px solid #faad14; }
.weather-widget.level-severe  { border-left: 2px solid #fa8c16; }
.weather-widget.level-extreme { border-left: 2px solid #f5222d; }

.weather-icon {
  font-size: 14px;
  line-height: 1;
}
.weather-temp {
  font-weight: 600;
  color: #e0f0ff;
  font-family: monospace;
  font-size: 11px;
}
.weather-desc {
  color: #a0c4e8;
  font-size: 11px;
}
.weather-wind {
  color: #7a9bb8;
  font-size: 10px;
}
.weather-factor {
  padding: 0 4px;
  border-radius: 3px;
  background: rgba(64, 224, 255, 0.12);
  color: #40e0ff;
  font-family: monospace;
  font-size: 10px;
}
.loading-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: #40e0ff;
  animation: blink 1s infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
