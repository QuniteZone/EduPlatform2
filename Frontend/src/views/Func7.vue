<template>
  <div class="main_container">
    <div class="about">
      <h2>作业辅导</h2>
      <h4>助学场景：AI作业辅导</h4>
    </div>
    <div class="common-layout">
      <el-container>
        <el-container class="split-container">
          <el-aside width="70%" class="chat-container">
            <div id="chat" :class="form.msgList.length === 0 ? 'nodata' : ''">
              <div class="chat-message" v-for="(item, index) in form.msgList" :key="index">
                <div class="chat-item user">
                  <div class="avatar-container">
                    <img src="@/image/user-icon.png" alt="用户图标" class="chat-icon" />
                  </div>
                  <div class="chat-bubble user">
                    <div class="message-content">{{ item.question }}</div>
                  </div>
                </div>
                <div class="chat-item bot">
                  <div class="avatar-container">
                    <img src="@/image/bot-icon.png" alt="机器人图标" class="chat-icon" />
                  </div>
                  <div class="chat-bubble bot">
                    <div class="message-content" v-html="item.answer"></div>
                  </div>
                </div>
              </div>
            </div>
          </el-aside>
          <el-main class="input-container">
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
                  <img src="@/image/upload-icon.png" alt="上传图标" class="upload-icon" />
                </el-upload>
              </el-tooltip>
            </div>
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
            <p class="disclaimer">
              服务生成的所有内容均由人工智能模型生成，其生成内容的准确性和完整性无法保证，不代表我们的态度或观点。
            </p>
          </el-main>
        </el-container>
      </el-container>
    </div>
  </div>
</template>

<script setup>
import { reactive, nextTick, ref } from 'vue';
import axios from "axios";

const form = reactive({
  input: '',
  msgList: [],
  fileIPs: []
});
let LLMs_messages = [];

function typeWriter(text, element, speed = 30) {
  let i = 0;
  const currentAnswer = element.answer || "";
  if (currentAnswer === "AI生成中...") {
    element.answer = "";
  }
  return new Promise((resolve) => {
    function typing() {
      if (i < text.length) {
        if (text.charAt(i) === '\n') {
          element.answer += '<br>';
        } else if (text.charAt(i) === ' ') {
          element.answer += '&nbsp;';
        } else {
          element.answer += text.charAt(i);
        }
        i++;
        setScrollToBottom();
        setTimeout(typing, speed);
      } else {
        resolve();
      }
    }
    typing();
  });
}

async function sendMsg() {
  if (form.input.length > 0) {
    const user_question = form.input;
    const msg = {
      question: user_question,
      answer: "AI生成中..."
    };
    form.msgList.push(msg);
    form.input = "";
    setScrollToBottom();
    const llm_cont = {
      'role': 'user',
      'content': user_question,
    };
    let llm_return_content = "";
    LLMs_messages.push(llm_cont);
    try {
      const response = await fetch("/api/ques/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: LLMs_messages,
          image_urls: form.fileIPs || []
        })
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      const lastMsgIndex = form.msgList.length - 1;
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        await typeWriter(chunk, form.msgList[lastMsgIndex], 10);
        llm_return_content += chunk;
      }
      form.msgList[lastMsgIndex].answer = llm_return_content;
      LLMs_messages.push({
        'role': 'assistant',
        'content': llm_return_content,
      });
    } catch (error) {
      console.error("Error:", error);
      form.msgList[form.msgList.length - 1].answer = "生成失败，请稍后重试";
    }
  }
}

const uploadedFiles = ref([]);

async function customUpload(fileData) {
  const formData = new FormData();
  formData.append("file", fileData.file);
  try {
    const response = await axios.post("/api/ques/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" }
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
      uploadedFiles.value.push({
        name: fileName,
        previewUrl: previewUrl
      });
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

async function setScrollToBottom() {
  await nextTick();
  let chat = document.querySelector("#chat");
  chat.scrollTop = chat.scrollHeight;
}
</script>

<style scoped>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  background-color: #f7f9fc;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
#app {
  height: 100%;
}
.main_container {
  margin-right: 80px;
  margin-left: 80px;
  margin-top: 40px;
}
.about {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin: 2rem auto;
  background: linear-gradient(135deg, #a7e6e5 0%, #e9ecef 100%);
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
  max-width: 10000px;
  height: 200px;
}
.about h2 {
  color: #458fd8;
  font-size: 2.5rem;
  font-weight: 700;
  margin-top: 0;
  margin-bottom: 0.5rem;
  letter-spacing: -0.5px;
  position: relative;
}
.about h4 {
  color: #518fc5;
  font-size: 1.3rem;
  font-weight: 400;
  margin: 0;
  padding: 0.8rem 1.5rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  display: inline-block;
  border: 1px solid rgba(0, 0, 0, 0.05);
}
.common-layout {
  height: calc(100vh - 260px);
  display: flex;
  flex-direction: column;
}
.split-container {
  display: flex;
  height: 100%;
}
.chat-container {
  overflow-y: auto;
  padding: 20px;
  border-right: 1px solid #e0e0e0;
}
.input-container {
  display: flex;
  flex-direction: column;
  padding: 20px;
  background-color: #ffffff;
}
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
.chat-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.chat-item.user {
  align-items: flex-end;
}
.avatar-container {
  width: 100%;
  display: flex;
  justify-content: flex-start;
  margin-bottom: 4px;
}
.chat-item.user .avatar-container {
  justify-content: flex-end;
}
.chat-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}
#chat {
  flex: 1;
  scroll-behavior: smooth;
}
.chat-message {
  max-width: 800px;
  margin: 12px auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.chat-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  max-width: 100%;
  word-break: break-word;
  font-size: 16px;
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
}
.chat-bubble.user {
  background-color: #e0f7fa;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}
.chat-bubble.bot {
  background-color: #f1f1f1;
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}
.message-content {
  text-align: left;
  flex: 1;
}
.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.input-box {
  flex: 1;
  height: 45px;
  border-radius: 12px;
}
.send-button {
  height: 45px;
  border-radius: 12px;
}
.upload-icon {
  width: 24px;
  height: 24px;
  cursor: pointer;
  transition: 0.3s ease;
}
.upload-icon:hover {
  transform: scale(1.1);
}
.disclaimer {
  margin-top: 16px;
  font-size: 12px;
  color: #888;
  text-align: center;
}
.nodata {
  background-repeat: no-repeat;
  background-size: 35%;
  background-position: center 40%;
  position: relative;
}
.nodata::before {
  content: "开始你的提问吧~";
  position: absolute;
  top: 70%;
  left: 50%;
  transform: translateX(-50%);
  font-size: 25px;
  color: #888;
  font-weight: 500;
}
</style>