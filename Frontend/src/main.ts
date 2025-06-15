// import { createApp } from 'vue'
// import App from './App.vue'
// import router from './router'
// import store from './store'


import 'element-plus/dist/index.css'


import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import * as echarts from 'echarts'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
