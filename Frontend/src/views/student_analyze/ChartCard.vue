<template>
  <div class="chart-card" :style="{ backgroundColor: color }">
    <div class="card-content">
      <p>{{ title }}</p>
      <h2>{{title==="做题正确率"?Math.floor(value*100)+'%':Math.floor(value) }}</h2>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: String,
    required: true,
  },
  color: {
    type: String,
    required: true,
  },
});


</script>

<style scoped>
.chart-card {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  border-radius: 16px;
  color: #fff;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15); /* 添加阴影效果 */
  position: relative;
  overflow: hidden;
}

.card-content {
  text-align: center;
  font-weight: bold;
  padding: 10px; /* 添加内边距 */
}

.chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05)); /* 添加渐变效果 */
  z-index: 1; /* 确保渐变层位于背景色之上 */
}

.card-content {
  position: relative;
  z-index: 2; /* 确保内容位于渐变层之上 */
}

h2 {
  font-size: 2.5em; /* 调整字体大小 */
  margin: 10px 0; /* 调整边距 */
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* 添加文字阴影 */
}

p {
  font-size: 1em; /* 调整字体大小 */
  margin: 0; /* 调整边距 */
  opacity: 0.9; /* 调整文字透明度 */
}
</style>