<script setup>
defineProps({
  goals: {
    type: Array,
    required: true,
  },
});
</script>

<template>
  <div class="learning-goals">
    <div class="goal-header">
      <span class="goal-title">学习建议</span>
    </div>
    <ul class="goals-list">
      <li v-for="(goal, index) in goals" :key="index" class="goal-item">
        <span class="check-icon">■</span>
        <span class="goal-text">{{ goal }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.learning-goals {
  width: 90%;
  max-width: 600px;
  margin: 5px auto;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  height: 345px;
  overflow: auto; /* 添加滚动条，防止子组件溢出 */
}
 /* 自定义滚动条样式 */
    .learning-goals::-webkit-scrollbar {
      width: 8px; /* 滚动条的宽度 */
    }

    .learning-goals::-webkit-scrollbar-track {
      background: transparent; /* 滚动条轨道的背景颜色 */
    }

    .learning-goals::-webkit-scrollbar-thumb {
      background: rgba(136, 136, 136, 0); /* 滚动条滑块的背景颜色，设置为半透明 */
      border-radius: 4px; /* 滚动条滑块的圆角 */
    }

    .learning-goals:hover::-webkit-scrollbar-thumb {
      background: rgba(136, 136, 136, 0.6); /* 鼠标悬停时滚动条滑块的颜色 */
    }

.goal-header {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eaeef2;

}

.goal-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.goals-list {
  list-style: none;
  padding: 0;
  margin: 0;

}

.goal-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  background-color: #dbe6f6;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.check-icon {
  width: 18px;
  height: 18px;
  margin-right: 15px;
  font-size: 16px;
  color: #4a6cf7;
}

.goal-text {
  flex: 1;
  font-size: 15px;
  color: #333;
  line-height: 1.5;
}

/* 添加不同颜色的图标来区分每个目标 */
.goal-item:nth-child(1) .check-icon {
  color: #4a6cf7;
}

.goal-item:nth-child(2) .check-icon {
  color: #34c38f;
}

.goal-item:nth-child(3) .check-icon {
  color: #fb9678;
}

.goal-item:nth-child(4) .check-icon {
  color: #706fd3;
}

.goal-item:nth-child(5) .check-icon {
  color: #54a0ff;
}
</style>