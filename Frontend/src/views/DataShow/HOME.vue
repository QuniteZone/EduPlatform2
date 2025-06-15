<template>
  <div class="dashboard">
    <div class="title_datashow">
      <h2 class="white-title">课程数据展示</h2>
    </div>
    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 左侧区域 -->
      <div class="right-section">
        <div class="indicator-overview">
          <div style="margin-bottom: 10px">
            <div style="margin-bottom: 10px">
              <el-icon size="large"><Search /></el-icon>
              <span style="font-size: 18px;">&nbsp;&nbsp;&nbsp;课程搜索</span>
            </div>
            <el-autocomplete
              v-model="state1"
              :fetch-suggestions="querySearch"
              clearable
              class="inline-input w-50"
              placeholder="Please Input"
              @select="handleSelect"
              @blur="handleBlur"
            />
          </div>
          <div style="display: flex; align-items: center; margin-top: 25px">
            <el-icon size="large"><Files /></el-icon>
            <span style="font-size: 18px;">&nbsp;&nbsp;&nbsp;指标总览</span>
          </div>
          <div class="card-group">
            <ChartCard title="学生数" :value="mockData.studentCount" color="#007bff" :title-size="15" :value-size="20" background="linear-gradient(135deg, #0ebeff, #25dbcb)"/>
            <ChartCard title="班级数" :value="mockData.classCount" color="#28a745" :title-size="15" :value-size="20" background="linear-gradient(135deg, #2be2bf, #3cf898)"/>
          </div>
          <div class="card-group-plus">
            <ChartCard title="总学习次数" :value="mockData.learningCount" color="#ff9900" :title-size="9" :value-size="14" background="linear-gradient(135deg, #0ebeff, #14c5f2)"/>
            <ChartCard title="总学习时长" :value="mockData.learningDuration" color="#007bff" :title-size="9" :value-size="14" background="linear-gradient(135deg, #1acce5, #1fd4d8)"/>
            <ChartCard title="人均学习次数" :value="mockData.avgLearningFrequency" color="#00bfff" :title-size="9" :value-size="14" background="linear-gradient(135deg, #25dbcb, #2be2bf)"/>
            <ChartCard title="人均学习时长" :value="mockData.avgLearningDuration" color="#28a745" :title-size="9" :value-size="14" background="linear-gradient(135deg, #31e9b2, #36f1a5)"/>
          </div>
        </div>

        <div class="learning-trend">
          <div style="display: flex; align-items: center; margin-top: 25px; margin-bottom: 15px">
            <el-icon><DataLine /></el-icon>
            <span style="font-size: 18px;">&nbsp;&nbsp;&nbsp;近一周学习情况</span>
          </div>
          <EChartsComponent
            chartType="line"
            :data="mockData.weeklyLearningTrend"
          />
        </div>
      </div>

      <!-- 中心区域 -->
      <div class="center-section">
        <!-- 上半部分 -->
        <div class="center-top">
          <router-link to="/DataShow/KnowledgeGraphPage">
            <el-button type="primary" size="large" link>
              <el-icon size="large"><DataAnalysis /></el-icon>
              <span style="font-size: 18px;">课程知识图谱</span>
            </el-button>
          </router-link>
          <div class="graph-container">
            <KnowledgeGraph
              v-if="mockData.knowledgeGraphUrl"
              :graph-data-url="mockData.knowledgeGraphUrl"
            />
          </div>
        </div>
        <!-- 下半部分 -->
        <div class="center-bottom">
          <div class="pie-container">
            <div class="pie-item">
              <div style="display: flex; align-items: center;margin-bottom: 15px">
                <el-icon size="large"><Files /></el-icon>
                <span style="font-size: 18px;">&nbsp;&nbsp;&nbsp;课程考察情况</span>
              </div>
              <EChartsComponent chartType="pie" :data="mockData.pie1Data" style="height: 30vh;"/>
            </div>
            <div class="pie-item">
                <div style="display: flex; align-items: center; margin-bottom: 15px">
                  <el-icon size="large"><Files /></el-icon>
                  <span style="font-size: 18px;">&nbsp;&nbsp;&nbsp;学生专业分布</span>
                </div>
                <EChartsComponent chartType="pie2" :data="mockData.pie2Data" style="height: 30vh;" />
              </div>
          </div>
        </div>
      </div>

      <!-- 右侧区域 -->
      <div class="left-section">
        <div class="ranking-table">
          <div style="display: flex; align-items: center; margin-bottom: 15px">
            <el-icon size="large"><Bell /></el-icon>
            <span style="font-size: 18px;">&nbsp;&nbsp;&nbsp;最新学习动态</span>
          </div>
          <el-table :data="mockData.topClassProgress"  style="width: 100%">
            <el-table-column prop="stu" label="学号" width="60" />
            <el-table-column prop="time" label="学习时间" width="130" />
            <el-table-column prop="chapter" label="章节名称" />
          </el-table>
