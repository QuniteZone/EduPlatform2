<template>
    <div class="step-content">
      <h3>设置</h3>
      <div class="title-input">
        <p>* 为您的学习计划命名</p>
        <el-input 
          v-model="localData.title"
          placeholder="输入您的计划标题..."
          clearable
        ></el-input>
      </div>
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
  
  <style scoped>
  .title-input {
    margin-top: 10px;
  }
  </style>