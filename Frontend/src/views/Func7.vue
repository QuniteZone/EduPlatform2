<template>
  <div class="main_container">
    <!-- 顶部区域 -->
    <div class="header">
      <h2>作业辅导</h2>
      <p>助学场景：AI作业辅导</p>
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
              <div class="bubble user-bubble">{{ item.question }}</div>
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
    </div>
  </div>
</template>

<script setup>
import {reactive, nextTick, ref} from 'vue';
import axios from "axios";
import MarkdownIt from 'markdown-it';

const md = new MarkdownIt({ html: true, linkify: true, typographer: true });
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
  const formData = new FormData();
  formData.append("file", fileData.file);
  try {
    const response = await axios.post("/api/ques/upload", formData, {
      headers: {"Content-Type": "multipart/form-data"}
    });
    if (response.data && response.data.fileIP) {
      const fileIP = response.data.fileIP;
      const fileName = fileData.file.name;
      let previewUrl = null;
      if (["image/jpeg", "image/png", "image/jpg"].includes(fileData.file.type)) {
        const reader = new FileReader();
        previewUrl = await new Promise((resolve) => {
          reader.onload = () => resolve(reader.result);
          reader.readAsDataURL(fileData.file);
        });
      }
      uploadedFiles.value.push({ name: fileName, previewUrl });
      form.fileIPs.push(fileIP);
    } else {
      throw new Error("后端返回数据不完整");
    }
  } catch (error) {
    alert("文件上传失败");
    console.error("文件上传失败:", error);
  }
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

async function sendMsg() {
  if (form.input.length > 0) {
    const user_question = form.input;
    const msg = {
      question: user_question,
      thinking: "AI正在思考中……",
      answer: ""
    };
    form.msgList.push(msg);
    form.input = "";
    setScrollToBottom();

    const llm_cont = {
      role: 'user',
      content: user_question
    };
    LLMs_messages.push(llm_cont);

    try {
      const response = await fetch("/api/ques/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          message: LLMs_messages,
          image_urls: form.fileIPs || []
        })
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

      LLMs_messages.push({ role: 'assistant', content: form.msgList[lastMsgIndex].answer });
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

/* 顶部区域 */
.header {
  background-color: #e6fffa;
  border-radius: 8px;
  padding: 20px;
  display: flex; /* 使用 Flexbox */
  flex-direction: column; /* 垂直排列 */
  justify-content: center; /* 垂直居中 */
  align-items: center; /* 水平居中 */
  width: 100%;
}

.header h2 {
  color: #0079bf;
  font-size: 24px;
  margin: 0;
}

.header p {
  background-color: #fff;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  margin-top: 10px; /* 调整间距 */
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
