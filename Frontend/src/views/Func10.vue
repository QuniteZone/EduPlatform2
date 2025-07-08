<template>
  <div class="analysis-container">
    <!-- 学生基本学习部分 -->
    <div class="report-card">
      <div class="card-header">
        <h2>学生基本学习</h2>
      </div>
      <div class="student-info">
        <div class="info-grid">
          <div class="info-item">
            <span class="label">学生姓名：</span>
            <span class="value">张三</span>
          </div>
          <div class="info-item">
            <span class="label">科目：</span>
            <span class="value">数据结构</span>
          </div>
          <div class="info-item">
            <span class="label">考试日期：</span>
            <span class="value">2023-10-15</span>
          </div>
          <div class="info-item">
            <span class="label">学习阶段：</span>
            <span class="value">进行中</span>
          </div>
        </div>
        <div class="score-section">
          <div class="total-score">
            <div class="score-value">78</div>
            <div class="score-label">总分</div>
          </div>
          <div class="completion-rate">
            <div class="rate-label">完成度78%</div>
            <div class="progress-bar">
              <div class="progress" :style="{ width: '78%' }"></div>
            </div>
          </div>
        </div>
        <div class="learning-stats">
          <div class="stat-item">
            <div class="stat-number">3</div>
            <div class="stat-text">已掌握</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">4</div>
            <div class="stat-text">待巩固</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">3</div>
            <div class="stat-text">需提高</div>
          </div>
        </div>
      </div>
    </div>
    <!-- 错题分析模块 -->
    <div class="exam-analysis-card">
      <div class="card-header">
        <h2>错题分析</h2>
      </div>
      <div class="wrong-questions-analysis">
        <div class="analysis-summary">
          <div class="summary-item">
            <div class="summary-number error">7</div>
            <div class="summary-label">错题数量</div>
          </div>
          <div class="summary-item">
            <div class="summary-number warning">4</div>
            <div class="summary-label">易错知识点</div>
          </div>
          <div class="summary-item">
            <div class="summary-number info">3</div>
            <div class="summary-label">重点关注</div>
          </div>
        </div>
        <div class="error-distribution">
          <div class="section-title">错题分布</div>
          <div class="distribution-items">
            <div class="distribution-item">
              <div class="item-header">
                <span class="question-number">1.2</span>
                <span class="difficulty medium">中等</span>
              </div>
              <div class="error-reason">概念理解不清</div>
            </div>
            <div class="distribution-item">
              <div class="item-header">
                <span class="question-number">1.3</span>
                <span class="difficulty hard">困难</span>
              </div>
              <div class="error-reason">解题思路不明确</div>
            </div>
            <div class="distribution-item">
              <div class="item-header">
                <span class="question-number">1.6</span>
                <span class="difficulty hard">困难</span>
              </div>
              <div class="error-reason">计算错误</div>
            </div>
          </div>
        </div>
        <div class="improvement-focus">
          <div class="section-title">重点关注</div>
          <div class="focus-tags">
            <div class="focus-tag">数据结构基础概念</div>
            <div class="focus-tag">算法复杂度分析</div>
            <div class="focus-tag">树结构应用</div>
          </div>
        </div>
      </div>
    </div>
    <!-- 学习时长分析部分 -->
    <div class="knowledge-analysis-card">
      <div class="card-header">
        <h2>学习时长分析</h2>
      </div>
      <div class="study-time-content">
        <div class="total-time-section">
          <div class="time-circle">
            <div class="time-number">23.5</div>
            <div class="time-unit">小时</div>
            <div class="time-label">本周总学习时长</div>
          </div>
          <div class="time-comparison">
            <div class="comparison-item">
              <div class="comparison-label">
                <i class="fas fa-arrow-up"></i>
                较上周增长
              </div>
              <div class="comparison-value positive">+2.5h</div>
            </div>
            <div class="comparison-item">
              <div class="comparison-label">
                <i class="fas fa-users"></i>
                班级平均
              </div>
              <div class="comparison-value">20h</div>
            </div>
          </div>
        </div>

        <div class="weekly-distribution">
          <div class="section-title">每日学习时长分布</div>
          <div class="day-bars">
            <div class="day-bar">
              <div class="bar-label">周一</div>
              <div class="bar-wrapper">
                <div class="bar-fill" style="height: 80%">
                  <span class="bar-value">4h</span>
                </div>
              </div>
            </div>
            <div class="day-bar">
              <div class="bar-label">周二</div>
              <div class="bar-wrapper">
                <div class="bar-fill" style="height: 60%">
                  <span class="bar-value">3h</span>
                </div>
              </div>
            </div>
            <div class="day-bar">
              <div class="bar-label">周三</div>
              <div class="bar-wrapper">
                <div class="bar-fill" style="height: 90%">
                  <span class="bar-value">4.5h</span>
                </div>
              </div>
            </div>
            <div class="day-bar">
              <div class="bar-label">周四</div>
              <div class="bar-wrapper">
                <div class="bar-fill" style="height: 70%">
                  <span class="bar-value">3.5h</span>
                </div>
              </div>
            </div>
            <div class="day-bar">
              <div class="bar-label">周五</div>
              <div class="bar-wrapper">
                <div class="bar-fill" style="height: 100%">
                  <span class="bar-value">5h</span>
                </div>
              </div>
            </div>
            <div class="day-bar">
              <div class="bar-label">周六</div>
              <div class="bar-wrapper">
                <div class="bar-fill weekend" style="height: 40%">
                  <span class="bar-value">2h</span>
                </div>
              </div>
            </div>
            <div class="day-bar">
              <div class="bar-label">周日</div>
              <div class="bar-wrapper">
                <div class="bar-fill weekend" style="height: 30%">
                  <span class="bar-value">1.5h</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="time-insights">
          <div class="insight-card">
            <div class="insight-icon">
              <i class="fas fa-clock"></i>
            </div>
            <div class="insight-content">
              <div class="insight-title">最佳学习时段</div>
              <div class="insight-value">19:00 - 21:00</div>
            </div>
          </div>
          <div class="insight-card">
            <div class="insight-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="insight-content">
              <div class="insight-title">单次最长专注</div>
              <div class="insight-value">45分钟</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 学习建议部分 -->
    <div class="learning-suggestion-card">
      <div class="card-header">
        <h2>学习建议</h2>
      </div>
      <div class="learning-content">
        <div class="key-points-section">
          <div class="section-header">
            <i class="fas fa-star"></i>
            <span>重点学习内容</span>
          </div>
          <div class="point-cards">
            <div class="point-card">
              <div class="point-title">
                <i class="fas fa-exclamation-circle"></i>
                百分数的实际应用
              </div>
              <div class="point-detail">
                <div class="progress-bar">
                  <div class="progress" style="width: 35%"></div>
                </div>
                <span class="progress-text">掌握度 35%</span>
              </div>
            </div>
            <div class="point-card">
              <div class="point-title">
                <i class="fas fa-exclamation-circle"></i>
                百分数应用题
              </div>
              <div class="point-detail">
                <div class="progress-bar">
                  <div class="progress" style="width: 45%"></div>
                </div>
                <span class="progress-text">掌握度 45%</span>
              </div>
            </div>
            <div class="point-card">
              <div class="point-title">
                <i class="fas fa-exclamation-circle"></i>
                分数、百分数复合应用
              </div>
              <div class="point-detail">
                <div class="progress-bar">
                  <div class="progress" style="width: 28%"></div>
                </div>
                <span class="progress-text">掌握度 28%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="suggestion-section">
          <div class="section-header">
            <i class="fas fa-lightbulb"></i>
            <span>学习方法建议</span>
          </div>
          <div class="suggestion-list">
            <div class="suggestion-item">
              <div class="suggestion-icon">
                <i class="fas fa-book-reader"></i>
              </div>
              <div class="suggestion-content">
                <h4>加强基础概念理解</h4>
                <p>建议多做相关应用题练习，巩固知识点</p>
              </div>
            </div>
            <div class="suggestion-item">
              <div class="suggestion-icon">
                <i class="fas fa-project-diagram"></i>
              </div>
              <div class="suggestion-content">
                <h4>构建知识体系</h4>
                <p>注重知识点之间的联系，形成完整的知识网络</p>
              </div>
            </div>
            <div class="suggestion-item">
              <div class="suggestion-icon">
                <i class="fas fa-tasks"></i>
              </div>
              <div class="suggestion-content">
                <h4>定期复习</h4>
                <p>每周进行错题复习，分析错误原因并及时改正</p>
              </div>
            </div>
          </div>
        </div>

        <div class="resources-section">
          <div class="section-header">
            <i class="fas fa-book"></i>
            <span>推荐学习资源</span>
          </div>
          <div class="resource-tags">
            <div class="resource-tag">
              <i class="fas fa-video"></i>
              视频讲解
            </div>
            <div class="resource-tag">
              <i class="fas fa-file-alt"></i>
              习题集
            </div>
            <div class="resource-tag">
              <i class="fas fa-chalkboard-teacher"></i>
              在线辅导
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- New Title Container -->
    <div class="title-container">
      <h1>学生个性化报告</h1>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentAnalysis',
  data() {
    return {
      student: {
        name: '张三',
        subject: '数据结构',
        examDate: '2023-10-15',
        score: 78,
        scorePercentage: 78
      },
      examResults: {
        correct: [1.1, 1.4, 1.5],
        incorrect: [1.2, 1.3, 1.6, 1.7, 1.8, 1.9, 2]
      },
      difficulty: {
        '1.1': '低',
        '1.2': '中',
        '1.3': '高',
        '1.4': '低',
        '1.5': '中',
        '1.6': '高',
        '1.7': '低',
        '1.8': '中',
        '1.9': '高',
        '2': '低'
      },
      improvementIndex: [
        { label: '百分数应用题', value: 28 },
        { label: '百分数的意义、读写及应用', value: 15 },
        { label: '百分数的实际应用', value: 13 }
      ],
      keyPoints: [
        '百分数的实际应用',
        '百分数应用题',
        '比与分数、除法的关系',
        '百分数的意义、读写及应用',
        '分数、百分数复合应用题'
      ],
      learningSuggestions: [
        '加强对百分数概念的理解，多做相关应用题练习',
        '注重知识点之间的联系，构建知识体系',
        '定期进行错题复习，分析错误原因'
      ]
    }
  },
  mounted() {
    console.log('学生分析页面已加载');
  },
  methods: {
    // 可以添加交互方法
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

#app {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.analysis-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto 1fr 1fr;
  gap: 8px;
  padding: 8px;
  width: 100vw;
  height: 100vh;
  background-color: #f0f2f5;
  margin: 0;
  overflow: auto;
}

