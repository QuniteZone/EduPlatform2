<template>
  <section class="editor">
    <textarea v-model="content" placeholder="请输入内容..."></textarea>
    <div class="select_box">
      <div class="course grade_select">
        <p class="label-text">输入年级</p>
        <input v-model="grade" placeholder="请输入..." />
      </div>
      <div class="course course_select">
        <p class="label-text">输入学科</p>
        <input v-model="subject" placeholder="请输入..." />
      </div>
      <!-- 按钮添加 loading 状态 -->
      <el-button
        type="primary"
        @click="generateContent"
        class="button"
        :loading="loading"
        :icon="loading ? 'Loading' : ''"
      >
        {{ loading ? '生成中...' : '生成内容' }}
      </el-button>
    </div>
  </section>
</template>

<script setup>
import { ref, defineEmits } from 'vue'
import axios from 'axios'

const emit = defineEmits(['update-preview'])

const content = ref('')
const grade = ref('')
const subject = ref('')
const loading = ref(false) // 控制加载状态

const generateContent = async () => {
  loading.value = true // 开始加载
  try {
    const response = await axios.post('/api/plan/lesson_plan', {
      grade: grade.value,
      subject: subject.value,
      knowledge: content.value
    })
    console.log('Editor_content:', response)
    emit('update-preview', response.data)
  } catch (error) {
    alert('生成失败')
    console.error('请求失败:', error)
  } finally {
    loading.value = false // 结束加载
  }
}
</script>

<style scoped>
/* 编辑器容器样式 */
.editor {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  border: 2px solid #3498db;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  box-sizing: border-box;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.editor:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  border-color: #2980b9;
}

/* 文本区域样式 */
textarea {
  width: 100%;
  height: 30vh;
  resize: none;
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
  color: #333;
}

textarea:focus {
  border-color: #3498db;
  box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
  outline: none;
  background-color: #fff;
}

/* 选择框容器样式 */
.select_box {
  display: flex;
  flex-wrap: nowrap;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-top: 0px;
  padding: 15px;
  background-color: #ffffff;
  border-radius: 8px;
}

.course {
  display: flex;
  flex-direction: column;
}

/* 选择框标签样式 */
.course p {
  margin-bottom: 5px;
  font-size: 16px;
  color: #2c3e50;
  font-weight: 500;
}

.course input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
  color: #333;
  flex-grow: 0;
  flex-shrink: 1;
}

/* Element Plus 选择器样式覆盖 */
:deep(.select) {
  width: 100%;
  max-width: 180px;
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
  margin-left: 0;
  align-self: flex-end;
  width: 100%;
  max-width: 180px;
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
    width: 80vw;
    height: 60vh;
    padding: 15px;
  }

  textarea {
    height: 35vh;
    font-size: 14px;
    padding: 10px;
  }

  .select_box {
    flex-direction: column;
    gap: 15px;
  }

  :deep(.select) {
    width: 100%;
  }

  .button {
    width: 50%;
    margin-left: 0;
  }
}

@media (min-width: 769px) and (max-width: 1200px) {
  .select_box {
    gap: 2%;
  }
}
</style>