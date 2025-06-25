<template>
  <header class="app-header">
    <h2>个性化学习路径 </h2>
  </header>
  <el-card class="learning-path" v-if="learningData">
    <el-button type="primary" @click="downloadAllStagesHTML" class="export-button">
        导出学习路径
</el-button>
    <h2 class="learning-path-line">
      <img src="@/assets/icons/learning-path-icon.png" class="icon-class-head"/>
      学习路径规划:{{ Plan_Title }}
    </h2>
    <!-- 阶段列表 -->
    <div class="stage-list">
      <div
          v-for="(stage, stageIndex) in learningData.learningPath"
          :key="stageIndex"
          class="stage-item"
          @click="toggleStage(stageIndex)"
          :class="{ 'active': activeStage === stageIndex }"
      >
        <span>
          <strong>{{ stageIndex + 1 }}. {{ stage.stage }}</strong>
          <el-tag size="small" type="info" class="duration-tag">
            <img src="@/assets/icons/time-icon.png" class="duration-icon"/>
            <span class="duration-text">{{ stage.duration }}</span>
          </el-tag>
        </span>
        <p class="icon-class">
          <img src="@/assets/icons/target-icon.png" class="tag-icon"/>
          目标：{{ stage.goal }}
        </p>
        <p class="icon-class">
          <img src="@/assets/icons/suggestion-icon.png" class="tag-icon"/>
          建议：{{ stage.suggestion }}
        </p>
        <i class="el-icon-arrow-right"></i>
      </div>
    </div>
    <!-- 显示当前选中的阶段任务 -->
    <div v-if="activeStage !== null" class="task-details">
      <h3 class="stage-title">
        <img src="@/assets/icons/stage-icon.png" class="tag-icon"/>
        当前阶段：{{ learningData.learningPath[activeStage].stage }}
      </h3>
      <div v-for="(task, taskIndex) in learningData.learningPath[activeStage].tasks" :key="taskIndex" class="task">
        <h4 class="icon-class">
          <img src="@/assets/icons/taskName-icon.png" class="tag-icon"/>
          子任务 {{ taskIndex + 1 }}: {{ task.taskName }}
        </h4>
        <p>{{ task.taskDescription }}</p>
        <div class="task-content-grid">
          <!-- 学习目标 -->
          <div class="task-section target-section">
            <div class="task-section-box">
              <h5 class="icon-class">
                <img src="@/assets/icons/study-target-icon.png" class="tag-icon"/>
                学习目标
              </h5>
              <ul>
                <li v-for="(obj, idx) in task.learningObjectives" :key="idx">{{ obj }}</li>
              </ul>
            </div>
          </div>
          <!-- 视频资源 -->
          <div class="task-section video-section">
            <div class="task-section-box">
              <h5 class="icon-class">
                <img src="@/assets/icons/video-icon.png" class="tag-icon"/>
                视频资源列表
              </h5>
              <ul>
                <li v-for="(res, idx) in task.bili_resource.slice(0, getDisplayCount('video'))" :key="idx"
                    class="resource-item">
                  <!-- 左右布局 -->
                  <div class="video-wrapper">
                    <a :href="res.link" target="_blank">
                      <div class="video-preview">
                        <img
                            :src="res.preview_image_url ? res.preview_image_url : '@/assets/default_preview_image.png'"
                            :alt="res.title"
                            class="video-image"
                        />
                      </div>
                    </a>
                  </div>
                  <div class="resource-info">
                    <a :href="res.link" target="_blank" class="resource-title">{{ res.title }}</a>
                    <div class="summary-container">
                      <p class="summary-text"><strong>视频摘要：</strong>{{ res.video_summary}}</p>
                    </div>
                    <div class="tags-container">
                      <img src="@/assets/icons/tag-icon.png" class="tag-icon"/>
                      <el-tag
                          v-for="(tag, tagIdx) in res.tags"
                          :key="tagIdx"
                          type="info"
                          size="small"
                          effect="plain"
                          class="tag"
                      >
                        {{ tag }}
                      </el-tag>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
          <!-- GitHub 开源项目 -->
          <div class="task-section github-section">
            <div class="task-section-box">
              <h5 class="icon-class">
                <img src="@/assets/icons/github-icon.png" class="tag-icon"/>
                GitHub 开源项目推荐
              </h5>
              <ul v-if="task.github_resource && task.github_resource.length > 0">
                <li v-for="(repo, idx) in task.github_resource.slice(0, getDisplayCount('github'))" :key="idx"
                    class="github-item">
                  <a :href="repo.link" target="_blank" class="github-name">{{ repo.name }}</a>
                  <p class="github-desc">{{ repo.description }}</p>
                  <div class="github-meta">
                    <span>⭐ {{ repo.stars }}</span>
                  </div>
                </li>
              </ul>
              <p v-else>暂无推荐项目</p>
            </div>
          </div>
          <!-- 在线资料 -->
          <div class="task-section online-section">
            <div class="task-section-box">
              <h5 class="icon-class">
                <img src="@/assets/icons/online-icon.png" class="tag-icon"/>
                在线资料列表
              </h5>
              <ul>
                <li v-for="(source, idx) in task.article_resource.slice(0, getDisplayCount('article'))" :key="idx">
                  <a :href="source.link" target="_blank">{{ source.title }}</a>
                  <p style="font-size: 0.85em; color: #666;">{{ source.introduce }}</p>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <el-divider/>
      </div>
    </div>
    <h3 class="final-suggestion-icon">
      <img src="@/assets/icons/final-sugestion.png" class="icon-class-head"/>
      学习建议
    </h3>
    <ul>
      <li v-for="(tip, index) in learningData.suggestion" :key="index">{{ tip }}</li>
    </ul>
  </el-card>
