<template>
  <el-row :gutter="20" class="mind-container">
    <el-col :span="8" class="left-panel">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-input v-model="title" placeholder="输入标题"></el-input>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 10px;">
        <el-col :span="24">
          <el-button type="primary" @click="generateMindMap">生成</el-button>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-input v-model="editorContent" type="textarea" rows="10" placeholder="编辑内容"></el-input>
        </el-col>
      </el-row>
    </el-col>

    <el-col :span="16" class="right-panel">
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
  </el-row>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'
import * as htmlToImage from 'html-to-image'
import { saveAs } from 'file-saver'

export default {
  name: 'HomeView',
  setup() {
    const transformer = new Transformer()

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

    const onSave = async () => {
      const dataUrl = await htmlToImage.toPng(svgRef.value)
      saveAs(dataUrl, 'pastking.png')
    }

    const generateMindMap = async () => {
      try {
        editorContent.value = ''
        mm.value?.setData(null)
        mm.value?.fit()
        const response = await fetch(
          `${process.env.VUE_APP_API_BASE_URL}/v1/chat/completions`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${process.env.VUE_APP_API_KEY}`
            },
            body: JSON.stringify({
              messages: [
                {
                  role: 'system',
                  content: `我将设计思维导图，请以markdown格式输出`
                },
                {
                  role: 'user',
                  content: `${title.value}`
                }
              ],
              stream: true,
              model: `gpt-3.5-turbo`,
              temperature: 0.5,
              presence_penalty: 2
            })
          }
        )

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
              // 流式处理结束，跳出循环
              break
            }
            if (line.startsWith('data: ')) {
              const data = JSON.parse(line.slice(6))
              if (data.choices[0].delta && data.choices[0].delta.content) {
                const deltaContent = data.choices[0].delta.content
                result += deltaContent
                editorContent.value += deltaContent // 实时更新编辑器内容

                // 实时更新思维导图
                nextTick(() => updateMindMap())
              }
            }
          }
        }

        // 流式处理结束后触发一次完整的更新
        nextTick(() => updateMindMap())
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
      svgRef
    }
  }
}
</script>

<style scoped>
/* 样式保持不变 */
</style>

<style scoped>
/* 全局重置 */
html,
body {
    margin: 0;
    padding: 0;
    height: 100%;
}

/* 主容器 */
.mind-container {
    width: 100%;
    height: 95vh;
    display: flex;
    overflow: hidden;
}

/* 左侧面板 */
.left-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
    padding: 20px;
    box-sizing: border-box;
}

/* 右侧面板 */
.right-panel {
    display: flex;
    flex-direction: column;
    flex: 1;
    height: 100%;
    padding: 20px;
    box-sizing: border-box;
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

/* 输入框样式 */
.el-input,
.el-textarea {
    width: 100%;
}

/* 按钮样式 */
.el-button {
    width: 100%;
    margin-bottom: 20px;
}

/* 文本编辑器 */
.el-textarea__inner {
    height: calc(100% - 140px);
    /* 自适应剩余高度 */
}
</style>
