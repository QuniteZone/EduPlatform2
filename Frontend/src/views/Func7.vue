<template>
  <div class="main_container">
    <div class="about">
      <div class="about-header">
        <h2>作业辅导</h2>
        <h4>助学场景：AI作业辅导</h4>
      </div>
    </div>

    <div class="common-layout">
      <el-container>
        <!-- 聊天区域 -->
        <el-main id="chat">
          <div
              class="chat-message"
              v-for="(item, index) in form.msgList"
              :key="index"
          >
            <!-- 用户消息 -->
            <div class="chat-item user">
              <div class="avatar-container">
                <img src="@/image/user-icon.png" alt="用户图标" class="chat-icon"/>
              </div>
              <div class="chat-bubble user">
                <div class="message-content">{{ item.question }}</div>
              </div>
            </div>

            <!-- 机器人消息 -->
            <div class="chat-item bot">
              <div class="avatar-container">
                <img src="@/image/bot-icon.png" alt="机器人图标" class="chat-icon"/>
              </div>
              <div class="chat-bubble bot">
                <div class="message-content" v-html="item.answer"></div>
              </div>
            </div>


          </div>
        </el-main>

        <!-- 输入区域 -->
        <el-row class="chat-input-area">
          <div class="input-wrapper">
            <el-input
                class="input-box"
                @keyup.enter="sendMsg"
                v-model="form.input"
                placeholder="请输入问题..."
            ></el-input>
            <el-button class="send-button" @click="sendMsg">发送</el-button>

            <!-- 文件上传图标 -->
            <el-tooltip
                content="上传作业文件（仅识别文字）,支持word，PDF和各类图片"
                placement="top"
            >
              <el-upload
                  action=""
                  :http-request="customUpload"
                  :show-file-list="false"
                  accept=".jpg,.jpeg,.png,.doc,.docx,.pdf"
                  multiple
              >
                <img
                    src="@/image/upload-icon.png"
                    alt="上传图标"
                    class="upload-icon"
                />
              </el-upload>
            </el-tooltip>
          </div>

          <!-- 文件上传区域 -->
          <div class="uploaded-files">
            <div
                v-for="(file, index) in uploadedFiles"
                :key="index"
                class="file-item"
            >
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
        </el-row>
      </el-container>
    </div>
  </div>
</template>

<script setup>
import {reactive, nextTick, ref} from 'vue'
import chat from './Func7_page/page_chat.vue'

const form = reactive({
  input: '',//输入
  msgList: [] //消息列表
});

// 打字机效果函数
function typeWriter(text, element, speed = 30) {
  let i = 0;
  element.answer = ""; // 清空内容

  return new Promise((resolve) => {
    function typing() {
      if (i < text.length) {
        // 处理换行符和空格
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

    // 添加用户问题到消息列表
    const msg = {
      question: user_question,
      answer: "AI生成中..."
    };
    form.msgList.push(msg);
    form.input = "";
    setScrollToBottom();

    try {
      const response = await fetch("/api/ques/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: user_question,
          image_urls: form.fileIPs || []
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let resultData = "";

      // 清空当前消息的占位符
      const lastMsgIndex = form.msgList.length - 1;

      // 使用流式处理数据
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const {done, value} = await reader.read();
        if (done) break;

        // 解码数据并拼接到结果中
        resultData += decoder.decode(value, {stream: true});

        // 使用打字机效果显示内容
        await typeWriter(resultData, form.msgList[lastMsgIndex], 10);
      }
    } catch (error) {
      console.error("Error:", error);
      form.msgList[form.msgList.length - 1].answer = "生成失败，请稍后重试";
    }
  }
}

/*内容显示过多时自动滑动*/
async function setScrollToBottom() {
  await nextTick()
  let chat = document.querySelector("#chat")
  chat.scrollTop = chat.scrollHeight
}
</script>

<style>
html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  background-color: #f7f9fc;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
  "Helvetica Neue", Arial, sans-serif;
}

#app {
  height: 100%;
}

.main_container {
  padding: 20px 0;
}

.about {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eea0b4 0%, #e9ecef 100%);
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
  max-width: 100%;
  margin: 0 auto;
  padding: 20px;
}

.about-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.about-icon {
  width: 40px;
  height: 40px;
}

.common-layout {
  height: calc(100vh - 260px);
  display: flex;
  flex-direction: column;
}

.uploaded-files {
  margin: 10px 20px;
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
  gap: 5px; /* 文件项之间的间距 */
  background-color: #f7f9fc;
  border-bottom: 1px solid #e0e0e0;
  padding: 5px 0;
  min-height: 40px; /* 设置最小高度，避免布局跳动 */
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
  width: calc(100% - 10px); /* 每列占三分之一宽度，减去间距 */
  box-sizing: border-box;
  flex-basis: calc(100% - 10px); /* 确保每行显示 3 个文件项 */
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
  overflow-y: auto;
  padding: 20px;
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

.chat-input-area {
  background-color: #ffffff;
  border-top: 1px solid #e0e0e0;
  padding: 12px 20px;
  position: sticky;
  bottom: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
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
  opacity: 0.85;
}

.disclaimer {
  color: red;
  font-size: 11px;
  margin-top: 5px;
  text-align: center;
}

@media (max-width: 768px) {
  .chat-message {
    max-width: 100%;
  }

  .chat-bubble {
    padding: 10px 12px;
  }

  .input-box {
    height: 40px;
  }

  .send-button {
    height: 40px;
  }

  /* 图标样式 */
  .user-icon, .bot-icon {
    width: 2px; /* 减小图标宽度 */
    height: 2px; /* 减小图标高度 */
    margin-right: 4px; /* 图标与文本之间的间距 */
    vertical-align: middle; /* 确保图标与文本对齐 */
  }

  .chat-bubble.user {
    background-color: #e0f7fa;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
    display: flex;
    align-items: flex-end;
  }

  .chat-bubble.bot {
    background-color: #f1f1f1;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
    display: flex;
    align-items: flex-end;
  }

}
</style>