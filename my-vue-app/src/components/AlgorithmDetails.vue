<template>
  <div class="algorithm-details">
    <div class="intro-section">
      <h3>算法简介</h3>
      <p>多目标A*算法（Multi-Objective A*）是经典A*算法的扩展，用于在多个优化目标（如最短距离、最少时间、最低燃油消耗）之间寻找最优平衡解。在机场多航班调度场景中，该算法不仅为单个航班规划路径，还考虑多个航班之间的协同调度，避免冲突并优化整体运行效率。</p>
    </div>

    <div class="features-section">
      <h3>算法特点</h3>
      <ul>
        <li>多目标优化：同时考虑距离、时间、燃油消耗等多个优化指标</li>
        <li>冲突避免：内置冲突检测机制，预测并避免航班间的时空冲突</li>
        <li>动态适应性：支持实时航班调度调整，应对突发情况</li>
        <li>协同优化：考虑多个航班之间的相互影响，实现整体最优</li>
      </ul>
    </div>

    <div class="application-section">
      <h3>机场多航班调度应用</h3>
      <p>在机场场面滑行轨迹优化中，多目标A*算法结合多航班调度可用于：</p>
      <ul>
        <li>为多个航班同时规划最优滑行路径，考虑离港和进港的不同需求</li>
        <li>避免航班之间的冲突（节点冲突、边冲突、交叉冲突）</li>
        <li>平衡多个优化目标：总滑行距离最短、总延误最小、燃油消耗最少</li>
        <li>支持不同的调度策略：先来先服务（FCFS）、优先级调度、时间窗调度</li>
        <li>提供备选路径方案，应对突发情况或管制员手动调整</li>
      </ul>
    </div>

    <div class="technical-section">
      <h3>技术实现</h3>
      <ul>
        <li><strong>启发函数扩展</strong>：传统A*的启发函数扩展为多目标向量，评估多个成本维度</li>
        <li><strong>冲突检测算法</strong>：基于时空轨迹预测，检测航班间的潜在冲突点</li>
        <li><strong>协同调度引擎</strong>：整合路径规划和调度决策，实现全局优化</li>
        <li><strong>实时可视化</strong>：提供交互式界面，展示路径规划结果和冲突情况</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlgorithmDetails',
  data() {
    return {}
  }
}
</script>

<style scoped>
.algorithm-details {
  background: rgba(30, 40, 70, 0.4);
  border-radius: 8px;
  padding: 1.5rem;
}

.intro-section, .features-section, .application-section, .technical-section {

  padding: 1.5rem;
  background: rgba(30, 40, 70, 0.4);
  border-radius: 8px;
}

.intro-section h3, .features-section h3, .application-section h3, .technical-section h3 {
  font-size: 1.4rem;
  margin-bottom: 1rem;
  color: #4facfe;
}

.intro-section p, .features-section ul, .application-section ul, .technical-section ul {
  color: #a0b3c6;
  line-height: 1.6;
}

.features-section li, .application-section li, .technical-section li {
  margin: 0.5rem 0;
  padding-left: 1rem;
}

.technical-section li {
  margin: 0.8rem 0;
}

.technical-section strong {
  color: #4facfe;
}
</style>