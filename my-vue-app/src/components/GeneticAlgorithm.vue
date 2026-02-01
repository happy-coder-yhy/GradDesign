<template>
  <div class="algorithm-detail">
    <div class="grid-background"></div>
    <div class="particles"></div>
    <div class="container">
      <h2 class="algorithm-title">遗传算法详情</h2>
      <div class="algorithm-content">
        <div class="intro-section">
          <h3>算法简介</h3>
          <p>遗传算法（Genetic Algorithm, GA）是一种模拟自然界生物进化过程的随机搜索算法。它基于达尔文的进化论，通过模拟遗传、交叉、变异等生物进化过程来求解优化问题。</p>
        </div>
        
        <div class="features-section">
          <h3>算法特点</h3>
          <ul>
            <li>模拟自然选择和遗传学原理的随机搜索算法</li>
            <li>对所求解的问题没有限制，不需要导数信息</li>
            <li>适合解决复杂的非线性优化问题</li>
            <li>能够处理多个约束条件和多目标优化</li>
          </ul>
        </div>
        
        <div class="application-section">
          <h3>机场滑行应用</h3>
          <p>在机场场面滑行轨迹优化中，遗传算法可用于：</p>
          <ul>
            <li>优化多架飞机的滑行路径，避免冲突</li>
            <li>平衡滑行时间、燃油消耗、安全性等多个目标</li>
            <li>处理复杂的机场约束条件（滑行道容量、安全距离等）</li>
          </ul>
        </div>
        
        <div class="visualization-section">
          <h3>算法演示</h3>
          <div class="visualization-area">
            <div class="population-container">
              <div class="chromosome" v-for="(chrom, idx) in population" :key="idx">
                <span class="gene" v-for="(gene, gIdx) in chrom" :key="gIdx" 
                      :class="{ selected: gene.selected }">
                  {{ gene.value }}
                </span>
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
  name: 'GeneticAlgorithm',
  data() {
    return {
      population: []
    };
  },
  mounted() {
    this.generatePopulation();
  },
  methods: {
    goBack() {
      this.$router.push('/');
    },
    generatePopulation() {
      // 生成示例种群数据用于可视化
      this.population = [];
      for (let i = 0; i < 6; i++) {
        const chromosome = [];
        for (let j = 0; j < 10; j++) {
          chromosome.push({
            value: Math.floor(Math.random() * 10),
            selected: Math.random() > 0.7
          });
        }
        this.population.push(chromosome);
      }
    }
  }
}
</script>

<style>
.algorithm-detail {
  position: relative;
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
  overflow-x: hidden;
}

/* 网格背景 */
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

/* 粒子动画效果 */
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
  0% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(5px, 5px);
  }
  50% {
    transform: translate(0, 5px);
  }
  75% {
    transform: translate(-5px, 0);
  }
  100% {
    transform: translate(0, 0);
  }
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

.population-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chromosome {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.gene {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: rgba(64, 224, 255, 0.3);
  border-radius: 4px;
  font-weight: bold;
  color: white;
  border: 1px solid rgba(64, 224, 255, 0.5);
}

.gene.selected {
  background: rgba(76, 175, 80, 0.7);
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.8);
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
}
</style>