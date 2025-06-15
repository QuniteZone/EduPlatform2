<template>
  <div class="summary-card">
    <div class="icon-container">
      <i :class="`icon-${icon}`"></i>
    </div>
    <div class="content">
      <p class="title">{{ title }}</p>
      <p class="value">{{ value }}</p>
    </div>
  </div>
</template>

<style scoped>
.summary-card {
  display: flex;
  align-items: center;
  gap: 16px;
}
.icon-container {
  width: 48px;
  height: 48px;
  background: #007bff1a;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon {
  font-size: 24px;
  color: #007bff;
}
.content {
  flex: 1;
}
.title {
  color: #6c757d;
  margin-bottom: 4px;
}
.value {
  font-weight: 600;
  font-size: 18px;
}
</style>