<template>
    <div class="step-content">
      <h3>选择您喜欢的学习资源类型</h3>
      <p class="description">随意选择多个。我们将相应地定制您的学习计划。</p>
      <el-checkbox-group v-model="localData.preferences">
        <el-checkbox-button 
          v-for="(option, index) in options" 
          :key="index" 
          :label="option.value"
          border
        >
          <div class="option-item">
            <i :class="option.icon"></i>
            <div class="text">
              <span>{{ option.label }}</span>
              <small>{{ option.desc }}</small>
            </div>
          </div>
        </el-checkbox-button>
      </el-checkbox-group>
    </div>
  </template>
  
  <script>
  export default {
    props: ['data'],
    data() {
      return {
        localData: { ...this.data },
        options: [
          { value: 'video', label: '视频', desc: '视觉学习', icon: 'el-icon-video-play' },
          { value: 'project', label: '项目', desc: '边做边学', icon: 'el-icon-s-grid' },
          { value: 'article', label: '文章/博客', desc: '在线 Gems', icon: 'el-icon-document' }
        ]
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
  .option-item {
    display: flex;
    align-items: center;
    padding: 15px;
  }
  
  .option-item i {
    font-size: 24px;
    margin-right: 10px;
  }
  
  .text small {
    display: block;
    font-size: 12px;
    color: #909399;
  }
  </style>