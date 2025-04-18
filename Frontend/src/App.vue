<template>
  <div class="app-container">
    <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">
      
      <el-menu-item index="/function1"><el-icon><Memo /></el-icon>教案生成</el-menu-item>
      <el-menu-item index="/function2"><el-icon><Tickets /></el-icon>逐字稿生成</el-menu-item>
      <el-menu-item index="/function3" ><el-icon><Monitor /></el-icon>PPT生成</el-menu-item>
      <el-menu-item index="/function4" ><el-icon><DataLine /></el-icon>班会稿生成</el-menu-item>
      <el-menu-item index="/function5" ><el-icon><DataLine /></el-icon>智能出题</el-menu-item>
      <el-menu-item index="/function6"  disabled><el-icon><DataLine /></el-icon>主观题批阅</el-menu-item>

      <el-sub-menu index="-1">
        <template #title>测试1</template>
        <el-menu-item index="2-1">item one</el-menu-item>
        <el-menu-item index="2-2">item two</el-menu-item>
        <el-menu-item index="2-3">item three</el-menu-item>
        <el-sub-menu index="2-4">
          <template #title>item four</template>
          <el-menu-item index="2-4-1">item one</el-menu-item>
          <el-menu-item index="2-4-2">item two</el-menu-item>
          <el-menu-item index="2-4-3">item three</el-menu-item>
        </el-sub-menu>
      </el-sub-menu>
      <el-menu-item index="-2" disabled>测试2</el-menu-item>
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