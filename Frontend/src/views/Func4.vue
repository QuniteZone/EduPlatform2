<template>
  <div class="mian_container">
    <div class="about">
      <h2>班会稿生成</h2>
      <h4>助教场景：AI辅助班会稿生成</h4>
    </div>
    <div class="editor-preview-container">
      <!-- @update-preview="updatePreview"：监听子组件Editor 触发的自定义事件 update-preview。
      当 Editor 组件触发该事件时，调用父组件中的方法 updatePreview。 -->
      <Editor class="editor" @update-preview="updatePreview" />
      <Preview class="preview" :content="previewContent" />
    </div>
  </div>
</template>

<script>
import Editor from "./Func4_page/PageEditor.vue";
import Preview from "./Func4_page/PagePreview.vue";

export default {
  name: 'FunctionOne',
  components: {
    Editor,
    Preview,
  },
  data() {
    return {
      previewContent: "NULL"
    };
  },
  methods: {
    updatePreview(newData) {
      this.previewContent = newData;  // 直接更新预览内容
    },
  },
};
</script>

<style scoped>
/* 全局样式设置 */
body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;  /* 设置默认字体 */
  margin: 0;                       /* 清除默认外边距 */
  padding: 0;                      /* 清除默认内边距 */
}

/* 主容器样式 */
.mian_container {
  margin-right: 80px;              /* 右侧外边距 */
  margin-left: 80px;               /* 左侧外边距 */
  margin-top: 40px;                /* 顶部外边距 */
}

/* 标题区域样式 */
.about {
  display: flex;                   /* 使用flex布局 */
  flex-direction: column;          /* 垂直方向排列 */
  align-items: center;             /* 水平居中 */
  justify-content: center;         /* 垂直居中 */
  text-align: center;              /* 文本居中对齐 */
  margin: 2rem auto;               /* 上下外边距2rem，左右自动居中 */
  background: linear-gradient(135deg, #eea0b4 0%, #e9ecef 100%); /* 浅灰色渐变背景 */
  border-radius: 1rem;             /* 圆角边框 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); /* 阴影效果 */
  border: 1px solid rgba(255, 255, 255, 0.3); /* 半透明白色边框 */
  max-width: 10000px;              /* 最大宽度限制 */
  height: 200px;                   /* 固定高度 */
}

/* 主标题样式 */
.about h2 {
  color: #458fd8;                  /* 文字颜色 */
  font-size: 2.5rem;               /* 字体大小 */
  font-weight: 700;                /* 字体粗细 */
  margin-top: 0;                   /* 移除顶部外边距 */
  margin-bottom: 0.5rem;           /* 减小底部外边距 */
  letter-spacing: -0.5px;          /* 字间距 */
  position: relative;              /* 相对定位 */
  padding-top: -10rem;              /* 添加顶部内边距 */
}

/* 副标题样式 */
.about h4 {
  color: #518fc5;                  /* 文字颜色 */
  font-size: 1.3rem;               /* 字体大小 */
  font-weight: 400;                /* 字体粗细 */
  margin: 0;                       /* 移除外边距 */
  padding: 0.8rem 1.5rem;          /* 内边距 */
  background: rgba(255, 255, 255, 0.9); /* 半透明白色背景 */
  border-radius: 1rem;             /* 圆角边框 */
  display: inline-block;           /* 行内块级元素 */
  border: 1px solid rgba(0, 0, 0, 0.05); /* 细边框 */
}

/* 编辑器预览容器样式 */
.editor-preview-container {
  display: flex;                   /* 使用flex布局 */
  gap: 25px;                       /* 子元素间距 */
  height: 50vh;                    /* 设置固定高度 */
  margin-top: 20px;                /* 添加上边距 */
  width: 100%;                     /* 占满父容器宽度 */
}

/* 编辑器和预览区域共用样式 */
.editor,
.preview {
  flex: 0 0 calc(50% - 12.5px);   /* 各占50%宽度，减去间距的一半 */
  border: 1px solid rgba(0, 0, 0, 0.1); /* 边框样式 */
  padding: 15px;                   /* 内边距 */
  box-sizing: border-box;          /* 盒模型计算方式 */
  color: #2c3e50;                  /* 文字颜色 */
  background-color: #ffffff;       /* 背景颜色 */
  border-radius: 10px;             /* 圆角边框 */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); /* 阴影效果 */
  transition: all 0.3s ease;       /* 过渡动画 */
  height: 100%;                    /* 占满容器高度 */
}

.editor:hover,
.preview:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); /* 悬停时加深阴影 */
  transform: translateY(-2px);      /* 悬停时轻微上移 */
}

/* 动画关键帧 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  /* 移动端主容器样式 */
  .mian_container {
    margin: 20px;                  /* 统一外边距 */
  }
  
  /* 移动端编辑器预览容器样式 */
  .editor-preview-container {
    flex-direction: column;         /* 垂直排列 */
    gap: 20px;                      /* 子元素间距 */
    height: auto;                   /* 自动高度 */
  }
  
  .editor,
  .preview {
    flex: 0 0 100%;                /* 移动设备上占满宽度 */
    height: 50vh;                   /* 移动设备上的固定高度 */
  }
}
</style>