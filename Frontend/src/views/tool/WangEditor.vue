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
import { onBeforeUnmount, ref, shallowRef, onMounted, watch, nextTick } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { Memo, Management } from '@element-plus/icons-vue'
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
    placeholder: '请输入内容...',
    MENU_CONF: { /* 菜单配置，下文解释 */ }
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
const downloadPDF = async () => {
    if (editorRef.value) {
        const html = editorRef.value.getHtml()
        const container = document.createElement('div')
        container.innerHTML = html
        container.style.width = '210mm' // 设置宽度为 A4 纸张宽度
        container.style.height = '297mm' // 设置高度为 A4 纸张高度
        container.style.margin = '10mm' // 设置页边距
        container.style.padding = '0'
        container.style.boxSizing = 'border-box'
        container.style.position = 'relative'
        container.style.overflow = 'hidden'
        container.style.fontFamily = "'PingFang SC', 'Microsoft YaHei', sans-serif" // 设置字体
        document.body.appendChild(container) // 将容器添加到 body 中

        await nextTick() // 确保 DOM 更新

        try {
            const canvas = await html2canvas(container, {
                scale: 2, // 提高分辨率
                useCORS: true, // 允许跨域资源
                logging: true // 启用日志
            })
            const imgData = canvas.toDataURL('image/png')
            const pdf = new jsPDF('p', 'mm', 'a4') // 创建 A4 纸张的 PDF
            const imgProps = pdf.getImageProperties(imgData)
            const pdfWidth = pdf.internal.pageSize.getWidth()
            const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width
            pdf.addImage(imgData, 'PNG', 10, 10, pdfWidth - 20, pdfHeight - 20) // 添加图像并设置页边距
            pdf.save('document.pdf')
        } catch (error) {
            console.error('Error generating PDF:', error)
        } finally {
            document.body.removeChild(container) // 移除容器
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