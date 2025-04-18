<template>
    <section class="preview">
      <div v-if="content" class="content">
        <WangEditor :initialContent="compiledMarkdown" />
      </div>
      <div v-else>
        待生成内容
      </div>
    </section>
  </template>
  
  <script>
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';  // 安全过滤
  import WangEditor from '@/views/tool/WangEditor.vue';
  
  export default {
    components: {
      WangEditor
    },
    props: {
      content: {
        type: Object,
        required: true
      }
    },
    computed: {
      compiledMarkdown() {
        try {
          if (this.content.status === 0) {
            return '<div class="error-message">内容加载失败，请稍后重试</div>';
          }
          // 解析Markdown并进行安全过滤
          const html = marked.parse(this.content.content || '');
          return DOMPurify.sanitize(html);
        } catch (error) {
          return '<div class="error-message">内容解析失败</div>';
        }
      }
    }
  };
  </script>
  
  <style scoped>
  /* 主容器样式 */
  .preview-main-container {
      width: 800px;                    /* 固定宽度 */
      height: 50vh;                    /* 视口高度的50% */
      padding: 20px;
      box-sizing: border-box;
      background-color: #f5f7fa;
      border-radius: 12px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
      display: flex;                   /* 使用flex布局 */
      flex-direction: column;          /* 垂直方向排列 */
  }
  
  .preview {
      width: 100%;                     /* 占满主容器宽度 */
      height: 100%;                    /* 占满主容器高度 */
      overflow-y: auto;
      border: 2px solid #3498db;      /* 边框样式 */
      border-radius: 10px;            /* 圆角大小 */
      padding: 20px;
      box-sizing: border-box;
      background-color: #fff;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
      transition: all 0.3s ease;      /* 添加过渡效果 */
  }
  
  .preview:hover {
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15); /* 悬停时阴影加深 */
      border-color: #2980b9;          /* 悬停时边框颜色变化 */
  }
  
  .preview-container {
      max-width: 800px;
      margin: 0 auto;
      font-family: Arial, sans-serif;
  }
  
  .section {
      margin-bottom: 30px;
      padding: 20px;
      background-color: #f9f9f9;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;      /* 添加过渡效果 */
  }
  
  .section:hover {
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); /* 悬停时阴影加深 */
      transform: translateY(-2px);    /* 悬停时轻微上浮 */
  }
  
  .section h2 {
      color: #2c3e50;
      border-bottom: 2px solid #3498db;
      padding-bottom: 10px;
      margin-bottom: 20px;
  }
  
  .objectives {
      background-color: #fff;
      padding: 15px;
      border-radius: 6px;
      margin-top: 15px;
  }
  
  .objectives h3 {
      color: #2c3e50;
      margin-bottom: 10px;
  }
  
  .objectives ul {
      list-style-type: disc;
      padding-left: 20px;
  }
  
  .objectives li {
      margin-bottom: 8px;
      line-height: 1.5;
  }
  
  .activity {
      background-color: #fff;
      padding: 15px;
      border-radius: 6px;
      margin-bottom: 15px;
      border-left: 4px solid #3498db;
  }
  
  .activity h3 {
      color: #2c3e50;
      margin-bottom: 10px;
  }
  
  .activity p {
      margin-bottom: 10px;
      line-height: 1.6;
  }
  
  .activity strong {
      color: #2c3e50;
      font-weight: 600;
  }
  
  /* 响应式设计 */
  @media (max-width: 768px) {
      .preview-main-container {
          width: 100%;                /* 在移动设备上占满宽度 */
          height: 50vh;               /* 保持视口高度的50% */
          padding: 10px;
      }
      
      .preview {
          height: 100%;               /* 保持占满主容器高度 */
      }
      
      select {
          height: 7vh; /* 在移动设备上稍微调高一点 */
          font-size: 14px;
          padding: 6px 10px;
      }
      
      select option {
          font-size: 14px;
          padding: 6px;
      }
      
      .preview-container {
          padding: 10px;
      }
      
      .section {
          padding: 15px;
      }
      
      .activity {
          padding: 10px;
      }
  }
  </style>