</template>

<script setup>
import {computed, defineProps, ref} from 'vue'
import { nextTick } from 'vue'
// 接收来自父组件传入的 learningData
const props = defineProps({
  learningData: {
    type: Object,
    required: true
  }
})

// 使用 props 中的数据
const learningData = ref(props.learningData)
//console.log("learningData title", learningData.value.title)
const Plan_Title = computed(() => props.learningData?.title || '默认标题')
const activeStage = ref(null)

// 切换阶段显示
const toggleStage = (stageIndex) => {
  if (activeStage.value === stageIndex) {
    activeStage.value = null
  } else {
    activeStage.value = stageIndex
  }
}

// 计算当前任务中应展示的资源数量
const getDisplayCount = (resourceType) => {
  const preference = learningData.value?.preference_type || []
  if (!Array.isArray(preference)) return 1 // 默认只展示一个
  const displayConfig = {
    video: preference.includes('video') ? 3 : 1,
    github: preference.includes('project') ? 3 : 1,
    article: preference.includes('article') ? 3 : 1
  }
  return displayConfig[resourceType] || 1
}

//下载学习路径
const downloadAllStagesHTML = async () => {
  const originalStage = activeStage.value
  const styles = Array.from(document.querySelectorAll('style')).map(style => style.outerHTML).join('\n')
  const title = Plan_Title.value.replace(/[\\/:*?"<>|]/g, '')
  let combinedContent = ''

  for (let i = 0; i < learningData.value.learningPath.length; i++) {
    activeStage.value = i
    await nextTick()

    const stageElement = document.querySelector('.task-details')
    if (!stageElement) continue

    const clone = stageElement.cloneNode(true)
    const stageData = learningData.value.learningPath[i]
    const stageName = stageData.stage.replace(/[\\/:*?"<>|]/g, '')

    const section = `
      <section style="margin-bottom: 40px;">
        <h2>${title} ——${stageName}</h2>
        <p><strong>时间：</strong>${stageData.duration}</p>
        <p><strong>目标：</strong>${stageData.goal}</p>
        <p><strong>建议：</strong>${stageData.suggestion}</p>
        ${clone.outerHTML}
      </section>
    `
    combinedContent += section
  }
  activeStage.value = originalStage
  const html = `
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title>${title} - 所有阶段</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }
    h2, h3, h4 { color: #333; }
    img { max-width: 100%; border-radius: 6px; margin: 5px 0; }
  </style>
  ${styles}
</head>
<body>
  <h1>${title} - 所有阶段学习路径</h1>
  ${combinedContent}
</body>
</html>
  `
  const blob = new Blob([html], { type: 'text/html' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${title}_所有阶段.html`
  link.click()
  URL.revokeObjectURL(link.href)
}
</script>
<style scoped>
.export-button {
  background-color: rgba(122, 138, 117, 0.53);
  color: rgb(87, 80, 80);
  border-radius: 20px;
  border: none;
  padding: 10px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.export-button:hover {
  background-color: rgba(184, 199, 218, 0.25); /* 鼠标悬停时更浅的色 */
}
.learning-path {
  padding: 15px;
  font-size: 12px;
}

.stage-list {
  background-color: rgba(184, 199, 218, 0.51);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.stage-item {
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-bottom: 10px;
  background-color: #fff;
}

.stage-item:hover {
  background-color: #f4f4f5;
}

.stage-item.active {
  background-color: #ecf5ff;
  font-weight: bold;
}

.stage-item p {
  margin: 6px 0 0;
  font-size: 0.9em;
  color: #666;
}

.task-details {
  margin-top: 2px;
}

.task h4 {
  margin-top: 5px;
}

.task-content-grid {
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  gap: 15px;
  padding-bottom: 10px;
}

/* 学习目标 */
.target-section {
  flex: 1 1 15%; /* 设置更窄的宽度 */
  min-width: 50px; /* 最小宽度 */
}

/* 视频资源 */
.video-section {
  flex: 1 1 40%; /* 更宽的宽度，适应视频内容 */
}

/* 在线资源 */
.online-section {
  flex: 1 1 20%;
}

/* 新增：为每个任务小块加边框 */
.task-section-box {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  padding: 12px;
  background-color: rgb(255, 255, 255);
  height: 100%;
}

.task-section h5 {
  margin-bottom: 6px;
  font-size: 1em;
  color: #333;
}

.task ul {
  list-style-type: disc;
  padding-left: 18px;
  margin-bottom: 10px;
  font-size: 0.95em;
}

.task a {
  color: #409EFF;
  text-decoration: none;
  font-size: 0.95em;
}

.task a:hover {
  text-decoration: underline;
}

.resource-title {
  display: block;
  margin-top: 6px;
  font-weight: bold;
}

.resource-item {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
  max-width: 100%;
}

.video-wrapper {
  width: 30%;
  max-width: 200px; /* 缩小视频预览图的最大宽度 */
}

.video-preview {
  width: 100%;
  max-width: 200px;
  overflow: hidden;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  margin-bottom: 8px;
}

.video-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 6px;
  transition: transform 0.3s ease;
}

.resource-info {
  flex: 1;
}

.tags-container {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  flex-wrap: wrap;
  width: 100%;
}

.video-preview:hover .video-image {
  transform: scale(1.05);
}

.icon-class {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 1em;
  color: #333;
}

.learning-path-line {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 2em;
  color: #333;
}

.final-suggestion-icon {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 1.5em;
  color: #333;
}

.tag {
  background-color: rgba(184, 199, 218, 0.25);
  color: #757e8a;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  line-height: 1.2;
}

.duration-tag {
  margin-left: 15px;
  color: #333333;
  height: auto;
  padding: 4px 4px;
  display: inline-flex;
  align-items: center;
}

.duration-text {
  margin-left: 10px;
  font-size: 10px;
  font-weight: bold;
}

.duration-icon {
  width: 15px;
  height: 15px;
  vertical-align: middle;
}

.app-header {
  background-color: rgba(122, 138, 117, 0.53);
  color: white;
  padding: 20px;
  text-align: center;
  height: 50px;
}

.tag-icon {
  width: 15px;
  height: 15px;
}

.icon-class-head {
  width: 25px;
  height: 25px;
}

.summary-text {
  font-size: 0.85em;
  color: #666;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3; /* 限制显示3行 */
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2em;
  max-height: calc(1.2em * 3); /* 3行高度 */
}

/* GitHub 推荐 */
.github-section {
  flex: 1 1 20%;
}

.github-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.github-item:last-child {
  border-bottom: none;
}

.github-name {
  font-weight: bold;
  color: #1e6bb8;
  text-decoration: none;
  display: block;
}

.github-name:hover {
  text-decoration: underline;
}

.github-desc {
  margin: 6px 0;
  font-size: 0.9em;
  color: #666;
  -webkit-line-clamp: 3; /* 限制显示3行 */
}

.github-meta {
  font-size: 0.85em;
  color: #999;
}
</style>
