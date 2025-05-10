<template>
  <div class="main_container">
    <div class="about">
      <h2>作业辅导</h2>
      <h4>助学场景：AI作业辅导</h4>
    </div>
    <div class="common-layout">
      <el-container>
        <el-container class="split-container">
          <!-- 左边容器：聊天区域 -->
          <el-aside width="70%" class="chat-container">
            <div
              id="chat"
              :class="form.msgList.length === 0 ? 'nodata' : ''"
            >
              <div
                class="chat-message"
                v-for="(item, index) in form.msgList"
                :key="index"
              >
                <!-- 用户消息 -->
                <div class="chat-item user">
                  <div class="avatar-container">
                    <img src="@/image/user-icon.png" alt="用户图标" class="chat-icon" />
                  </div>
                  <div class="chat-bubble user">
                    <div class="message-content">{{ item.question }}</div>
                  </div>
                </div>
                <!-- 机器人消息 -->
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

          <!-- 右边容器：输入框和上传文件区域 -->
          <el-main class="input-container">
            <div class="input-wrapper">
              <el-input
                class="input-box"
                @keyup.enter="sendMsg"
                v-model="form.input"
                placeholder="请输入问题..."
              ></el-input>
              <el-button class="send-button" @click="sendMsg">发送</el-button>
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
          </el-main>
        </el-container>
      </el-container>
    </div>
  </div>
</template>

<script setup>
import { reactive, nextTick, ref } from 'vue';
import axios from "axios";

// 定义响应式变量
const form = reactive({
  input: '',
  msgList: [],
  fileIPs: []
});

let LLMs_messages= []; // 用于存储 LLMs 的消息


// typeWriter 函数用于模拟打字机效果，逐字符地将文本内容显示到指定的元素中。
function typeWriter(text, element, speed = 30) {
  let i = 0; // 当前处理的字符索引
  const currentAnswer = element.answer || ""; // 获取当前的 answer 内容
  element.answer = currentAnswer; // 初始化目标元素的 answer 属性为当前内容

  return new Promise((resolve) => {
    /**
     * 内部递归函数 typing，逐字符处理文本内容。
     */
    function typing() {
      if (i < text.length) { // 如果还未处理完所有字符
        if (text.charAt(i) === '\n') { // 如果当前字符是换行符
          element.answer += '<br>'; // 添加 HTML 换行标签
        } else if (text.charAt(i) === ' ') { // 如果当前字符是空格
          element.answer += '&nbsp;'; // 添加 HTML 空格实体
        } else { // 其他字符直接添加
          element.answer += text.charAt(i);
        }
        i++; // 移动到下一个字符
        setScrollToBottom(); // 调用滚动到底部的函数，确保新内容可见
        setTimeout(typing, speed); // 延迟调用自身，实现逐字符显示效果
      } else {
        resolve(); // 所有字符处理完毕后 resolve Promise
      }
    }
    typing(); // 开始执行递归函数
  });
}



function parseLLMContent(llm_return_content) {
  let think_content = ""; // 存储 <think> 标签内的思考过程
  let other_content = ""; // 存储非 <think> 标签的输出内容
  let inside_think = false; // 标记是否在 <think> 标签内
  let buffer = ""; // 缓存 <think> 标签内的内容

  // 按行分割内容（假设每行以换行符分隔）
  const lines = llm_return_content.split("\n");

  // 遍历每一行内容
  for (const line of lines) {
    if (line.includes("<think>")) {
      // 进入 <think> 标签
      inside_think = true;
      // 提取 <think> 标签后的内容
      const start_index = line.indexOf("<think>") + "<think>".length;
      buffer += line.substring(start_index).trim() + "\n";
    } else if (line.includes("</think>")) {
      // 离开 </think> 标签
      inside_think = false;
      // 提取 </think> 标签前的内容
      const end_index = line.indexOf("</think>");
      buffer += line.substring(0, end_index).trim() + "\n";
      think_content += buffer.trim() + "\n"; // 将缓存内容添加到 think_content
      buffer = ""; // 清空缓存
      // 提取 </think> 标签后的内容
      other_content += line.substring(end_index + "</think>".length).trim() + "\n";
    } else if (inside_think) {
      // 在 <think> 标签内，继续收集内容
      buffer += line.trim() + "\n";
    } else {
      // 不在 <think> 标签内，直接添加到 other_content
      other_content += line.trim() + "\n";
    }
  }

  // 返回解析结果
  return {
    think_content: think_content.trim(), // 去除多余的换行符
    other_content: other_content.trim() // 去除多余的换行符
  };
}


