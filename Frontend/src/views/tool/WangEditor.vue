<template>
    <div class="main-container">
        <!-- 工具栏 -->
        <Toolbar :editor="editorRef" :defaultConfig="toolbarConfig" class="toolbar" />
        <!-- 编辑器 -->
        <Editor v-model="valueHtml" :defaultConfig="editorConfig" class="editor" @onCreated="handleCreated" />
        <!-- 下载按钮 -->
        <div class="button-group">
            <el-button-group>
                <el-button type="primary" :icon="Memo" @click="downloadWord" size="large">Word</el-button>
                <el-button type="primary" :icon="Management" @click="downloadPDF" size="large">PDF</el-button>
            </el-button-group>
        </div>
    </div>

</template>

<script setup>
import { onBeforeUnmount, ref, shallowRef, onMounted, watch, nextTick} from 'vue'
import {Editor, Toolbar} from '@wangeditor/editor-for-vue'
import {Memo, Management} from '@element-plus/icons-vue'
import htmlToDocx from 'html-docx-js/dist/html-docx';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

// 编辑器实例，必须用 shallowRef，重要！
const editorRef = shallowRef()

// 内容 HTML
const valueHtml = ref('<p>hello</p>')

// 接收 initialContent 属性
const props = defineProps({
  initialContent: {
    type: String,
    default: '<p>hello</p>'
  }
})

// 监听 initialContent 变化
watch(
    () => props.initialContent,
    (newContent) => {
      if (editorRef.value) {
        editorRef.value.setHtml(newContent)
      }
    }
)

// 模拟 ajax 异步获取内容
onMounted(() => {
  setTimeout(() => {
    valueHtml.value = props.initialContent
  }, 1500)
})

// 编辑器配置
const editorConfig = {
  placeholder: '待生成内容...',
  MENU_CONF: { /* 菜单配置，下文解释 */}
}

const handleCreated = (editor) => {
  editorRef.value = editor // 记录 editor 实例，重要！
  editor.setHtml(props.initialContent) // 设置初始内容
}

// 组件销毁时，及时销毁编辑器
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})

// 下载 Word
const downloadWord = () => {

  if (editorRef.value) {
    const html = editorRef.value.getHtml()
    const docx = htmlToDocx.asBlob(html)
    const link = document.createElement('a')
    console.log(editorRef.value)
    console.log(html)
    console.log(docx)
    link.href = URL.createObjectURL(docx)
    link.download = 'document.docx'
    link.click()
  }
}

// 下载 PDF
// 下载 PDF
const downloadPDF = async () => {
  if (editorRef.value) {
    const html = editorRef.value.getHtml();

    // 配置选项
    const options = {
      margin: 10,
      filename: 'document.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    try {
      // 正确导入html2pdf.js库
      const html2pdfModule = await import('html2pdf.js');
      const html2pdf = html2pdfModule.default || html2pdfModule;

      // 生成并下载PDF
      html2pdf().from(html).set(options).save();
    } catch (error) {
      console.error('生成PDF失败:', error);
      alert('导出PDF时出现错误，请稍后再试');
    }
  }
}
</script>

<!-- 别忘了引入样式 -->
<style src="@wangeditor/editor/dist/css/style.css"></style>

<style scoped>
.main-container {
  border: 1px solid #ccc;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.toolbar {
  border-bottom: 1px solid #ccc;
  width: 100%;
}

.editor {
  height: 500px;
  overflow-y: hidden;
  width: 100%;
}

.button-group {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  /* 居中对齐 */
  width: 100%;
  margin-bottom: 2%;
}
</style>