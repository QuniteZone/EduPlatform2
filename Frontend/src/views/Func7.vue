<template>
  <div class="main_container">
    <!-- 顶部区域 -->
    <div class="about">
      <h2>作业辅导</h2>
      <h4>助学场景：AI作业辅导</h4>
    </div>
    <!-- 主体内容 -->
    <div class="content-container">
      <!-- 消息区域 -->
      <div class="message-area">
        <div id="chat" :class="form.msgList.length === 0 ? 'nodata' : ''">
          <!-- 欢迎提示 -->
          <div v-if="form.msgList.length === 0" class="welcome-message">
            <span>欢迎提问！</span>
          </div>
          <!-- 消息列表 -->
          <div v-for="(item, index) in form.msgList" :key="index" class="message-group">
            <!-- 用户提问 -->
            <div class="user-message">
              <div class="avatar-container-user">
                <img src="@/image/user-icon.png" alt="用户图标" class="chat-icon"/>
              </div>
              <div>
                <!-- 用户上传的图片（如果存在） -->
                <img
                    v-if="item.image"
                    :src="item.image"
                    class="chat-image"
                    alt="用户上传图片"
                    @click="showImagePreview(item.image)"
                />

                <!-- 用户消息内容 -->
                <div class="bubble user-bubble">{{ item.question }}</div>
              </div>
            </div>

            <!-- 思考内容（用特殊样式展示） -->
            <div v-if="item.thinking" class="thinking-content">
              <div class="label">🧠 思考过程：</div>
              <div class="content">{{ item.thinking }}</div>
            </div>
            <!-- AI 回复 -->
            <div v-if="item.answer" class="bot-message">
              <div class="avatar-container-bot">
                <img src="@/image/bot-icon.png" alt="机器人图标" class="chat-icon"/>
              </div>
              <div class="bubble bot-bubble" v-html="parseMarkdown(item.answer)"></div>
            </div>
          </div>
        </div>
      </div>
      <!-- 输入框区域 -->
      <div class="input-wrapper">
        <el-input
            class="input-box"
            @keyup.enter="sendMsg"
            v-model="form.input"
            placeholder="请输入问题..."
        ></el-input>
        <el-button class="send-button" @click="sendMsg">发送</el-button>
        <el-tooltip content="上传作业文件（仅识别文字）,支持word，PDF和各类图片" placement="top">
          <el-upload
              action=""
              :http-request="customUpload"
              :show-file-list="false"
              accept=".jpg,.jpeg,.png,.doc,.docx,.pdf"
              multiple
          >
            <img src="@/image/upload-icon.png" alt="上传图标" class="upload-icon"/>
          </el-upload>
        </el-tooltip>
      </div>
      <!-- 已上传文件列表 -->
      <div class="uploaded-files">
        <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
          <span class="file-name">{{ file.name }}</span>
          <img
              v-if="file.previewUrl"
              :src="file.previewUrl"
              alt="文件预览"
              class="file-preview"
          />
          <button class="delete-button" @click="removeFile(index)">删除</button>
        </div>
      </div>
      <!-- 提示信息 -->
      <p class="disclaimer">
        服务生成的所有内容均由人工智能模型生成，其生成内容的准确性和完整性无法保证，不代表我们的态度或观点。
      </p>
      <el-dialog v-model="dialogVisible" width="60%" center>
        <img :src="dialogImage" alt="预览图" class="dialog-preview-image"/>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import {reactive, nextTick, ref} from 'vue';
import axios from "axios";
import MarkdownIt from 'markdown-it';
//图片预览
const dialogVisible = ref(false);
const dialogImage = ref("");

function showImagePreview(imgUrl) {
  dialogImage.value = imgUrl;
  dialogVisible.value = true;
}

const md = new MarkdownIt({html: true, linkify: true, typographer: true});

function parseMarkdown(content) {
  try {
    return md.render(content);
  } catch (error) {
    console.error("Markdown 解析失败:", error);
    return content;
  }
}

function setScrollToBottom() {
  nextTick(() => {
    const chat = document.querySelector('#chat');
    if (chat) chat.scrollTop = chat.scrollHeight;
  });
}

const uploadedFiles = ref([]);

async function customUpload(fileData) {
  const file = fileData.file;
  let previewUrl = null;

  if (!["image/jpeg", "image/png", "image/jpg"].includes(file.type)) {
    alert("仅支持 JPG/PNG 图像上传");
    return;
  }

  const reader = new FileReader();
  previewUrl = await new Promise((resolve) => {
    reader.onload = () => resolve(reader.result);
    reader.readAsDataURL(file);
  });

  // 仅保留一张图片
  uploadedFiles.value = [{
    name: file.name,
    previewUrl,
    raw: file
  }];
}

