<template>
  <section class="editor">
    <!-- 文件上传部分 -->
    <div class="file_upload">
      <p>上传教案文件（可选）</p>
      <input type="file" @change="handleFileUpload" multiple accept=".pdf,.doc,.docx" />
    </div>

    <!-- 逐字稿要求部分 -->
    <div class="transcription_requirements">
      <p>逐字稿要求</p>
      <textarea v-model="require" placeholder="请输入逐字稿要求..."></textarea>
    </div>

    <!-- 提交按钮 -->
    <el-button type="primary" @click="generateContent" class="button">
      生成内容
    </el-button>
  </section>
</template>

<script lang="ts" setup>
import { ref, defineEmits } from 'vue'
import axios from 'axios'

const emit = defineEmits(['update-preview'])

const fileData = ref<File[]>([])
const require = ref('')

const handleFileUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input?.files) {
    const filesArray = Array.from(input.files)
    const validExtensions = ['.pdf', '.doc', '.docx']
    const validTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]

    const allValid = filesArray.every(file => {
      const extValid = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext))
      const typeValid = validTypes.includes(file.type)
      return extValid || typeValid
    })

    if (!allValid) {
      alert('只能上传 PDF、DOC 或 DOCX 文件！')
      input.value = ''
      fileData.value = []
    } else {
      fileData.value = filesArray
    }
  }
}

const generateContent = async () => {
  if (fileData.value.length === 0) {
    alert('请至少上传一个文件！')
    return
  }
  if (!require.value) {
    alert('请填写逐字稿要求！')
    return
  }

  const formData = new FormData()
  fileData.value.forEach(file => formData.append('files', file))
  formData.append('require', require.value)

  try {
    const response = await axios.post('api/plan/lesson_script', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    emit('update-preview', response.data)
  } catch (error) {
    alert('生成失败')
    console.error('请求失败:', error)
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

/* 文件上传部分样式 */
.file_upload p {
  margin-bottom: 10px;
  font-size: 16px;
  color: #2c3e50;
}

input[type="file"] {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

/* 逐字稿要求部分样式 */
.transcription_requirements p {
  margin-bottom: 8px;
  font-size: 16px;
  color: #2c3e50;
}

textarea {
  width: 100%;
  height: 20vh;
  resize: none;
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  box-sizing: border-box;
  background-color: #f8f9fa;
  color: #333;
}

textarea:focus {
  border-color: #3498db;
  box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
  outline: none;
  background-color: #fff;
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
</style>
