<template>
    <div class="step-content">
      <h3>为您的计划增加时间</h3>
      <div class="time-settings">
        <div class="deadline">
          <p>1. 您的计划有截止日期吗？</p>
          <small>您也可以稍后添加截止日期</small>
          <el-date-picker 
            v-model="localData.deadline"
            type="date"
            placeholder="选择日期"
          ></el-date-picker>
        </div>
        <div class="weekly-hours">
          <p>* 2. 您每周可以在此计划上花费多少小时？</p>
          <el-slider 
            v-model="localData.time"
            :min="5"
            :max="40"
            show-stops
            :marks="{20: '20 小时'}"
          ></el-slider>
          <span class="current-value">{{ localData.time }} 小时</span>
        </div>
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
  .time-settings {
    margin-top: 10px;
  }
  
  .deadline,
  .weekly-hours {
    margin-bottom: 20px;
  }
  
  .current-value {
    display: block;
    text-align: center;
    margin-top: 10px;
  }
  </style>