<template>
  <section class="editor">
    <!-- 两列三行布局 -->
    <div class="two-column-layout">
      <!-- 第一列 -->
      <div class="column">
        <!-- 学科 -->
        <div class="input_box">
          <label>学科 <span style="color: red;">(必填)</span></label>
          <input v-model="subject" placeholder="请输入..." />
        </div>
        <!-- 教材名称 -->
        <div class="input_box">
          <label>教材名称 <span style="color: red;">(必填)</span></label>
          <input v-model="textbook" placeholder="请输入..." />
        </div>
        <div class="select_box">
            <label>题型 <span style="color: red;">(必填)</span></label>
            <el-select v-model="questionType" placeholder="请选择" class="select">
              <el-option v-for="item in questionTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
        </div>
      </div>
      <!-- 第二列 -->
      <div class="column">
        <div class="input_box">
          <label>年级 <span style="color: red;">(必填)</span></label>
          <input v-model="grade" placeholder="请输入..." />
        </div>
        <!-- 主题 -->
        <div class="input_box">
          <label>主题 <span style="color: red;">(必填)</span></label>
          <input v-model="topic" placeholder="请输入..." />
        </div>
        <!-- 难度 -->
        <div class="select_box">
          <label>难度 <span style="color: red;">(必填)</span></label>
          <el-select v-model="difficulty" placeholder="请选择" class="select">
            <el-option v-for="item in difficultyOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 其他字段 -->
    <div class="single-column-layout">
      <!-- 题量 -->
      <div class="input_box">
        <label>题量 <span style="color: red;">(必填)</span></label>
        <input v-model="questionCount" type="number" placeholder="请输入..." />
      </div>

      <!-- 知识点 -->
      <div class="input_box">
        <label>知识点 <span style="color: red;">(必填)</span></label>
        <textarea v-model="knowledgePoints" placeholder="请输入..." />
      </div>

      <!-- 其他要求 -->
      <div class="input_box">
        <label>其他要求</label>
        <textarea v-model="otherRequirements" placeholder="请输入..." />
      </div>
    </div>

    <!-- 生成按钮 -->
    <el-button type="primary" @click="generateContent" class="button">
      生成
    </el-button>
  </section>
</template>

<script lang="ts" setup>
import { ref, defineEmits } from 'vue'
import axios from 'axios'

const emit = defineEmits(['update-preview'])

// 数据绑定变量
const grade = ref('')
const subject = ref('')
const textbook = ref('')
const topic = ref('')
const questionType = ref('不限')
const difficulty = ref('不限')
const questionCount = ref(0)
const knowledgePoints = ref('')
const otherRequirements = ref('')

// 下拉选项
const questionTypeOptions = [
  { value: '不限', label: '不限' },
  { value: '选择题', label: '选择题' },
  { value: '填空题', label: '填空题' },
  { value: '解答题', label: '解答题' },
]

const difficultyOptions = [
  { value: '不限', label: '不限' },
  { value: '简单', label: '简单' },
  { value: '中等', label: '中等' },
  { value: '困难', label: '困难' },
]

// 生成内容方法
const generateContent = async () => {
  try {
    const response = await axios.post('/api/plan/gen_question', {
      subject: subject.value,
      grade: grade.value,
      textbook: textbook.value,
      topic: topic.value,
      questionType: questionType.value,
      difficulty: difficulty.value,
      questionCount: questionCount.value,
      knowledgePoints: knowledgePoints.value,
      otherRequirements: otherRequirements.value,
    });
    console.log('Generated Content:', response.data);
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

/* 两列布局容器 */
.two-column-layout {
  display: flex;
  justify-content: space-between;
  gap: 20px; /* 两列之间的间距 */
  margin-bottom: 20px;
}

/* 单列布局容器 */
.single-column-layout {
  display: flex;
  flex-direction: column;
  gap: 20px; /* 单列中各字段之间的间距 */
}

/* 列样式 */
.column {
  flex: 1; /* 每列占据相同的宽度 */
  display: flex;
  flex-direction: column;
  gap: 20px; /* 列内字段之间的间距 */
}

/* 输入框样式 */
.input_box {
  display: flex;
  flex-direction: column;
}

.input_box label {
  margin-bottom: 5px;
  font-size: 16px;
  color: #2c3e50;
  font-weight: 500;
}

.input_box input,
.input_box textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
  color: #333;
}

.input_box input:focus,
.input_box textarea:focus {
  border-color: #3498db;
  box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
  outline: none;
  background-color: #fff;
}

/* 文本区域样式 */
textarea {
  height: 100px;
  resize: vertical;
}

/* 选择框容器样式 */
.select_box {
  display: flex;
  flex-direction: column;
}

.select_box label {
  margin-bottom: 5px;
  font-size: 16px;
  color: #2c3e50;
  font-weight: 500;
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
  align-self: flex-end;
  width: 100%;
  max-width: 100px;
  height: 40px;
  font-size: 16px;
  border-radius: 3px;
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
    height: auto;
    padding: 15px;
  }

  .two-column-layout {
    flex-direction: column; /* 小屏幕下改为单列布局 */
    gap: 15px;
  }

  .single-column-layout {
    gap: 15px;
  }

  .input_box input,
  .input_box textarea {
    font-size: 14px;
    padding: 10px;
  }

  :deep(.select) {
    width: 100%;
  }

  .button {
    width: 50%;
  }
}
</style>