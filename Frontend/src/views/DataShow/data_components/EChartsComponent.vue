<template>
  <div ref="chartRef" class="echarts-container"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  chartType: {
    type: String,
    required: true
  },
  data: {
    type: Object,
    required: true
  }
})

const chartRef = ref(null)
let chartInstance = null

// 初始化图表
const initChart = () => {
  if (!chartRef.value) {
    console.warn('DOM未挂载，无法初始化图表')
    return
  }

  // 清除旧实例（如果存在）
  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)

  // 根据 chartType 动态生成 option
  let option = {}

  switch (props.chartType) {
    case 'gauge':
      option = {
        title: { text: props.data.title },
        series: [{
          type: 'gauge',
          radius: '80%',
          startAngle: 180,
          endAngle: 0,
          min: 0,
          max: props.data.max,
          splitNumber: 10,
          axisLine: { lineStyle: { width: 10 } },
          pointer: { width: 5 },
          detail: { valueAnimation: true, formatter: '{value}' },
          data: [{ value: props.data.value }]
        }]
      }
      break

    case 'pie':
      option = {
        title: false,
        tooltip: {},
        legend: { orient: 'horizontal', left: 'center' },
        series: [{
          name: '占比',
          type: 'pie',
          radius: ['40%', '70%'],
          label: { show: false },
          emphasis: {
            label: { show: true, fontSize: '14', fontWeight: 'bold' }
          },
          labelLine: { show: false },
          data: props.data.seriesData || []
        }]
      }
      break

    case 'bar':
      option = {
        title: { text: props.data.title },
        tooltip: {},
        legend: {
          data: (props.data.seriesData || []).map(item => item.name)
        },
        xAxis: {
          type: 'category',
          data: props.data.categories || []
        },
        yAxis: {},
        series: (props.data.seriesData || []).map(item => ({
          ...item,
          type: 'bar'
        }))
      }
      break

    case 'line':
      option = {
        title: { text: props.data.title },
        tooltip: {},
        legend: {
          data: (props.data.seriesData || []).map(item => item.name)
        },
        xAxis: {
          type: 'category',
          data: props.data.categories || []
        },
        yAxis: {},
        series: (props.data.seriesData || []).map(item => ({
          ...item,
          type: 'line'
        }))
      }
      break
case 'pie2':
  option = {
    title: false,
    tooltip: {
      trigger: 'item'
    },
    legend: false,
    series: [{
  name: props.data.seriesName || 'Access From',
  type: 'pie',
  radius: props.data.radius || '65%',
  center: props.data.center || ['50%', '50%'], // 👈 将饼图垂直方向向上移动
  data: props.data.seriesData || [],
  emphasis: {
    itemStyle: {
      shadowBlur: 10,
      shadowOffsetX: 0,
      shadowColor: 'rgba(0, 0, 0, 0.5)'
    }
  }
}]
  }
  break



  }

  chartInstance.setOption(option)
}

// 窗口大小变化时自动调整图表尺寸
const resizeChart = () => {
  chartInstance?.resize()
}

// 组件挂载后初始化图表
onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

// 清理资源，防止内存泄漏
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})

// 响应 props.data 的变化并重绘图表
watch(
  () => [props.data, props.chartType],
  () => {
    initChart()
  },
  { deep: true }
)
</script>

<style scoped>
.echarts-container {
  width: 100%;
  height: 300px;
}
</style>
