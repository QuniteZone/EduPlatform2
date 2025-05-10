<template>
  <el-dialog v-model="visible" title="计划详情" width="60%" custom-class="custom-plan-dialog" @close="handleClose">
    <div v-if="plan">
      <h3>{{ plan.title }}</h3>
      <p><strong>状态:</strong> {{ plan.status }}</p>
      <p><strong>创建时间:</strong> {{ plan.createdAt }}</p>
      <p><strong>目标:</strong> {{ plan.goal }}</p>
      <p><strong>背景:</strong> {{ plan.background }}</p>
      <p><strong>内容:</strong>
        <Markdown :source="plan.content" />
      </p>
      <p><strong>时间:</strong> {{ plan.time }} 小时</p>
      <p><strong>截止日期:</strong> {{ plan.deadline }}</p>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="visible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import Markdown from 'vue3-markdown-it';

export default {
  name: 'PlanDetails',
  components: {
    Markdown
  },
  props: {
    plan: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      visible: false
    };
  },
  watch: {
    plan: {
      handler(newVal) {
        if (newVal) {
          this.visible = true; // 每次 plan 变化时，重新打开弹窗
        } else {
          this.visible = false; // 如果 plan 被清空，则关闭弹窗
        }
      },
      immediate: true
    }
  },
  methods: {
    handleClose() {
      this.visible = false;
    }
  }
};
</script>

<style scoped>
.custom-plan-dialog {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
</style>