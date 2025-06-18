<script setup>
defineProps({
  name: {
    type: String,
    required: true,
  },
   s_class: {
    type: String,
    required: true,
  },
  id: {
    type: String,
    required: true,
  },
  school: {
    type: String,
    required: true,
  },
  major: {
    type: String,
    required: true,
  },

});
</script>

<template>
  <div class="info-card-container">
    <div class="info-card">
      <div class="card-header">
        <i class="el-icon-user"></i>
        <span>学生基本信息</span>
      </div>
      <div class="info-content">

         <div class="info-row">
          <div class="info-label">学号</div>
          <div class="info-value">{{ id }}</div>
        </div>
        <div class="info-row">
          <div class="info-label">班级</div>
          <div class="info-value">{{ s_class }}</div>
        </div>
        <div class="info-row">
          <div class="info-label">专业</div>
          <div class="info-value">{{ major }}</div>
        </div>
        <div class="info-row">
          <div class="info-label">学校</div>
          <div class="info-value">{{ school }}</div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.info-card-container {
  height: 100%;
}

.info-card {
  background: linear-gradient(145deg, #ffffff, #f5f7fa);
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  padding: 30px;
  transition: all 0.3s ease;
  border: 1px solid rgba(142, 200, 225, 0.2);
  height: 330px;
}

.info-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(142, 200, 225, 0.3);
}

.card-header i {
  font-size: 24px;
  color: #8ec8e1;
  margin-right: 12px;
}

.card-header span {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed rgba(142, 200, 225, 0.2);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  width: 100px;
  font-size: 15px;
  color: #666;
  font-weight: 500;
}

.info-value {
  flex: 1;
  font-size: 15px;
  color: #2c3e50;
  font-weight: 500;
  padding-left: 16px;
}

.info-value.address {
  color: #666;
  line-height: 1.5;
}






</style>