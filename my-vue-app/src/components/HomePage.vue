<template>
  <div class="home-page">
    <header class="page-header">
      <div class="container">
        <h1 class="title">机场场面滑行轨迹优化系统</h1>
        <p class="subtitle">智能优化飞机滑行路径，提升机场运行效率</p>
      </div>
    </header>

    <main class="home-content">
      <section class="algorithm-selection">
        <div
          class="algorithm-card"
          @click="selectAlgorithm(currentAlgorithm)"
        >
          <div class="icon">{{ currentAlgorithm.icon }}</div>
          <h3>{{ currentAlgorithm.name }}</h3>
          <p>{{ currentAlgorithm.description }}</p>
        </div>
      </section>

      <section class="developer-info">
        <div class="info-card">
          <div class="info-content">
            <p><span class="label">姓名:</span> <span class="value">袁皓宇</span></p>
            <p><span class="label">专业:</span> <span class="value">计算机科学与技术</span></p>
            <p><span class="label">指导老师:</span> <span class="value">左海超</span></p>
          </div>
        </div>
      </section>
    </main>

    <footer class="page-footer">
      <div class="container">
        <p>&copy; 2026 机场场面滑行轨迹优化系统 | 民航智能化解决方案</p>
      </div>
    </footer>
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

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 页头 */
.page-header {
  background: rgba(10, 15, 47, 0.85);
  backdrop-filter: blur(10px);
  color: white;
  padding: 2rem 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(64, 224, 255, 0.3);
  flex-shrink: 0;
}

.title {
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 0.5rem;
  font-weight: 600;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 15px rgba(79, 172, 254, 0.3);
}

.subtitle {
  text-align: center;
  font-size: 1.1rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
  font-weight: 300;
  color: #a0b3c6;
}

/* 主体内容 */
.home-content {
  flex: 1;
  padding: 2rem 0;
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

/* 页脚 */
.page-footer {
  background: rgba(10, 15, 47, 0.85);
  color: #a0b3c6;
  text-align: center;
  padding: 1.5rem 0;
  border-top: 1px solid rgba(64, 224, 255, 0.3);
  backdrop-filter: blur(10px);
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .title {
    font-size: 1.8rem;
  }

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
