<template>
  <div class="chat">
    <!-- 问题 -->
    <div style="text-align: right;">
      <div class="el-card chat-right">{{ msg.question }}</div>
    </div>
    <!-- AI回答 -->
    <div style="text-align: left;">
      <div class="el-card chat-left" ref="aiResponse">{{ aiAnswer }}</div>
    </div>
    <!-- 输入框 -->
    <div>
      <el-input v-model="userMessage" placeholder="请输入你的问题"></el-input>
      <el-button @click="sendMessage">发送</el-button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    msg: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      userMessage: '',
      aiAnswer: ''
    };
  },
  methods: {
    async sendMessage() {
      this.aiAnswer = ''; // 清空之前的回答
      const response = await axios.post('/chat', {
        message: this.userMessage,
        image_urls: [] // 根据实际情况添加图片URL
      }, {
        responseType: 'stream'
      });

      const reader = response.data.getReader();
      const decoder = new TextDecoder('utf-8');
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        const chunk = decoder.decode(value, { stream: !done });
        this.aiAnswer += chunk;
        this.$refs.aiResponse.scrollTop = this.$refs.aiResponse.scrollHeight; // 滚动到底部
      }
    }
  }
};
</script>

<style scoped>
.chat {
  max-width: 1000px;
  margin: 0 auto;
  padding-top: 10px;
  padding-bottom: 10px;
  border: 2px solid #3498db;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0);

}

.ai-img {
  height: 36px;
  width: 36px;
}

.chat-left {
  background-color: #f5f6f7 !important;
  display: inline-block;
  box-sizing: border-box;
  width: auto;
  text-align: left;
  border-radius: 12px;
  line-height: 24px;
  max-width: 100%;
  padding: 12px 16px;
  white-space: pre-wrap;
  overflow-y: auto; /* 添加滚动条 */
  height: 200px; /* 设置高度 */
}

.chat-right {
  background-color: #e0dfff;
  display: inline-block;
  box-sizing: border-box;
  width: auto;
  color: #3f3f3f;
  border-radius: 12px;
  line-height: 24px;
  max-width: 100%;
  padding: 12px 16px;
  white-space: pre-wrap;
}
</style>