<!--          <DataTable :data="mockData.topClassProgress" />-->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElButton } from 'element-plus'
import axios from 'axios';
import { reactive } from 'vue'
import EChartsComponent from './data_components/EChartsComponent.vue';
import ChartCard from './data_components/ChartCard.vue';
import DataTable from './data_components/DataTable.vue';
import KnowledgeGraph from './data_components/KnowledgeGraph.vue';
// 定义后端返回数据格式 ： mockData 类型（可选）
interface MockData {
  studentCount: number
  classCount: number
  knowledgeGraphUrl: string | null
  learningCount: string
  learningDuration: string
  avgLearningDuration: string
  avgLearningFrequency: string
  weeklyLearningTrend: any
  pie1Data: any
  pie2Data: any
  topClassProgress: Array<{ ranking: string; unitName: string; quantity: number }>
}
// 数据绑定
// const mockData = ref<MockData | null>(null)
const mockData = reactive<MockData>({
  studentCount: 0,
  classCount: 0,
  knowledgeGraphUrl: null,
  learningCount: '',
  learningDuration: '',
  avgLearningDuration: '',
  avgLearningFrequency: '',
  weeklyLearningTrend: { seriesData: [] },
  pie1Data: { seriesData: [] },
  pie2Data: {},
  topClassProgress: []
})
const state1 = ref('')
const restaurants = ref<{ value: string }[]>([])

//请求后端接口获取 图表&统计指标 数据
const getMockDataFromBackend = async (keyword: string): Promise<MockData | null> => {
  try {
    const response = await axios.post('/api/user/course_data', { keyword })
    return response.data
  } catch (error) {
    console.error('请求失败:', error)
    return mockData_test
  }
}

// 课程搜索逻辑
import { onMounted, ref } from 'vue'

const handleBlur = async () => {
  const keyword = state1.value;
  if (!keyword) {
    console.warn('关键词为空，不发起请求');
    return;
  }
  try {
    const fetchedData = await getMockDataFromBackend(keyword);
    if (fetchedData) {
      Object.assign(mockData, fetchedData);
    }
  } catch (err) {
    console.error('Blur 请求出错:', err);
  }
}

const querySearch = async (queryString: string, cb: any) => {
  const results = queryString
    ? restaurants.value.filter(createFilter(queryString))
    : restaurants.value
  cb(results)
}
const createFilter = (queryString: string) => {
  return (suggestion: { value: string }) => {
    return (
      suggestion.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0
    )
  }
}
const loadAll = () => {
  return [
    { value: '素质素养' },
    { value: '测试1' },
    { value: '测试2' }
  ]
}

const handleSelect = (item: Record<string, any>) => {
  console.log(item)
}

onMounted(() => {
  restaurants.value = loadAll()
})


