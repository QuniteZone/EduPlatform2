const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false,
  // 测试测试测试123123123
  devServer: {
    proxy: {
      // /api：这是代理的前缀路径。所有以 /api 开头的请求都会被代理到指定的目标服务器。
      '/api': {
        // target：目标服务器的 URL。在这个例子中，所有以 /api 开头的请求都会被代理到 http://localhost:3000
        target: 'https://94686t61i9.zicp.fun',
        changeOrigin: true,
        // pathRewrite：路径重写规则。在这个例子中，'^/api': '' 表示将请求路径中的 /api 前缀去掉。例如，/api/generate 会被重写为 /generate。
        pathRewrite: { '^/api': '' },
      },
    },
  },
})