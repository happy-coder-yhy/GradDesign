const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8888
  },
  // 打包输出到后端项目的 static 目录
  outputDir: path.resolve(__dirname, '../GraduationDesign/static'),
  // 静态资源引用路径
  publicPath: '/',
  pages: {
    index: {
      entry: 'src/main.js',
      template: 'public/index.html',
      filename: 'index.html',
      title: '毕业设计 - 机场场面滑行轨迹优化系统'
    }
  }
})