/**
 * sendMsg 函数用于发送用户输入的消息，并通过 API 获取 AI 的回复，同时支持流式接收和显示回复内容。
 */
 async function sendMsg() {
  if (form.input.length > 0) { // 如果用户输入框中有内容
    const user_question = form.input; // 获取用户输入的内容
    const msg = {
      question: user_question, // 用户问题
      answer: "AI生成中..." // 初始状态显示“AI生成中...”
    };
    form.msgList.push(msg); // 将消息对象添加到消息列表中
    form.input = ""; // 清空输入框
    setScrollToBottom(); // 滚动到底部，确保新消息可见

    const llm_cont={
      'role':'user',
      'content':user_question,
    }
    let llm_return_content="" //LLMs返回的内容
    LLMs_messages.push(llm_cont);
    console.log('LLMs_messages'+LLMs_messages);

    try {
      // 发送 POST 请求到服务器，获取 AI 回复
      const response = await fetch("/api/ques/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          // message: user_question, // 用户问题
          message: LLMs_messages, // 用户问题
          image_urls: form.fileIPs || [] // 文件上传后的 IP 地址列表
        })
      });
      

      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`); // 如果响应状态码不为 2xx，抛出错误

      const reader = response.body.getReader(); // 获取流式数据读取器
      const decoder = new TextDecoder(); // 创建解码器，用于将二进制数据转换为字符串
      const lastMsgIndex = form.msgList.length - 1; // 获取最后一条消息的索引
      let flag = 0;
      // 使用 while 循环流式读取服务器返回的数据
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read(); // 读取流中的数据
        if (done) break; // 如果读取完成，退出循环
        const chunk = decoder.decode(value, { stream: true }); // 解码当前数据块
        console.log("flag:", flag)
        flag += 1;
        console.log("Received chunk:", chunk) 
        await typeWriter(chunk, form.msgList[lastMsgIndex], 10); // 使用 typeWriter 函数逐字符显示当前数据块
        llm_return_content += chunk; // 将当前数据块添加到 LLMs_messages 中
        
      }

      //llm_return_content //待解析对象内容
      let think_content="" // LLMs的思考过程
      let other_content="" // LLMs的输出
      let parse_result=parseLLMContent(llm_return_content);
      if(parse_result.think_content.length>0){
        think_content=parse_result.think_content;
        other_content=parse_result.other_content;
      }else{
        think_content=llm_return_content;
      }
      console.log("think_content:", think_content);
      console.log("other_content:", other_content);

      LLMs_messages.push({
          'role':'assistant',
          'content':other_content,
        });


    } catch (error) {
      console.error("Error:", error); // 捕获并打印错误信息
      form.msgList[form.msgList.length - 1].answer = "生成失败，请稍后重试"; // 更新最后一条消息的状态为“生成失败”
    }
  }
}

const uploadedFiles = ref([]); // 初始化 uploadedFiles

// 文件上传方法
async function customUpload(fileData) {
  const formData = new FormData();
  formData.append("file", fileData.file);
  try {
    const response = await axios.post("/api/ques/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });

    // 校验后端返回数据
    if (response.data && response.data.fileIP) {
      const fileIP = response.data.fileIP;
      const fileName = fileData.file.name;

      // 如果是图片，生成预览 URL
      let previewUrl = null;
      if (["image/jpeg", "image/png", "image/jpg"].includes(fileData.file.type)) {
        const reader = new FileReader();
        previewUrl = await new Promise((resolve) => {
          reader.onload = () => resolve(reader.result);
          reader.readAsDataURL(fileData.file);
        });
      }

      // 添加到 uploadedFiles 和 form.fileIPs
      uploadedFiles.value.push({
        name: fileName,
        previewUrl: previewUrl
      });
      form.fileIPs.push(fileIP);

      //alert("文件上传成功！");
    } else {
      throw new Error("后端返回数据不完整");
    }
  } catch (error) {
    alert("文件上传失败");
    console.error("文件上传失败:", error);
  }
}

// 删除文件方法
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
  margin-right: 80px;
  /* 右侧外边距 */
  margin-left: 80px;
  /* 左侧外边距 */
  margin-top: 40px;
  /* 顶部外边距 */
}
.about {
  display: flex;
  /* 使用flex布局 */
  flex-direction: column;
  /* 垂直方向排列 */
  align-items: center;
  /* 水平居中 */
  justify-content: center;
  /* 垂直居中 */
  text-align: center;
  /* 文本居中对齐 */
  margin: 2rem auto;
  /* 上下外边距2rem，左右自动居中 */
  background: linear-gradient(135deg, #a7e6e5 0%, #e9ecef 100%);
  /* 浅灰色渐变背景 */
  border-radius: 1rem;
  /* 圆角边框 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  /* 阴影效果 */
  border: 1px solid rgba(255, 255, 255, 0.3);
  /* 半透明白色边框 */
  max-width: 10000px;
  /* 最大宽度限制 */
  height: 200px;
  /* 固定高度 */
}

.about h2 {
  color: #458fd8;
  /* 文字颜色 */
  font-size: 2.5rem;
  /* 字体大小 */
  font-weight: 700;
  /* 字体粗细 */
  margin-top: 0;
  /* 移除顶部外边距 */
  margin-bottom: 0.5rem;
  /* 减小底部外边距 */
  letter-spacing: -0.5px;
  /* 字间距 */
  position: relative;
  /* 相对定位 */
  padding-top: -10rem;
  /* 添加顶部内边距 */
}

/* 副标题样式 */
.about h4 {
  color: #518fc5;
  /* 文字颜色 */
  font-size: 1.3rem;
  /* 字体大小 */
  font-weight: 400;
  /* 字体粗细 */
  margin: 0;
  /* 移除外边距 */
  padding: 0.8rem 1.5rem;
  /* 内边距 */
  background: rgba(255, 255, 255, 0.9);
  /* 半透明白色背景 */
  border-radius: 1rem;
  /* 圆角边框 */
  display: inline-block;
  /* 行内块级元素 */
  border: 1px solid rgba(0, 0, 0, 0.05);
  /* 细边框 */
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
