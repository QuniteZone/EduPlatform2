<template>
  <div class="mian_container">
    <div class="about">
      <h2>知识点梳理</h2>
      <h4>助学场景：AI辅助自动知识点梳理</h4>
    </div>
    <div class="ci_container">
    <el-col :span="24" class="left-panel"  style="display: flex; flex-direction: column; height: 70vh">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-input v-model="title" type="textarea" rows="4" placeholder="输入标题"></el-input>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 10px;">
        <el-col :span="24">
          <el-button type="primary" @click="generateMindMap" :loading="isSending">生成</el-button>
        </el-col>
      </el-row>
      <div style="margin-bottom: 50px">
      <el-row :gutter="20" style="margin-top: 10px; flex: 1; min-height: 0;">
        <el-col :span="24">
          <el-input v-model="editorContent"  :autosize="{ minRows: 10, maxRows: 15 }" type="textarea" placeholder="编辑内容" ></el-input>
        </el-col>
      </el-row>
        <!-- 新增按钮区域 -->
      <el-row :gutter="20" style="margin-top: 10px;">
        <el-col :span="12">
          <el-button @click="copyContent" type="success" style="width: 100%">快捷复制</el-button>
        </el-col>
        <el-col :span="12">
          <el-button @click="regenerateMindMap" type="warning" style="width: 100%">重新生成</el-button>
        </el-col>
      </el-row>
      </div>
    </el-col>

    <el-col :span="16" class="right-panel" style="display: flex; flex-direction: column; height: 70vh">
      <div class="svg-container">
        <svg ref="svgRef" class="markmap-svg"></svg>
      </div>
      <el-row :gutter="10" class="controls">
        <el-col :span="6">
          <el-button @click="zoomIn">放大</el-button>
        </el-col>
        <el-col :span="6">
          <el-button @click="zoomOut">缩小</el-button>
        </el-col>
        <el-col :span="6">
          <el-button @click="fitToScreen">适应屏幕</el-button>
        </el-col>
        <el-col :span="6">
          <el-button @click="onSave">下载</el-button>
        </el-col>
      </el-row>
    </el-col>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'
import * as htmlToImage from 'html-to-image'
import { saveAs } from 'file-saver'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'HomeView',
  setup() {
    const transformer = new Transformer()
    const isSending = ref(false)
    const title = ref('')
    const editorContent = ref('')

    const mm = ref()
    const svgRef = ref()

    const updateMindMap = () => {
      try {
        const { root } = transformer.transform(editorContent.value)
        mm.value?.setData(root)
        mm.value?.fit()
      } catch (e) {
        console.error('转换失败:', e)
      }
    }

    const zoomIn = () => mm.value?.rescale(1.25)
    const zoomOut = () => mm.value?.rescale(0.8)
    const fitToScreen = () => mm.value?.fit()
    const isCopying = ref(false) // 防止重复点击

    const copyContent = () => {
      if (isCopying.value) return

      // 判断内容是否为空（含空格/换行）
      if (!editorContent.value || editorContent.value.trim() === '') {
        ElMessage({
          type: 'warning',
          message: '编辑框内容为空，无法复制',
        })
        return
      }

      isCopying.value = true

      // 尝试使用现代 API
      navigator.clipboard.writeText(editorContent.value)
        .then(() => {
          ElMessage.success('内容已复制到剪贴板')
        })
        .catch(() => {
          // 降级使用 document.execCommand
          const success = fallbackCopyText(editorContent.value)
          if (success) {
            ElMessage.success('内容已复制到剪贴板（降级方案）')
          } else {
            ElMessage.error('复制失败，请手动复制')
          }
        })
        .finally(() => {
          isCopying.value = false
        })
    }

    // 降级复制方法
    function fallbackCopyText(text) {
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.top = '-9999px'
      textArea.style.left = '-9999px'
      textArea.style.opacity = '0'
      textArea.style.pointerEvents = 'none'

      document.body.appendChild(textArea)
      textArea.select()
      textArea.setSelectionRange(0, textArea.value.length) // 移动端支持

      let success = false
      try {
        success = document.execCommand('copy')
      } catch (err) {
        console.error('Fallback 复制失败', err)
      }

      document.body.removeChild(textArea)
      return success
    }




    // const onSave = async () => {
    //   const dataUrl = await htmlToImage.toPng(svgRef.value)
    //   saveAs(dataUrl, 'pastking.png')
    // }
    const onSave = () => {
      // 获取 SVG 元素
      const svgElement = svgRef.value;
      if (!svgElement) {
        console.error('SVG 元素未找到');
        return;
      }

      // 将 SVG 转换为 XML 字符串
      const serializer = new XMLSerializer();
      const svgData = serializer.serializeToString(svgElement);

      // 创建 Blob 对象
      const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });

      // 创建下载链接并触发下载
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'mindmap.svg';
      link.click();

      // 释放对象 URL
      URL.revokeObjectURL(url);
    };

    const regenerateMindMap = () => {
   if (!editorContent.value || editorContent.value.trim() === '') {
    ElMessage.warning('编辑框内容为空，无法生成')
    return
  }

  isSending.value = true

  // 销毁旧实例
  if (mm.value) {
    mm.value.destroy()
    mm.value = null
  }

  // 重新创建 SVG 实例
  mm.value = Markmap.create(svgRef.value)

  // 使用当前 editorContent 内容生成思维导图
  try {
    const { root } = transformer.transform(editorContent.value)
    mm.value?.setData(root)
    mm.value?.fit()

    // 延迟适配屏幕
    setTimeout(() => {
      fitToScreen()
    }, 100)

    isSending.value = false
  } catch (e) {
    console.error('转换失败:', e)
    isSending.value = false
  }
}

