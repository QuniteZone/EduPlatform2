
import 'element-plus/dist/index.css'
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import * as echarts from 'echarts'

const app = createApp(App)

// 使用 ElementPlus
app.use(ElementPlus)

// 注册所有 ElementPlus 图标为全局组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 挂载 ECharts 到全局属性（方便在组件中通过 this.$echarts 调用）
app.config.globalProperties.$echarts = echarts

// 使用路由
app.use(router)

// 挂载应用
app.mount('#app')