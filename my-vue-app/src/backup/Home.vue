<template>
  <div class="home-content">
    <section class="algorithm-selection">
      <h2>请选择优化算法</h2>
      <div class="algorithm-grid">
        <div 
          v-for="(algo, index) in algorithms" 
          :key="index" 
          class="algorithm-card"
          @click="selectAlgorithm(algo)"
        >
          <div class="icon">{{ algo.icon }}</div>
          <h3>{{ algo.name }}</h3>
          <p>{{ algo.description }}</p>
        </div>
      </div>
    </section>
    
    <!-- 开发者信息 -->
    <section class="developer-info">
      <div class="info-card">
        <h3>开发者信息</h3>
        <div class="info-content">
          <p><span class="label">姓名:</span> <span class="value">许培红</span></p>
          <p><span class="label">专业:</span> <span class="value">计算机科学与技术</span></p>
          <p><span class="label">指导老师:</span> <span class="value">张三教授</span></p>
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
      algorithms: [
        {
          name: 'A*算法',
          description: '基于启发式的路径搜索算法，适用于静态环境下的最优路径规划',
          icon: '🌟',
          id: 'astar'
        },
        {
          name: '遗传算法',
          description: '模拟自然进化过程的全局优化算法，适用于复杂约束条件',
          icon: '🧬',
          id: 'genetic'
        },
        {
          name: '混合整数动态规划',
          description: '结合离散与连续变量的优化方法，处理多阶段决策问题',
          icon: '📊',
          id: 'mixed-integer'
        }
      ]
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
  margin-bottom: 3rem;
  text-align: center;
}

.algorithm-selection h2 {
  font-size: 1.8rem;
  margin-bottom: 2rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  position: relative;
  display: inline-block;
}

.algorithm-selection h2::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 3px;
}

.algorithm-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.algorithm-card {
  background: rgba(20, 30, 60, 0.6);
  border-radius: 10px;
  padding: 2rem 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: all 0.4s ease;
  cursor: pointer;
  text-align: center;
  border: 1px solid rgba(64, 224, 255, 0.2);
  backdrop-filter: blur(5px);
  position: relative;
  overflow: hidden;
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
  font-size: 3rem;
  margin-bottom: 1rem;
}

.algorithm-card h3 {
  font-size: 1.4rem;
  margin-bottom: 1rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.algorithm-card p {
  color: #a0b3c6;
  line-height: 1.6;
}

.developer-info {
  margin-top: 2rem;
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
  .algorithm-grid {
    grid-template-columns: 1fr;
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