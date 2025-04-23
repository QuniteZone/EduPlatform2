<template>
  <section class="editor">
    <textarea v-model="content" placeholder="请输入内容..."></textarea>
    <div class="select_box">
      <div class="grade_select">
        <p>选择年级</p>
        <el-select v-model="grade" placeholder="Select" class="select">
          <el-option v-for="item in gradeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </div>
      <div class="course_select">
        <p>选择课程</p>
        <el-select v-model="subject" placeholder="Select" class="select">
          <el-option v-for="item in subjectOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </div>
      <el-button type="primary" @click="generateContent" class="button">
        生成内容
      </el-button>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { ref, defineEmits } from 'vue'
import axios from 'axios'

const emit = defineEmits(['update-preview'])

const grade = ref('未选择')
const subject = ref('未选择')
const content = ref('')
const gradeOptions = [
  { value: '高一', label: '高一' },
  { value: '高二', label: '高二' },
  { value: '高三', label: '高三' },
]

const subjectOptions = [
  { value: '数学', label: '数学' },
  { value: '语文', label: '语文' },
  { value: '英语', label: '英语' },
]

const generateContent = async () => {
  try {
    const response = await axios.post('/api/plan/lesson_plan', {
      grade: grade.value,
      subject: subject.value,
      knowledge: content.value
      });
    console.log('Editor_content:', response.data);
    emit('update-preview', response.data)
  } catch (error) {
    alert('生成失败');
    console.error('请求失败:', error);
  }
};
</script>

<style scoped>
/* 编辑器容器样式 */
.editor {
  width: 100%;                    /* 容器宽度自适应 */
  max-width: 800px;               /* 最大宽度 */
  margin: 0 auto;                 /* 水平居中 */
  border: 2px solid #3498db;      /* 边框样式 */
  border-radius: 10px;            /* 圆角大小 */
  padding: 20px;                  /* 内边距 */
  display: flex;
  flex-direction: column;
  background-color: #fff;         /* 背景色 */
  box-sizing: border-box;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
  transition: all 0.3s ease;      /* 添加过渡效果 */
}

.editor:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15); /* 悬停时阴影加深 */
  border-color: #2980b9;          /* 悬停时边框颜色变化 */
}

/* 文本区域样式 */
textarea {
  width: 100%;                    /* 占满容器宽度 */
  height: 30vh;                   /* 文本区域高度 */
  resize: none;                   /* 是否允许调整大小 */
  margin-bottom: 20px;            /* 底部外边距 */
  padding: 15px;                  /* 内边距 */
  border: 1px solid #ddd;         /* 边框样式 */
  border-radius: 6px;             /* 圆角大小 */
  font-size: 16px;                /* 字体大小 */
  box-sizing: border-box;         /* 确保padding不会增加元素总宽度 */
  transition: all 0.3s ease;      /* 添加过渡效果 */
  background-color: #f8f9fa;      /* 背景色 */
  color: #333;                    /* 文字颜色 */
}

textarea:focus {
  border-color: #3498db;          /* 获得焦点时边框颜色变化 */
  box-shadow: 0 0 5px rgba(52, 152, 219, 0.3); /* 获得焦点时添加阴影 */
  outline: none;                  /* 移除默认焦点轮廓 */
  background-color: #fff;         /* 获得焦点时背景色变化 */
}

/* 选择框容器样式 */
.select_box {
  display: flex;
  gap: 5%;                        /* 默认间距 */
  margin-top: 0px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;                /* 允许换行 */
}

/* 选择框标签样式 */
.grade_select p,
.course_select p {
  margin-bottom: 8px;             /* 标签与下拉框的间距 */
  font-size: 16px;                /* 标签字体大小 */
  color: #2c3e50;                 /* 标签文字颜色 */
  font-weight: 500;               /* 字体粗细 */
}

/* Element Plus 选择器样式覆盖 */
:deep(.select) {
  width: 100%;                    /* 宽度自适应 */
  max-width: 180px;               /* 最大宽度 */
}

:deep(.select .el-input__wrapper) {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: none;
  transition: all 0.3s ease;
}

:deep(.select .el-input__wrapper:hover) {
  border-color: #3498db;
}

:deep(.select .el-input__wrapper.is-focus) {
  border-color: #3498db;
  box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
}

/* 按钮样式 */
.button {
  margin-left: 0;                 /* 移除默认左侧外边距 */
  align-self: flex-end;
  width: 100%;                    /* 宽度自适应 */
  max-width: 180px;               /* 最大宽度 */
  height: 40px;
  font-size: 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor {
    width: 80vw;                /* 移动端使用视口宽度 */
    height: 60vh;               /* 移动端容器高度 */
    padding: 15px;              /* 移动端内边距 */
  }

  textarea {
    height: 35vh;               /* 移动端文本区域高度 */
    font-size: 14px;            /* 移动端字体大小 */
    padding: 10px;              /* 移动端内边距 */
  }

  .select_box {
    flex-direction: column;      /* 移动端垂直排列 */
    gap: 15px;                  /* 移动端间距 */
  }

  :deep(.select) {
    width: 100%;                /* 移动端选择框宽度 */
  }

  .button {
    width: 50%;                /* 移动端按钮宽度 */
    margin-left: 0;             /* 移动端左侧外边距 */
  }
}

@media (min-width: 769px) and (max-width: 1200px) {
  .select_box {
    gap: 2%;                    /* 中等屏幕间距 */
  }
}
</style>