function removeFile(index) {
  uploadedFiles.value.splice(index, 1);
  form.fileIPs.splice(index, 1);
}

const form = reactive({
  input: '',
  msgList: [],
  fileIPs: []
});

let LLMs_messages = [];
import { v4 as uuidv4 } from 'uuid'; // 顶部引入

const session_id = uuidv4(); // 页面加载生成一次会话 ID
async function sendMsg() {
  if (form.input.length > 0) {
    const user_question = form.input;
    const msg = {
      question: user_question,
      thinking: "AI正在思考中……",
      answer: "",
      image: uploadedFiles.value[0]?.previewUrl || null
    };

    form.msgList.push(msg);
    form.input = "";
    setScrollToBottom();

    const formData = new FormData();
    formData.append("message", user_question);
    formData.append("session_id", session_id); // ✅ 关键新增


    // 如果有上传的图片，添加到表单中（目前支持一张）
    if (uploadedFiles.value.length > 0 && uploadedFiles.value[0].raw) {
      formData.append("file", uploadedFiles.value[0].raw);
    }

    try {
      const response = await fetch("/api/ques/chat", {
        method: "POST",
        body: formData
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      const lastMsgIndex = form.msgList.length - 1;

      let fullResponse = '';
      let isInThinkTag = false;
      let thinkingContent = '';
      let answerContent = '';

      // eslint-disable-next-line no-constant-condition
      while (true) {
        const {done, value} = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, {stream: true});
        fullResponse += chunk;

        while (fullResponse.includes('<think>') || fullResponse.includes('</think>')) {
          if (!isInThinkTag) {
            const startIdx = fullResponse.indexOf('<think>');
            if (startIdx !== -1) {
              isInThinkTag = true;
              fullResponse = fullResponse.slice(startIdx + 7);
            } else {
              break;
            }
          } else {
            const endIdx = fullResponse.indexOf('</think>');
            if (endIdx !== -1) {
              thinkingContent += fullResponse.slice(0, endIdx);
              fullResponse = fullResponse.slice(endIdx + 8);
              await displayThinkingContent(lastMsgIndex, thinkingContent);
              isInThinkTag = false;
              thinkingContent = '';
            } else {
              thinkingContent += fullResponse;
              fullResponse = '';
            }
          }
        }

        if (!isInThinkTag && fullResponse.length > 0) {
          answerContent += fullResponse;
          await typeWriterEffect(lastMsgIndex, answerContent.trim());
          fullResponse = '';
        }

        setScrollToBottom();
      }

      // 清空上传列表，避免重复提交
      uploadedFiles.value = [];
    } catch (error) {
      console.error("Error:", error);
      form.msgList[form.msgList.length - 1].answer = "生成失败，请稍后重试";
    }
  }
}

function displayThinkingContent(index, text) {
  return new Promise((resolve) => {
    let i = 0;
    form.msgList[index].thinking = '';
    const interval = setInterval(() => {
      if (i < text.length) {
        form.msgList[index].thinking += text[i];
        i++;
      } else {
        clearInterval(interval);
        resolve();
      }
      setScrollToBottom();
    }, 50);
  });
}

function typeWriterEffect(index, text) {
  return new Promise((resolve) => {
    let i = 0;
    form.msgList[index].answer = '';
    const interval = setInterval(() => {
      if (i < text.length) {
        form.msgList[index].answer += text[i];
        i++;
      } else {
        clearInterval(interval);
        resolve();
      }
      setScrollToBottom();
    }, 50);
  });
}
</script>


<style scoped>
.chat-image {
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
  margin-bottom: 8px;
  display: block;
  cursor: pointer;
  transition: transform 0.2s;
}

.chat-image:hover {
  transform: scale(1.02);
}

.dialog-preview-image {
  width: 100%;
  height: auto;
  border-radius: 10px;
}

/* 整体容器 */
.main_container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100vh; /* 全屏高度 */
  margin: 0 auto;
  padding: 20px;
}