const generateMindMap = async () => {
  if (!title.value || title.value.trim() === '') {
    ElMessage.warning('请输入标题，再生成思维导图')
    return
  }
  try {
    isSending.value = true;
    // 👇 清空编辑内容和思维导图
    editorContent.value = ''
    // 销毁旧实例
    if (mm.value) {
      mm.value.destroy()
      mm.value = null
    }

    // 重新创建实例
    mm.value = Markmap.create(svgRef.value)

    const response = await fetch("/api/ques/kn_chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: [
          {
            role: 'system',
            content: `我是一名设计思维导图设计师，我将会详细分析用户的提出的知识点与要求，设计较为详细的思维导图，并严格按照markdown格式输出`
          },
          {
            role: 'user',
            content: `${title.value}`
          }
        ]
      })
    });

    if (!response.ok) throw new Error('请求失败')

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let result = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n').filter(line => line.trim())
      for (const line of lines) {
        if (line === 'data: [DONE]') {
          break
        }
        if (line.startsWith('data: ')) {
          const message = line.slice(6)
          result += message + '\n'
          editorContent.value += message + '\n'
          nextTick(() => updateMindMap())
        }
      }
    }

     nextTick(() => {
      updateMindMap()
       // 延迟 100ms 确保 SVG 渲染完成
      setTimeout(() => {
        fitToScreen()
      }, 100)
       isSending.value = false
    })
  } catch (error) {
    console.error('生成失败:', error)
  }
}


    onMounted(() => {
      mm.value = Markmap.create(svgRef.value)
      console.assert(mm.value, 'Markmap 初始化失败')
      updateMindMap()
    })

    return {
      title,
      editorContent,
      generateMindMap,
      zoomIn,
      zoomOut,
      fitToScreen,
      onSave,
      svgRef,
      isSending,
      copyContent,
      regenerateMindMap
    }
  }
}
</script>



<style scoped>
body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  /* 设置默认字体 */
  margin: 0;
  /* 清除默认外边距 */
  padding: 0;
  /* 清除默认内边距 */
}

html,
body {
    margin: 0;
    padding: 0;
    height: 100%;
}

/* 主容器 */
.mian_container {
  margin-right: 80px;
  /* 右侧外边距 */
  margin-left: 80px;
  /* 左侧外边距 */
  margin-top: 40px;
  /* 顶部外边距 */
}

/* 标题区域样式 */
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
  background: linear-gradient(135deg, #caf496 0%, #e9ecef 100%);
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

/* 主标题样式 */
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

.ci_container
{
display: flex;
  gap: 20px; /* 左右组件之间的间距 */
  padding: 20px;
  width: 100%; /* 确保占满父容器宽度 */
  height: 100%;
}

/* 左侧面板 */
.left-panel {
  flex: 0 0 30%;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 15px;
  box-sizing: border-box;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  height: 60vh;
  overflow: hidden;
}

/* 右侧面板 */
.right-panel {
  flex: 1;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 15px;
  box-sizing: border-box;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  height: 60vh;
  flex-direction: column;

}

/* SVG容器 */
.svg-container {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    height: calc(100% - 60px);
    /* 减去控制栏高度 */
    background-color: #f8f8f8;
}

.markmap-svg {
    width: 100%;
    height: 100%;
}

/* 控制按钮栏 */
.controls {
    flex-shrink: 0;
    height: 60px;
    margin-top: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}



/* 按钮样式 */
.el-button {
    width: 100%;
    margin-bottom: 20px;
}

/* 文本编辑器 */
.el-textarea__inner {
    height: calc(100% );
    /* 自适应剩余高度 */
}
</style>