<template>
  <div class="mian_container">
    <!-- Element Plus 弹窗 -->
    <el-dialog v-model="showModal" title="创建 AI 计划" width="60%" :close-on-click-modal="false"
      custom-class="custom-wizard-dialog">
      <div class="wizard-container">
        <!-- 左侧步骤导航 -->
        <div class="steps-sidebar">
          <div v-for="(step, index) in steps" :key="index" :class="['step-item', { active: currentStep === index }]"
            @click="currentStep = index">
            <span class="step-number">{{ step.number }}</span>
            {{ step.title }}
          </div>
        </div>

        <!-- 右侧内容区域 -->
        <div class="content-area">
          <component :is="currentComponent" :data="formData" @update-data="handleDataUpdate"></component>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <template #footer>
        <div class="dialog-footer">
          <el-button v-if="currentStep > 0" type="primary" plain @click="currentStep--">{{ currentStep === steps.length
            - 1 ? '取消' : '上一步' }}</el-button>
          <el-button type="primary" :loading="submitting" @click="handleNextOrSubmit">{{ currentStep === steps.length -
            1 ? '生成' : '下一步' }}</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 学习计划卡片区域 -->
    <div class="plan-cards" v-if="plans.length > 0">
      <el-card v-for="(plan, index) in plans" :key="index" class="plan-card" @click="showPlanDetails(plan)">
        <template #header>
          <div class="card-header">
            <span>{{ plan.title }}</span>
            <el-tag type="info">{{ plan.status }}</el-tag>
          </div>
        </template>
        <div class="card-body">
          <!-- <img 
            src="Frontend\src\assets\logo.png" 
            alt="计划封面" 
            class="cover-image"
          > -->
          <div class="meta-info">
            <p><strong>学习目标:</strong> {{ plan.goal }}</p>
            <p><strong>创建时间:</strong> {{ plan.createdAt }}</p>
            <p><strong>截止日期:</strong> {{ plan.deadline }}</p>
          </div>
        </div>
      </el-card>
    </div>
    <!-- 添加 PlanDetails 组件 -->
    <PlanDetails :plan="selectedPlan" v-if="selectedPlan" />
  </div>
</template>

<script>
import Editor from "./Func1_page/PageEditor.vue";
import Preview2 from "./Func1_page/PagePreview2.vue";
import axios from 'axios';
import Step1 from './Func8_page/Step1.vue'
import Step2 from './Func8_page/Step2.vue'
import Step3 from './Func8_page/Step3.vue'
import Step4 from './Func8_page/Step4.vue'
import Step5 from './Func8_page/Step5.vue'
import PlanDetails from './Func8_page/PlanDetails.vue'

export default {
  name: 'FunctionOne',
  components: {
    Editor,
    Preview2,
    Step1,
    Step2,
    Step3,
    Step4,
    Step5,
    PlanDetails
  },
  data() {
    return {
      previewContent: "NULL",
      showModal: true, // 初始值为 false，可以根据需要改为 true
      currentStep: 0,
      submitting: false,
      formData: {
        goal: '',
        background: '',
        preferences: [],
        time: 20,
        deadline: null,
        title: ''
      },
      steps: [
        { number: 1, title: '目标', component: 'Step1' },
        { number: 2, title: '背景', component: 'Step2' },
        { number: 3, title: '偏好', component: 'Step3' },
        { number: 4, title: '时间', component: 'Step4' },
        { number: 5, title: '设置', component: 'Step5' }
      ],
      plans: [],
      selectedPlan: null
    };
  },
  computed: {
    currentComponent() {
      return this.steps[this.currentStep].component
    }
  },
  methods: {
    updatePreview(newData) {
      this.previewContent = newData;
    },
    handleDataUpdate(data) {
      Object.assign(this.formData, data)
    },
    async handleNextOrSubmit() {
      if (this.currentStep < this.steps.length - 1) {
        this.currentStep++
      } else {
        this.submitting = true
        try {
          const response = await axios.post('/api/plan/study_plan', this.formData)
          console.log('YTYPlan:', response.data)
          this.plans.push(response.data)
          this.showModal = false // 关闭弹窗
          this.$message.success('计划生成成功')
        } catch (error) {
          this.$message.error('生成失败，请重试')
        } finally {
          this.submitting = false
        }
      }
    },
    showPlanDetails(plan) {
      this.selectedPlan = null; // 先清空 selectedPlan
      this.$nextTick(() => {
        this.selectedPlan = plan; // 再赋值新的 plan
      });
      this.showModal = false; // 确保关闭弹窗
      console.log('PlanDetails:', plan);
    },
    async fetchPlans() { // 向服务器请求，加载历史学习计划数据
      try {
        const response = await axios.post('/api/plan/study_plan')
        this.plans = response.data
      } catch (error) {
        console.error('加载计划失败:', error)
      }
    }
  },
  mounted() {
    this.fetchPlans()
  }
};
</script>

<style scoped>
/* 全局样式 */
body {
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
  color: #303133;
  background: #f0f2f5;
  padding: 20px;
}

/* 弹窗样式 */
.custom-wizard-dialog {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.wizard-container {
  display: flex;
  height: 500px;
  background: #f9fafc;
  border-radius: 12px;
}

.steps-sidebar {
  width: 180px;
  padding: 20px;
  border-right: 1px solid #ebeef5;
  background: #fff;
  border-top-left-radius: 12px;
  border-bottom-left-radius: 12px;
}

.step-item {
  cursor: pointer;
  margin-bottom: 15px;
  color: #909399;
  font-size: 14px;
  transition: all 0.3s;
}

.step-item:hover,
.step-item.active {
  color: #409EFF;
  font-weight: bold;
  transform: translateX(5px);
}

.step-number {
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  border-radius: 50%;
  background: #ebeef5;
  margin-right: 8px;
  font-size: 12px;
  transition: all 0.3s;
}

.step-item.active .step-number {
  background: #409EFF;
  color: #fff;
}

.content-area {
  flex: 1;
  padding: 30px;
  background: #fff;
  border-top-right-radius: 12px;
  border-bottom-right-radius: 12px;
}

.dialog-footer {
  text-align: right;
  padding: 20px;
  border-top: 1px solid #ebeef5;
}

/* 卡片样式 */
.plan-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin: 20px 0;
}

.plan-card {
  width: calc(33% - 20px);
  cursor: pointer;
  transition: all 0.3s;
}

.plan-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cover-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 10px;
}

.meta-info {
  color: #909399;
  font-size: 14px;
}

@media (max-width: 768px) {
  .plan-card {
    width: 100%;
  }
}
</style>