// 模拟数据（含图表数据）
const mockData_test = {
  // 数字指标卡片
  studentCount: 67879,
  classCount: 2081,
  // 图谱路径
  knowledgeGraphUrl: '/All_shuzi_Xiaorong.json',
  // 学习相关指标
  learningCount: '21亿次',
  learningDuration: '84万小时',
  avgLearningFrequency: '5.1次/周',
  avgLearningDuration: '17.5小时',

  // 折线图：近一周学习情况
  weeklyLearningTrend: {
    title: '数字素养',
    categories: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    seriesData: [
      { name: '学习人次', data: [690, 526, 650, 300, 122, 74, 62] },
    ],
  },
  // 考察情况分布
  pie1Data: {
    title: '',
    seriesData: [
      { name: '选择题', value: 541 },
      { name: '填空题', value: 273 },
      { name: '判断题', value: 322 },
      { name: '简答题', value: 90 },
      { name: '计算题', value: 40 },
      { name: '应用题', value: 17 },
    ],
    legend: true
  },
  pie2Data: {
  title: '学生专业分布',
  subtext: '学生专业分布',
  seriesName: '学生专业分布',
  radius: '50%',
  seriesData: [
    { value: 1048, name: '计算机技术' },
    { value: 904, name: '电子信息' },
    { value: 516, name: '大数据' },
    { value: 102, name: '数学' },
    { value: 1048, name: '大数据' },
    { value: 79, name: '信息媒体技术' },
    { value: 484, name: '软件工程' },
    { value: 484, name: '物联网工程' },
    { value: 169, name: '统计学' },
    { value: 210, name: '自动化' }
  ]
},
  // 表格数据 - 排行榜
  topClassProgress: [
      { stu: '001', time: '2024/6/14 12:00', chapter: '机器学习' },
      { stu: '0002', time: '2024/6/14  12:00', chapter: '机器学习与人工智能' },
      { stu: '001', time: '2024/6/14 12:00', chapter: '机器学习' },
      { stu: '0002', time: '2024/6/14  12:00', chapter: '机器学习与人工智能' },
      { stu: '001', time: '2024/6/14 12:00', chapter: '机器学习' },
      { stu: '0002', time: '2024/6/14  12:00', chapter: '机器学习与人工智能' },
      { stu: '001', time: '2024/6/14 12:00', chapter: '机器学习' },
      { stu: '0002', time: '2024/6/14  12:00', chapter: '机器学习与人工智能' },
      { stu: '001', time: '2024/6/14 12:00', chapter: '机器学习' },
      { stu: '0002', time: '2024/6/14  12:00', chapter: '机器学习与人工智能' },
      { stu: '001', time: '2024/6/14 12:00', chapter: '机器学习' },
      { stu: '0002', time: '2024/6/14  12:00', chapter: '机器学习与人工智能' },
      { stu: '001', time: '2024/6/14 12:00', chapter: '机器学习' },
      { stu: '0002', time: '2024/6/14  12:00', chapter: '机器学习与人工智能' },
      { stu: '001', time: '2024/6/14 12:00', chapter: '机器学习' },
      { stu: '0002', time: '2024/6/14  12:00', chapter: '机器学习与人工智能' },
  ]
};
</script>

<style scoped>
.title_datashow {
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
  background: linear-gradient(135deg,  #1cc6dd,  #30e4b2);
  /* 浅灰色渐变背景 */
  border-radius: 1rem;
  /* 圆角边框 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  /* 阴影效果 */
  border: 1px solid rgba(255, 255, 255, 0.3);
  margin-bottom: 10px;
  /* 半透明白色边框 */
  max-width: 10000px;
  /* 最大宽度限制 */
  height: 50px;
  /* 固定高度 */
}
.white-title {
  color: white;
  font-family: 'FZLanTingHeiS-R-GB', 'SimHei', sans-serif; /* 方正兰亭黑为例 */
  font-size: 24px;
}
.dashboard {
  padding-bottom: 20px;
  padding-right: 20px;
  padding-left: 20px;
  background-color: #f5f8fd;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}

.card-group {
  display: flex; /* 允许卡片换行 */
  gap: 10px;
  margin-top: 15px;
}
.card-group-plus {
  display: flex; /* 允许卡片换行 */
  gap: 10px;
  margin-top: 15px;
}

.main-content {
  display: grid;
  grid-template-columns: minmax(250px, 25%) minmax(300px, 50%) minmax(250px, 25%);
  gap: 20px;
  margin-bottom: 24px;
  max-width: 100vw;
  max-height: 100vh;
  overflow-x: hidden;
  box-sizing: border-box;
}

.left-section,
.right-section {
  background-color: #fff;
  padding-right: 20px;
  padding-left: 20px;
  padding-top: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
  height: 92vh;
}

.center-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 上半部分 - 独立白底 */
.center-top {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 50vh;
}
/* 下半部分 - 独立白底 */
.center-bottom {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 40vh;
}
.graph-container {
  width: 100%;
  height: 100%;
}

.pie-container {
  display: flex;
  flex-wrap: wrap; /* 移动端自动换行 */
  justify-content: space-between;
  gap: 20px;
}

.pie-item {
  flex: 1 1 45%; /* 自适应宽度，移动端自动换行 */
  min-width: 250px;
  box-sizing: border-box;
}

</style>