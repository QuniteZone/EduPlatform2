<template>
    <div class="step-content">
      <h3>您的学习目标是什么？</h3>
      <p class="description">确定您希望学习的特定知识或技能，以及您希望如何应用它们。</p>
      <el-input 
        type="textarea" 
        v-model="localData.goal"
        :rows="5"
        placeholder="例如，能够使用 Python 编码并使用 OpenAI API..."
      ></el-input>
      <el-link type="primary" @click="optimizeGoal">使用 AI 优化您的目标</el-link>
    </div>
  </template>
  
  <script>
  export default {
    props: ['data'],
    data() {
      return {
        localData: { ...this.data }
      }
    },
    watch: {
      localData: {
        handler(val) {
          this.$emit('update-data', val)
        },
        deep: true
      }
    },
    methods: {
      optimizeGoal() {
        // 调用AI优化逻辑
        this.localData.goal = '优化后的目标描述'
      }
    }
  }
  </script>
  
  <style scoped>
  .description {
    color: #909399;
    margin-bottom: 10px;
  }
  
  .el-link {
    display: block;
    margin-top: 10px;
  }
  </style>