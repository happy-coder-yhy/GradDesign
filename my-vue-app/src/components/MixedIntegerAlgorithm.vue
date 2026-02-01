<template>
  <div class="algorithm-detail">
    <div class="grid-background"></div>
    <div class="particles"></div>
    <div class="container">
      <h2 class="algorithm-title">混合整数动态规划算法详情</h2>
      <div class="algorithm-content">
        <div class="intro-section">
          <h3>算法简介</h3>
          <p>混合整数规划（Mixed Integer Programming, MIP）是一种数学优化或约束最优化问题，其中部分变量被限制为整数值。当目标函数和约束条件都是线性时，称为混合整数线性规划（MILP）。动态规划则是一种通过将复杂问题分解为子问题来求解的方法。</p>
        </div>
        
        <div class="features-section">
          <h3>算法特点</h3>
          <ul>
            <li>结合了整数规划和动态规划的优势</li>
            <li>能处理离散决策变量和连续变量的混合问题</li>
            <li>通过分层优化策略提高计算效率</li>
            <li>适用于多阶段决策问题</li>
          </ul>
        </div>
        
        <div class="application-section">
          <h3>机场滑行应用</h3>
          <p>在机场场面滑行轨迹优化中，混合整数动态规划算法可用于：</p>
          <ul>
            <li>优化多架飞机的滑行序列，减少冲突</li>
            <li>同时考虑离散决策（如滑行路径选择）和连续变量（如滑行速度）</li>
            <li>处理随时间变化的动态约束条件</li>
          </ul>
        </div>
        
        <div class="visualization-section">
          <h3>算法演示</h3>
          <div class="visualization-area">
            <div class="equation-container">
              <div class="equation-header">优化目标函数</div>
              <div class="equation-formula">
                min Σ(i∈N) Σ(t∈T) c_it · x_it + Σ(k∈K) f_k · y_k
              </div>
              <div class="constraints">
                <div class="constraint">约束条件:</div>
                <div class="constraint-item">Σ(t∈T) x_it = 1, ∀i∈N (每架飞机仅分配一条路径)</div>
                <div class="constraint-item">Σ(i∈N) a_ijk · x_it ≤ C_jk, ∀j,k (滑行道容量限制)</div>
                <div class="constraint-item">x_it ∈ {0,1}, y_k ∈ {0,1} (变量类型约束)</div>
              </div>
            </div>
            
            <div class="process-steps">
              <h4>算法执行步骤</h4>
              <div class="step" v-for="(step, index) in steps" :key="index">
                <div class="step-number">{{ index + 1 }}</div>
                <div class="step-content">
                  <h5>{{ step.title }}</h5>
                  <p>{{ step.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <button class="back-btn" @click="goBack">返回算法选择</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MixedIntegerAlgorithm',
  data() {
    return {
      steps: [
        {
          title: "问题建模",
          description: "建立混合整数规划模型，定义决策变量、目标函数和约束条件"
        },
        {
          title: "动态分解",
          description: "将多阶段决策问题分解为一系列子问题，降低计算复杂度"
        },
        {
          title: "分支定界",
          description: "使用分支定界算法求解整数变量，逐步逼近最优解"
        },
        {
          title: "动态规划优化",
          description: "在每个子问题中应用动态规划方法优化连续变量"
        },
        {
          title: "解的整合",
          description: "将各子问题的解整合为完整问题的最优解"
        }
      ]
    };
  },
  methods: {
    goBack() {
      this.$router.push('/');
    }
  }
}
</script>

<style>
.algorithm-detail {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
  position: relative;
  overflow-x: hidden;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

/* 网格背景 */
.grid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(64, 224, 255, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(64, 224, 255, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  z-index: 0;
}

/* 粒子效果 */
.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.particles::before,
.particles::after {
  content: '';
  position: absolute;
  width: 2px;
  height: 2px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  box-shadow: 
    0 0 10px rgba(64, 224, 255, 0.8),
    0 0 20px rgba(64, 224, 255, 0.5);
  animation: float 10s infinite ease-in-out;
}

.particles::before {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.particles::after {
  top: 60%;
  right: 10%;
  animation-delay: 5s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(0);
  }
  25% {
    transform: translateY(-20px) translateX(10px);
  }
  50% {
    transform: translateY(10px) translateX(-10px);
  }
  75% {
    transform: translateY(-10px) translateX(5px);
  }
}

.algorithm-title {
  font-size: 2rem;
  text-align: center;
  margin-bottom: 2rem;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
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

.visualization-area {
  background: rgba(10, 20, 40, 0.7);
  padding: 1.5rem;
  border-radius: 8px;
  overflow-x: auto;
}

.equation-container {
  margin-bottom: 2rem;
}

.equation-header {
  font-size: 1.2rem;
  font-weight: bold;
  color: #4facfe;
  margin-bottom: 1rem;
  text-align: center;
}

.equation-formula {
  font-family: 'Courier New', monospace;
  font-size: 1.1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 5px;
  text-align: center;
  margin: 1rem 0;
  color: #a0f0a0;
}

.constraints {
  margin-top: 1rem;
}

.constraint {
  font-weight: bold;
  color: #4facfe;
  margin-bottom: 0.5rem;
}

.constraint-item {
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
  margin: 0.3rem 0;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.process-steps {
  margin-top: 2rem;
}

.process-steps h4 {
  color: #4facfe;
  margin-bottom: 1rem;
  text-align: center;
}

.step {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding: 0.8rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 5px;
}

.step-number {
  width: 30px;
  height: 30px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 1rem;
  flex-shrink: 0;
}

.step-content h5 {
  color: #4facfe;
  margin-bottom: 0.3rem;
}

.step-content p {
  color: #a0b3c6;
  line-height: 1.4;
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
  
  .step {
    flex-direction: column;
  }
  
  .step-number {
    margin-bottom: 0.5rem;
    margin-right: 0;
  }
}
</style>