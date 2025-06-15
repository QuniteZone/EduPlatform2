<template>
  <div ref="chartRef" class="echarts-container"></div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount, watch} from 'vue'
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

  chartInstance = echarts.init(chartRef.value)

  // 根据 chartType 动态生成 option
  let option = {}

  switch (props.chartType) {
    case 'g_radar':
      option = {

    color: ['#67F9D8', '#FFE434', '#56A3F1', '#FF917C'],
    title: {
      text: props.data.title
    },

    radar: [
      {
        indicator: props.data.indicators ,
        center: ['50%', '50%'],
        radius: '70%',
        axisName: {
            color: '#2c5c98',              // 文字颜色
            backgroundColor: 'rgba(0, 0, 0, 0)',    // 背景色
            padding: [0, 0],            // 内边距
            fontSize:16,
            fontWeight: 'bold',
             formatter: function (value) {
            if (value.length <= 6) { // 如果字符串长度小于等于6，直接显示完整内容
              return value;
            } else {
              // 显示前3个字符 + ... + 后3个字符
              return value.substring(0, 5) + '...' ;
            }

          },
        },
        //内部颜色


      }
    ],
    series: [
      {
        type: 'radar',
        radarIndex: 0,
        data: props.data.seriesData.map(item => ({
          ...item,
          // 保留原始配置中的默认样式，同时允许用户自定义
          symbolSize: item.symbolSize || 12,

          label: item.label || {
            show: true,
            formatter: function(params) {
              return Number(params.value).toFixed(2);
            }
          },
           // 设置数据区域填充颜色为红色半透明

        }))
      }
    ]

  };
        break

    case 'b_radar':
      option = {

    color: ['#67F9D8', '#FFE434', '#56A3F1', '#FF917C'],
    title: {
      text: props.data.title
    },

    radar: [
      {
        indicator: props.data.indicators ,
        center: ['50%', '50%'],
        radius: '70%',
        axisName: {
          color: '#b34633',              // 文字颜色
          backgroundColor: 'rgba(0, 0, 0, 0)',    // 背景色
          padding: [0, 0],            // 内边距
          fontSize: 16,
          fontWeight: 'bold',
          formatter: function (value) {
            if (value.length <= 6) { // 如果字符串长度小于等于6，直接显示完整内容
              return value;
            } else {
              // 显示前3个字符 + ... + 后3个字符
              return value.substring(0, 5) + '...' ;
            }

          },
          //内部颜色
        }

      }
    ],
    series: [
      {
        type: 'radar',
        radarIndex: 0,
        data: props.data.seriesData.map(item => ({
          ...item,
          // 保留原始配置中的默认样式，同时允许用户自定义
          symbolSize: item.symbolSize || 12,


          label: item.label || {
            show: true,
            formatter: function(params) {
              return Number(params.value).toFixed(2);
            }
          },

           // 设置数据区域填充颜色为红色半透明
        areaStyle: {
          color: 'rgba(255, 0, 0, 0.3)'
        },
         lineStyle: {
        color: '#eca9aa',  // 红色边界线

      }

        }))
      }
    ]

  };
        break

    case 'pie':
      option = {
  title: {
    text: props.data.title,
    left: 'center',
    top: '5%'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {d}%',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    textStyle: { color: '#333' }
  },

  series: [{
    name: '占比',
    type: 'pie',
    radius: ['0%', '40%'],
    center: ['50%', '50%'],
    selectedMode: 'single',
    selectedOffset: 20,

    // 颜色配置
    color: [
      '#a2e49c', '#f4e74b', '#2c5c98',

    ],

    // 数据标签
    label: {
      show: true,
      position: 'outside',
      formatter: '{b|{b}: }\n {d|{d}%}',
      rich: {
        b: { fontSize: 16, fontWeight: 'bold' },
        d: { fontSize: 20,fontWeight: 'bold' },
      }
    },
    // 样式优化
    itemStyle: {
      shadowBlur: 20,
      shadowColor: 'rgba(0, 0, 0, 0.1)',
      borderRadius: 4
    },

    // 高亮效果
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowOffsetX: 0,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    },

    // 中心标题

    data: props.data.seriesData
  }]
};
      break

    case 'bar':
      option = {
        title: { text: props.data.title },
        tooltip: {},
        legend: { data: props.data.seriesData.map(item => item.name) },
        xAxis: { type: 'category', data: props.data.categories },
        yAxis: {},
        series: props.data.seriesData.map(item => ({
          ...item,
          type: 'bar'
        }))
      }
      break

    case 'line':
      option = {
        title: { text: props.data.title },
        tooltip: {formatter: '{a} <br/>第{b}天: {c}'},
        xAxis: {
          name: props.data.x_name,
           boundaryGap: false,
          type: 'category', data: props.data.categories },
        yAxis: {
          type: 'value',
          min: 0,
          name: props.data.y_name,
          data: props.data.y_value},
        series: props.data.seriesData.map(item => ({
          ...item,
          type: 'line',
           label: {
      show: true,                   // 显示数据标签
      position: 'top',              // 标签位置在上方
      formatter: '{c}'              // 显示整数值
    }
        }))
      }
      break
  }

  chartInstance.setOption(option)
}

// 窗口大小变化时自动调整图表尺寸
const resizeChart = () => {
  chartInstance?.resize()
}
//监听data属性变化
watch(
  () => props.data,
  (newData, oldData) => {
    if (newData !== oldData) {
      console.log('数据变化，重新渲染图表');
      initChart(); // 数据变化时重新初始化图表
    }
  },
  { deep: true } // 深度监听对象的变化
);




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
</script>

<style scoped>
.echarts-container {
  width: 100%;
  height: 300px;

}
</style>