<template>
  <div class="home-content">
    <section class="algorithm-selection">
      <!-- A*算法卡片 -->
      <div
        class="algorithm-card"
        @click="selectAlgorithm(currentAlgorithm)"
      >
        <div class="icon">{{ currentAlgorithm.icon }}</div>
        <h3>{{ currentAlgorithm.name }}</h3>
        <p>{{ currentAlgorithm.description }}</p>
      </div>
    </section>

    <!-- 开发者信息 -->
    <section class="developer-info">
      <div class="info-card">
        <div class="info-content">
          <p><span class="label">姓名:</span> <span class="value">袁皓宇</span></p>
          <p><span class="label">专业:</span> <span class="value">计算机科学与技术</span></p>
          <p><span class="label">指导老师:</span> <span class="value">左海超</span></p>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  data() {
    return {
      currentAlgorithm: {
        name: '多目标A*算法+多航班调度机制+2D可视化',
        description: '基于多目标A*算法的机场场面滑行轨迹优化，集成多航班调度策略，实现冲突检测与消解，提供2D可视化演示',
        icon: '✈️',
        id: 'astar'
      }
    }
  },
  methods: {
    selectAlgorithm(algorithm) {
      this.$router.push({ name: algorithm.id });
    }
  }
}
</script>

<style>
.home-content {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
}

.algorithm-selection {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
}



.algorithm-card {
  background: rgba(20, 30, 60, 0.6);
  border-radius: 10px;
  padding: 2.5rem 3rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: all 0.4s ease;
  cursor: pointer;
  text-align: center;
  border: 1px solid rgba(64, 224, 255, 0.2);
  backdrop-filter: blur(5px);
  position: relative;
  overflow: hidden;
  max-width: 850px;
  width: 100%;
}

.algorithm-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(79, 192, 234, 0.2),
    transparent
  );
  transition: 0.5s;
}

.algorithm-card:hover::before {
  left: 100%;
}

.algorithm-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 35px rgba(0, 100, 255, 0.2);
  border: 1px solid rgba(64, 224, 255, 0.5);
}

.algorithm-card .icon {
  font-size: 3.5rem;
  margin-bottom: 1.2rem;
}

.algorithm-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1.2rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.algorithm-card p {
  color: #a0b3c6;
  line-height: 1.6;
  max-width: 550px;
  margin: 0 auto;
  font-size: 1.05rem;
}

.developer-info {
  margin-top: 1px;
  text-align: center;
}

.info-card {
  background: rgba(20, 30, 60, 0.6);
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(64, 224, 255, 0.2);
  backdrop-filter: blur(5px);
  max-width: 600px;
  margin: 0 auto;
}

.info-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.info-content {
  text-align: left;
}

.info-content p {
  margin: 0.8rem 0;
  padding: 0.5rem 1rem;
  background: rgba(30, 40, 70, 0.4);
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
}

.label {
  font-weight: bold;
  color: #4facfe;
  min-width: 80px;
}

.value {
  color: #e0e0e0;
  flex: 1;
  text-align: right;
}

@media (max-width: 768px) {
  .algorithm-card {
    max-width: 90%;
    padding: 2rem 1.5rem;
  }

  .algorithm-card .icon {
    font-size: 3rem;
  }

  .algorithm-card h3 {
    font-size: 1.4rem;
  }

  .algorithm-card p {
    font-size: 1rem;
    max-width: 100%;
  }

  .info-content p {
    flex-direction: column;
    align-items: flex-start;
  }

  .label {
    margin-bottom: 0.3rem;
  }

  .value {
    text-align: left;
  }
}
</style>