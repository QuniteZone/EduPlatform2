const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false,
  // 测试测试测试123123123
  devServer: {
    host: '0.0.0.0', // 设置host为0.0.0.0，允许通过局域网访问
    port: 3000, // 开发服务器端口
    allowedHosts: 'all', // 允许所有主机（可能不安全）
    open: true, // 启动后自动打开浏览器

    proxy: {
      // /api：这是代理的前缀路径。所有以 /api 开头的请求都会被代理到指定的目标服务器。
      '/api': {
        // target：目标服务器的 URL。在这个例子中，所有以 /api 开头的请求都会被代理到 http://localhost:3000
        // target: 'https://fz68ok24676.vicp.fun',
        target:'http://192.168.122.16:5001',
        changeOrigin: true,
        // pathRewrite：路径重写规则。在这个例子中，'^/api': '' 表示将请求路径中的 /api 前缀去掉。例如，/api/generate 会被重写为 /generate。
        pathRewrite: { '^/api': '' },
      },
    },
  },
})