<template>
  <div class="chart-card" :style="{ background: background || color }">
    <div class="card-content">
      <p :style="{ fontSize: titleSize + 'px', margin: '0' }">{{ title }}</p>
      <h2 :style="{ fontSize: valueSize + 'px', margin: '0' }">{{ value }}</h2>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  value: { type: [Number, String], required: true },
  color: { type: String, required: true },
  background: { type: String, default: '' }, // 新增属性
  titleSize: { type: [Number, String], default: 14 },
  valueSize: { type: [Number, String], default: 20 }
});
</script>

<style scoped>
.chart-card {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 70px;
  border-radius: 8px;
  color: #fff;
  width: 100%;
}

.card-content {
  text-align: center;
  font-weight: bold;
}
</style>
