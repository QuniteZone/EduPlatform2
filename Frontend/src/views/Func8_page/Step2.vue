<template>
    <div class="step-content">
      <h3>您从哪里开始？</h3>
      <p class="description">描述您在与学习目标相关的领域的现有知识或技能水平。</p>
      <el-input 
        type="textarea" 
        v-model="localData.background"
        :rows="5"
        placeholder="例如，我没有编程经验，但学习了概率与统计课程..."
      ></el-input>
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
    }
  }
  </script>