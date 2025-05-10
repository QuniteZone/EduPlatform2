<template>
  <div class="func11-test-container">
    <!-- 创建学习计划的组件 -->
    <func8 @create-plan="handleCreatePlan" />

    <!-- 学习路径展示组件 -->
    <learning-path :learning-data="currentLearningData" v-if="currentLearningData" />
  </div>
</template>

<script>
import func8 from '@/views/Func8_study_plan/all_steps.vue'
import LearningPath from '@/views/Func8_study_plan/LearningPath.vue'

export default {
  name: 'Func11Test',
  components: {
    func8,
    LearningPath
  },
  data() {
    return {
      currentLearningData: null // 接收从 func8 传来的学习计划数据
    }
  },
  methods: {
    /**
     * 处理从 func8 组件 $emit 过来的学习计划数据
     * @param {Object} planData - 来自后端返回的学习计划 JSON 数据
     */
    handleCreatePlan(planData) {
      console.log('收到学习计划数据:', planData)
      this.currentLearningData = planData
    }
  }
}
</script>

<style scoped>
.func11-test-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
</style>