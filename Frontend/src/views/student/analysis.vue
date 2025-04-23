<template>
  <div class="student-info">
    <div class="box box-1">容器 1</div>
    <div class="box box-2">容器 2</div>
    <div class="box box-3">容器 3</div>
    <div class="box box-4">容器 4</div>
  </div>
</template>

<script>
export default {
  name: 'StudentInfo'

};
</script>

<style scoped>

.student-info   {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 创建两列 */
  grid-template-rows: 1fr 1fr; /* 创建两行 */
  height: 100vh; /* 设置容器高度为视口高度 */
  gap: 10px; /* 设置网格项目之间的间距 */
  padding: 10px; /* 可选：添加内边距 */
}

.box {
  padding: 20px;
  border: 1px solid #ccc;
  box-sizing: border-box; /* 包括边框和内边距在内的尺寸计算 */
}

.box-1 {
  /* 特定于 box-1 的样式 */
  background-color: #f0f0f0;
}

.box-2 {
  /* 特定于 box-2 的样式 */
  background-color: #e0f0f0;
}

.box-3 {
  /* 特定于 box-3 的样式 */
  background-color: #d0e0e0;
}

.box-4 {
  /* 特定于 box-4 的样式 */
  background-color: #c0d0c0;
}
</style>