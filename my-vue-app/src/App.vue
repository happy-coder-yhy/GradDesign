<template>
  <div id="app">
    <div class="grid-background"></div>
    <div class="particles"></div>
    
    <header class="header">
      <div class="container">
        <h1 class="title">机场场面滑行轨迹优化系统</h1>
        <p class="subtitle">智能优化飞机滑行路径，提升机场运行效率</p>
      </div>
    </header>
    
    <main class="main-content">
      <router-view />
    </main>
    
    <footer class="footer">
      <div class="container">
        <p>&copy; 2026 机场场面滑行轨迹优化系统 | 民航智能化解决方案</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  color: #e0e0e0;
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
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
}

.header {
  background: rgba(10, 15, 47, 0.85);
  backdrop-filter: blur(10px);
  color: white;
  padding: 2rem 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(64, 224, 255, 0.3);
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
}

.main-content {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
}

.footer {
  background: rgba(10, 15, 47, 0.85);
  color: #a0b3c6;
  text-align: center;
  padding: 1.5rem 0;
  margin-top: 2rem;
  border-top: 1px solid rgba(64, 224, 255, 0.3);
  backdrop-filter: blur(10px);
}

@media (max-width: 768px) {
  .title {
    font-size: 1.8rem;
  }
}
</style>