<template>
  <div class="app-container">
    <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">
      
      <el-menu-item index="/function1"><el-icon><Memo /></el-icon>教案生成</el-menu-item>
      <el-menu-item index="/function2"><el-icon><Tickets /></el-icon>逐字稿生成</el-menu-item>
      <el-menu-item index="/function3" ><el-icon><Monitor /></el-icon>PPT生成</el-menu-item>
      <el-menu-item index="/function4" ><el-icon><DataLine /></el-icon>班会稿策划</el-menu-item>
      <el-menu-item index="/function5" ><el-icon><DataLine /></el-icon>智能出题</el-menu-item>
      <el-menu-item index="/function6" ><el-icon><DataLine /></el-icon>主观题批阅</el-menu-item>
      <el-menu-item index="/function7" ><el-icon><DataLine /></el-icon>作业辅导</el-menu-item>
      <el-menu-item index="/function8" ><el-icon><DataLine /></el-icon>AI学习计划</el-menu-item>
      <!--<el-menu-item index="/function9" ><el-icon><DataLine /></el-icon>知识点梳理</el-menu-item>  -->
      <!--<el-menu-item index="/student" ><el-icon><DataLine /></el-icon>学生个性化报告</el-menu-item>-->
      <el-menu-item index="/Knowledge_Organization" ><el-icon><DataLine /></el-icon>知识点梳理</el-menu-item>
    </el-menu>
    <router-view />
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Tickets,Memo,DataLine,Monitor } from '@element-plus/icons-vue'
const router = useRouter()
const route = useRoute()
const activeIndex = ref(route.path)
// const activeIndex = ref("Home.vue")

const handleSelect = (key: string, keyPath: string[]) => {
  router.push(key)
  console.log(key, keyPath)
}

</script>