/* 标题区域样式 */
.about {
  display: flex; /* 使用flex布局 */
  flex-direction: column; /* 垂直方向排列 */
  align-items: center; /* 水平居中 */
  justify-content: center; /* 垂直居中 */
  text-align: center; /* 文本居中对齐 */
  margin: 2rem auto; /* 上下外边距2rem，左右自动居中 */
  background: linear-gradient(135deg, #f18e8e 0%, #e9ecef 100%); /* 浅灰色渐变背景 */
  border-radius: 1rem; /* 圆角边框 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); /* 阴影效果 */
  border: 1px solid rgba(255, 255, 255, 0.3); /* 半透明白色边框 */
  width: 80vw;
  height: 250px; /* 固定高度 */
}

/* 主标题样式 */
.about h2 {
  color: #458fd8; /* 文字颜色 */
  font-size: 2.5rem; /* 字体大小 */
  font-weight: 700; /* 字体粗细 */
  margin-top: 0; /* 移除顶部外边距 */
  margin-bottom: 0.5rem; /* 减小底部外边距 */
  letter-spacing: -0.5px; /* 字间距 */
  position: relative; /* 相对定位 */
  padding-top: -10rem; /* 添加顶部内边距 */
}

/* 副标题样式 */
.about h4 {
  color: #518fc5; /* 文字颜色 */
  font-size: 1.3rem; /* 字体大小 */
  font-weight: 400; /* 字体粗细 */
  margin: 0; /* 移除外边距 */
  padding: 0.8rem 1.5rem; /* 内边距 */
  background: rgba(255, 255, 255, 0.9); /* 半透明白色背景 */
  border-radius: 1rem; /* 圆角边框 */
  display: inline-block; /* 行内块级元素 */
  border: 1px solid rgba(0, 0, 0, 0.05); /* 细边框 */
}

/* 主体内容 */
.content-container {
  display: flex;
  flex-direction: column; /* 垂直布局 */
  justify-content: space-between; /* 确保输入框在底部 */
  align-items: stretch;
  width: 100%;
  max-width: 1200px;
  margin-top: 20px;
  height: calc(100vh - 160px); /* 减去顶部区域和底部间距 */
}

/* 消息区域 */
.message-area {
  flex: 1; /* 占据剩余空间 */
  overflow-y: auto;
  //border: 1px solid #ccc; /* 边框区分 */
  border-radius: 8px;
  padding: 20px;
  background-color: #f9f9f9; /* 背景颜色 */
}

#chat {
  height: 100%;
  overflow-y: auto;
}

.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 18px;
  color: #888;
}

.message-group {
  margin-bottom: 20px;
}

.user-message, .bot-message {
  display: flex;
  align-items: start;
  gap: 10px;
  margin-bottom: 8px;
}

.user-message {
  justify-content: flex-end;
}

.user-message {
  display: flex;
  align-items: center;
  justify-content: flex-end; /* 消息靠右对齐 */
  gap: 10px;
  margin-bottom: 8px;
}

/* 用户头像容器 */
.avatar-container-user {
  order: 2; /* 将头像放在右侧 */
}

/* 用户消息气泡 */
.user-bubble {
  background-color: rgba(122, 138, 117, 0.25); /* 用户消息气泡背景色 */
  border-radius: 16px 16px 16px 4px; /* 右侧圆角 */
  padding: 12px 16px;
  max-width: 70%;
  word-break: break-word;
  white-space: pre-wrap;
  align-self: flex-end; /* 气泡靠右对齐 */
}

/* AI 回复消息 */
.bot-message {
  display: flex;
  align-items: start;
  justify-content: flex-start; /* AI 消息靠左对齐 */
}

/* AI 头像容器 */
.avatar-container-bot {
  align-items: flex-start;
}

/* AI 消息气泡 */
.bot-bubble {
  background-color: rgb(255, 255, 255);
  border-radius: 16px 16px 4px 16px; /* 左侧圆角 */
  padding: 3px 4px;
  max-width: 100%;
  word-break: break-word;
  white-space: pre-wrap;
  align-self: flex-start; /* 气泡靠左对齐 */
}


.thinking-content {
  margin-top: 10px;
  margin-left: 40px;
  padding: 10px 15px;
  background-color: rgba(122, 138, 117, 0.08);
  border-left: 4px solid #757e8a;
  color: rgb(4, 4, 4);
  border-radius: 6px;
}

.label {
  font-weight: bold;
  margin-bottom: 6px;
}

/* 输入框区域 */
.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 40px;
  margin-bottom: 20px;
}

.input-box {
  flex: 1;
}

.send-button {
  padding: 10px 20px;
  background-color: #0079bf;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.upload-icon {
  width: 24px;
  height: 24px;
}

/* 已上传文件列表 */
.uploaded-files {
  margin: 10px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  background-color: #f7f9fc;
  min-height: 40px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 5px;
  background-color: #e9ecef;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  color: #333;
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.file-preview {
  width: 24px;
  height: 24px;
  object-fit: cover;
  border-radius: 4px;
}

.delete-button {
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 2px 6px;
  cursor: pointer;
  font-size: 10px;
}

.delete-button:hover {
  background-color: #ff7875;
}

/* 提示信息 */
.disclaimer {
  font-size: 12px;
  color: #666;
  text-align: center;
}
</style>
