<template>
  <div class="app-container">
    <div class="page_navigate">
      <div
        v-for="page in pages"
        :key="page.id"
        :class="{ selected: currentPage === page.id }"
        @click="toPage(page.id)"
        class="nav-item"
      >
        {{ page.label }}
      </div>
    </div>

    <!-- 主容器 -->
    <div id="container" ref="container"></div>
  </div>
</template>

<script>
import { DocmeeUI } from '@docmee/sdk-ui';

export default {
  name: 'AiPptDemo',
  data() {
    return {
      apiKey: process.env.VUE_APP_API_KEY || 'ak_r_n1lbppv5rrFcmG8E', // 从环境变量获取
      uid: '200109',
      limit: null,
      token: null,
      currentPage: 'creator',
      docmeeUI: null,
      pages: [
        {id: 'creator', label: '生成PPT'},
        {id: 'dashboard', label: 'PPT列表'},
        {id: 'customTemplate', label: '自定义模板'}
      ]
    }
  },
  async mounted() {
    if (location.protocol === 'file:') {
      alert('不支持 file 协议访问，请使用HTTP服务');
      return;
    }

    try {
      this.token = await this.createApiToken();
      if (this.token) {
        this.initializeUI();
      }
    } catch (error) {
      console.error('初始化失败:', error);
      alert('初始化失败，请检查控制台日志');
    }
  },
  beforeUnmount() {
    this.docmeeUI?.destroy();
  },
  methods: {
    // 创建API Token（异步处理）
    async createApiToken() {
      if (!this.apiKey) {
        alert('API Key未配置');
        return null;
      }
      try {
        const response = await fetch('https://docmee.cn/api/user/createApiToken', {
          method: 'POST',
          headers: {
            'Api-Key': this.apiKey,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            uid: this.uid,
            limit: this.limit
          })
        });

        if (!response.ok) throw new Error(`HTTP错误: ${response.status}`);

        const data = await response.json();
        if (data.code !== 0) throw new Error(data.message);
        return data.data.token;

      } catch (error) {
        console.error('Token创建失败:', error);
        alert('认证失败，请检查API Key配置');
        return null;
      }
    },

    // 初始化UI组件
    initializeUI() {
      this.docmeeUI = new DocmeeUI({
        token: this.token,
        container: this.$refs.container,
        page: this.currentPage,
        lang: 'zh',
        mode: 'light',
        isMobile: false,
        background: 'linear-gradient(-157deg,	#87CEFA, #E0FFFF)',
        padding: '40px 20px 0px',
        onMessage: this.handleMessage
      });
    },

    // 统一消息处理器
    handleMessage(message) {
      const handlers = {
        'invalid-token': () => this.handleInvalidToken(),
        'before-generate': (data) => this.handleBeforeGenerate(data),
        'before-create-custom-template': (data) => this.handleBeforeCreateTemplate(data),
        'page-change': (data) => this.currentPage = data.page,
        'before-download': (data) => this.handleBeforeDownload(data),
        'error': (data) => this.handleError(data)
      };

      const handler = handlers[message.type];
      return handler ? handler(message.data) : console.warn('未知消息类型:', message);
    },

    // Token失效处理
    handleInvalidToken() {
      this.createApiToken().then(newToken => {
        if (newToken) {
          this.token = newToken;
          this.docmeeUI.updateToken(newToken);
        }
      });
    },

    // 生成前验证
    handleBeforeGenerate({subtype}) {
      if (!['outline', 'ppt'].includes(subtype)) return false;
      console.log(`开始生成${subtype === 'outline' ? '大纲' : 'PPT'}`);
      return true;
    },

    // 模板创建前验证
    handleBeforeCreateTemplate({totalPptCount}) {
      if (totalPptCount < 2) {
        alert('生成积分不足，无法创建模板');
        return false;
      }
      return true;
    },

    // 下载前处理
    handleBeforeDownload({subject}) {
      return `PPT_${subject}_${Date.now()}.pptx`;
    },

    // 统一错误处理
    handleError({code, message}) {
      const errorMap = {
        88: '生成次数已用完',
        default: `发生错误：${message}`
      };
      alert(errorMap[code] || errorMap.default);
    },

    // 页面跳转
    toPage(pageId) {
      if (this.currentPage === pageId) return;
      this.currentPage = pageId;
      this.docmeeUI.navigate({page: pageId});
    },

    // 跳转示例二
    goToDemo2() {
      if (this.token) {
        window.location.href = `/demo2?token=${encodeURIComponent(this.token)}`;
      } else {
        alert('Token未就绪，无法跳转');
      }
    }
  }
}
</script>

<style scoped>
.app-container {
  width: 100vw;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  background: #f9f9f9; /* 淡灰色背景 */
}

.demo-notice {
  text-align: center;
  padding: 1rem;
  background: #f0f8ff; /* 淡蓝色背景 */
  border-radius: 4px;
  margin-bottom: 1rem;
  color: #555; /* 柔和的文字颜色 */
}

.page_navigate {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.nav-item {
  padding: 0.8rem 1.5rem;
  background: #e6f7ff; /* 淡蓝色按钮背景 */
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  color: #333; /* 柔和的文字颜色 */
}

.nav-item.selected {
  background: linear-gradient(-157deg, #49b9ff, #b3e5fc); /* 淡蓝到淡绿渐变 */
  color: #fff; /* 白色文字 */
}

#container {
  width: 100%;
  height: calc(100vh - 200px);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05); /* 更柔和的阴影 */
  overflow: hidden;
  position: relative;
  background: #ffffff; /* 纯白背景 */
}
</style>