/* 卡片通用样式 */
.card-header {
  background-color: #ffffff;
  padding: 6px 8px;
  border-radius: 6px 6px 0 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  min-height: 32px;
  display: flex;
  align-items: center;
}

h2 {
  font-size: 14px;
  font-weight: 600;
  margin: 0;
  color: #1a1a1a;
}

/* 学情分析报告卡片 */
.report-card {
  grid-row: 2;
  grid-column: 1;
  background-color: #ffffff;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.student-info {
  padding: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
}

.label {
  color: #666;
  margin-right: 8px;
  font-size: 14px;
}

.value {
  color: #333;
  font-weight: 500;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.total-score {
  text-align: center;
  padding: 16px;
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
  border-radius: 50%;
  width: 80px;
  height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: white;
}

.score-value {
  font-size: 24px;
  font-weight: bold;
}

.score-label {
  font-size: 12px;
  margin-top: 4px;
}

.completion-rate {
  flex: 1;
}

.rate-label {
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #4a90e2 0%, #357abd 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.learning-stats {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 0 16px;
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #4a90e2;
  margin-bottom: 4px;
}

.stat-text {
  font-size: 12px;
  color: #666;
}

/* 错题分析模块 */
.exam-analysis-card {
  grid-row: 2;
  grid-column: 2;
  background-color: #ffffff;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.wrong-questions-analysis {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.analysis-summary {
  display: flex;
  justify-content: space-around;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.summary-item {
  text-align: center;
}

.summary-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 4px;
}

.summary-number.error {
  color: #ff4d4f;
}

.summary-number.warning {
  color: #faad14;
}

.summary-number.info {
  color: #1890ff;
}

.summary-label {
  font-size: 12px;
  color: #666;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.distribution-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 8px;
}

.distribution-item {
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.distribution-item:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.question-number {
  font-weight: 500;
  color: #333;
}

.difficulty {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.difficulty.easy {
  background: #e6f7ff;
  color: #1890ff;
}

.difficulty.medium {
  background: #fff7e6;
  color: #faad14;
}

.difficulty.hard {
  background: #fff1f0;
  color: #ff4d4f;
}

.error-reason {
  font-size: 12px;
  color: #666;
}

.improvement-focus {
  flex-shrink: 0;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.focus-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.focus-tag {
  padding: 4px 12px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.3s ease;
}

.focus-tag:hover {
  background: #1890ff;
  color: white;
}

.error-distribution {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.error-distribution::-webkit-scrollbar {
  width: 4px;
}

.error-distribution::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 2px;
}

.error-distribution::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 2px;
}

/* 学习时长分析部分 */
.knowledge-analysis-card {
  grid-row: 3;
  grid-column: 1;
  background-color: #ffffff;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.study-time-content {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.total-time-section {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.time-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 16px;
  text-align: center;
}

.time-number {
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
}

.time-unit {
  font-size: 14px;
  margin-top: 4px;
}

.time-label {
  font-size: 12px;
  margin-top: 4px;
  opacity: 0.9;
}

.time-comparison {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comparison-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.comparison-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.comparison-label i {
  font-size: 12px;
}

.comparison-value {
  font-weight: 500;
  color: #333;
}

.comparison-value.positive {
  color: #52c41a;
}

.weekly-distribution {
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.day-bars {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 160px;
  padding-top: 20px;
}

.day-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.bar-wrapper {
  width: 24px;
  height: 120px;
  background: #f0f0f0;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.bar-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: linear-gradient(180deg, #4a90e2 0%, #357abd 100%);
  border-radius: 12px;
  transition: height 0.3s ease;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.bar-fill.weekend {
  background: linear-gradient(180deg, #91d5ff 0%, #69c0ff 100%);
}

.bar-value {
  color: white;
  font-size: 12px;
  padding: 4px 0;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.bar-wrapper:hover .bar-value {
  opacity: 1;
}

.bar-label {
  font-size: 12px;
  color: #666;
}

.time-insights {
  display: flex;
  gap: 16px;
}

.insight-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.insight-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.insight-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e6f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1890ff;
}

.insight-content {
  flex: 1;
}

.insight-title {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.insight-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

/* 自定义滚动条 */
.study-time-content::-webkit-scrollbar {
  width: 4px;
}

.study-time-content::-webkit-scrollbar-track {
  background: #f0f0f0;
}

.study-time-content::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 2px;
}

/* 学习建议卡片 */
.learning-suggestion-card {
  grid-row: 3;
  grid-column: 2;
  background-color: #ffffff;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.learning-content {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 15px;
  font-weight: 500;
  color: #1a1a1a;
}

.section-header i {
  color: #4a90e2;
}

.point-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.point-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  transition: all 0.3s ease;
}

.point-card:hover {
  transform: translateX(4px);
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.point-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.point-title i {
  color: #ff4d4f;
  font-size: 14px;
}

.point-detail {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #ff4d4f 0%, #ff7875 100%);
  border-radius: 3px;
}

.progress-text {
  font-size: 12px;
  color: #666;
  min-width: 80px;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.suggestion-item:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.suggestion-icon {
  width: 40px;
  height: 40px;
  background: #e6f7ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.suggestion-icon i {
  color: #1890ff;
  font-size: 18px;
}

.suggestion-content h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #333;
}

.suggestion-content p {
  margin: 0;
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

.resource-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.resource-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.resource-tag:hover {
  background: #1890ff;
  color: white;
}

.resource-tag i {
  font-size: 14px;
}

/* 自定义滚动条 */
.learning-content::-webkit-scrollbar {
  width: 4px;
}

.learning-content::-webkit-scrollbar-track {
  background: #f0f0f0;
}

.learning-content::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 2px;
}

/* Add hover effect for all cards */
.report-card:hover, .exam-analysis-card:hover, .knowledge-analysis-card:hover, .learning-suggestion-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
  transition: all 0.3s ease;
}

.title-container {
  grid-column: 1 / -1;
  grid-row: 1;
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
  padding: 16px;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  text-align: center;
  margin-bottom: 8px;
  color: #ffffff;
  transition: all 0.3s ease;
}

.title-container:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
  transform: translateY(-2px);
}

.title-container h1 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}
</style>