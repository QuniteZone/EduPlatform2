<template>
  <div class="dashboard">
     <div class="theme-card">
   <span class="theme">学生画像分析</span>
    <input class="input_id" v-model="studentId" placeholder="请输入学号" />
        <el-button
        class="click_id"
        @click="sendStudentInfo"
        :loading="loading"
        :icon="loading ? 'Loading' : ''"
    >
      {{ loading ? '生成中...' : '生成内容' }}
    </el-button>
  </div>
    <!-- 头部指标 -->
    <div class="header-cards">
      <!-- 左侧容器 -->

         <Stu_info
          :name="studentInfo.name"
          :s_class="studentInfo.class"
          :id="studentInfo.id"
           :major="studentInfo.major"
          :school="studentInfo.school"
         />


      <!-- 顶部容器 - 四个卡片 -->
      <div class="ly ly--fourcard" >
        <div class="header-right">
          <ChartCard
            :title="'总做题量'"
            :value="studentInfo.all_questions"
            :color="'#ff9900'"
          />
          <ChartCard
            :title="'学习课程数'"
            :value="studentInfo.all_lessons"
            :color="'#007bff'"
          />
          <ChartCard
            :title="'总学习小时数'"
            :value="studentInfo.all_time"
            :color="'#00bfff'"
          />
          <ChartCard
            :title="'做题正确率'"
            :value="studentInfo.right"
            :color="'#28a745'"
          />
          </div>

      </div>

        <!-- 顶部右侧容器 活跃与学生风格 -->
      <div class="header-three">

            <stu_face
                :styles=studentInfo.styles
               />
         <Suggest
                :goals=studentInfo.goals
               />


      </div>

    </div>

    <!-- 中间部分 -->
    <div class="middle-section">
      <div class="left-column">
        <div class="ly ly--stdstate" >
        <h3>近期学习动态</h3>
        <DataTable
            :data="studentInfo.info" />
        </div>
      </div>

      <div class="center-column">

        <div class="ly ly--test" >
          <h3>掌握程度最高的知识点</h3>
        <EChartsComponent
          :chartType="'g_radar'"
          :data="{

           indicators: [
                { text:`${studentInfo.top_points_list[0]}`, max: 1 },
                { text:`${studentInfo.top_points_list[1]}`, max: 1 },
                { text:`${studentInfo.top_points_list[2]}`, max: 1 },
                { text:`${studentInfo.top_points_list[3]}`, max: 1 },
                { text:`${studentInfo.top_points_list[4]}`, max: 1 },
                { text:`${studentInfo.top_points_list[5]}`, max: 1 },
              ],
           seriesData: [
              {
                value:studentInfo.top_scores_list,
                symbol: 'circle',  // 自定义标记为圆形
                areaStyle: { color: 'rgba(153,204,70,0.3)' }
              }
             ]
          }"
        />
        </div>
      </div>

      <div class="right-column">
         <div class="ly" >
          <h3>掌握程度最低的知识点</h3>
        <EChartsComponent
          :chartType="'b_radar'"
          :data="{
           indicators: [
                { text:`${studentInfo.bottom_points_list[0]}`, max: 1 },
                { text:`${studentInfo.bottom_points_list[1]}`, max: 1 },
                { text:`${studentInfo.bottom_points_list[2]}`, max: 1 },
                { text:`${studentInfo.bottom_points_list[3]}`, max: 1 },
                { text:`${studentInfo.bottom_points_list[4]}`, max: 1 },
                { text:`${studentInfo.bottom_points_list[5]}`, max: 1 },
              ],
           seriesData: [
              {
                value:studentInfo.bottom_scores_list,
                symbol: 'circle',  // 自定义标记为圆形
                areaStyle: { color: 'rgba(153,204,70,0.3)' }
              }
             ]
          }"
        />

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import EChartsComponent from '@/views/student_analyze/EChartsComponent.vue';
import ChartCard from '@/views/student_analyze/ChartCard.vue';
import DataTable from '@/views/student_analyze/DataTable.vue';
import { ref} from 'vue';
import Suggest from "@/views/student_analyze/Suggest.vue";
import Stu_info from "@/views/student_analyze/stu_info.vue";
import axios from "axios";
import Stu_face from "@/views/student_analyze/stu_face.vue";



const studentInfo = ref({
  //基本信息展示
  name: '',
  class: '',
  id:'',
  major: '',
  school: '',
  //四个小卡片  四位数
  all_questions: '', //总做题量
  all_lessons: '', //已学习课程数量
  all_time: '', //总学习时长
  right : "",//正确率

  //知识点掌握程度最好
   "top_points_list": ['标签1','标签2','标签3','标签4','标签5','标签6'],
   "top_scores_list": [],

  //知识点掌握程度最差
   "bottom_points_list": ['标签1','标签2','标签3','标签4','标签5','标签6'],
   "bottom_scores_list":[],

//近期信息动态
  info : '',
  //学习建议
  goals : [
  '无'
],
  styles:['无']
});

//<!-- 前端将学号发送给后端，并且从后端接受数据继续变量赋值 -->
//*************************************
//*******************************
const studentId = ref(''); // 学生学号
const loading = ref(false) // 控制加载状态
const sendStudentInfo = async () => {
  loading.value = true; // 开始加载
  try {
     const response = await axios.post('/api/user/Tags', {
      student_id: studentId.value,
    });
// 模拟后端返回的数据
    console.log("****************************************************************");
    //用于接受数据 改为response.data.stu_data
    const stu_data = response.data.data.stu_data;
    console.log(response.data.data)
    // console.log(response.data.stu_data.all_lessons);
    //
    // console.log(response.data.stu_data.name);

    console.log("****************************************************************");
    //下面对数据进行赋值
    studentInfo.value={
      name: stu_data.name,
      id: stu_data.id,
      class: stu_data.class,
      major: stu_data.major,
      school: stu_data.school,

      all_questions: stu_data.all_questions,
      all_lessons: stu_data.all_lessons,
      all_time: stu_data.all_time,
      right: stu_data.right,

      top_points_list: stu_data.top_points_list,
      top_scores_list: stu_data.top_scores_list,

      bottom_points_list: stu_data.bottom_points_list,
      bottom_scores_list: stu_data.bottom_scores_list,


      info: stu_data.info,

      goals: stu_data.goals,
      styles: stu_data.styles,

    }

    console.log('发送成功:', response.data);
    alert('信息发送成功！');
  } catch (error) {
    alert('发送失败');
    console.error('请求失败:', error);
  } finally {
    loading.value = false; // 结束加载
  }
};


</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  background-color:  #f7f9fc; /* 淡蓝色背景，可根据需求调整色值 */
  height: 100%; /* 占满视口高度 */
}
.header-cards,
.middle-section {
  height: 50%; /* 上下两部分各占50% */

}
.ly {
  background-color: #ffffff;
  border-radius: 30px; /* 圆角边框，数值越大圆角越明显 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); /* 立体感阴影 */
  padding: 20px; /* 内部边距，根据内容调整 */
  transition: all 0.3s ease; /* 鼠标悬停动画过渡效果 */
  border: 1px solid #8ec8e1; /* 浅灰色边框 */


}
 /* 第一层大容器 */
.header-cards {
  display: grid;
  grid-template-columns:1fr 1fr 3fr;  /* 3列 */
  gap: 10px;
  width: 100%;

}

/* 四个小卡片大容器 */
.ly--fourcard {
  padding: 10px;
}
.header-right {
  display: grid;
  grid-template-columns: 1fr 1fr;  /* 右侧再次使用Grid布局，平均分成两列 */
  grid-template-rows: 1fr 1fr;     /* 两行 */
  gap: 10px;
  height: 100%;
}

/* 做题与风格大容器 */
.header-three{
  display: grid;
  grid-template-columns: 2fr 2fr;  /* 右侧再次使用Grid布局，平均分成两列 */
  gap: 10px;
  height: 100%;
}

/* 第二层  */
.middle-section {
  display: grid;
  grid-template-columns: 5fr 3fr 3fr;
  gap: 20px;
  color:  #f7f9fc;
}

.left-column,
.center-column,
.right-column {
  background-color: #f7f9fc;
  height: 100%;

}

.ly{
  padding: 25px 30px;
  border-radius: 20px;
  background-color: #fff;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0e0e0;
  position: relative;
  overflow: hidden;
}



.ly h3 {
  color: #333;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #121010;
}

.ly {
  height: 340px; /* 增加高度以适应图表 */
}

.ly .echarts-container {
  width: 100%;
  height: 300px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  background-color: #fafafa; /* 图表背景色 */
}


h3 {
  margin-top: -10px; /* 例如设置顶部间距为 15 像素 */
  margin-bottom: 10px;
  color: #333;
}

::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.5); /* 半透明滑块 */
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #e2e8f0, #cbd5e1);
}

/* 对顶部主题容器框进行美化 */
.theme-card {
  display: flex;
  justify-content: center;
  padding: 30px 40px;
  background: linear-gradient(135deg, #e6f7ff 0%, #c2e9fb 100%);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(44, 92, 152, 0.1);
  position: relative;
  overflow: hidden;

  /* 装饰性元素 */
  &::before {
    content: '';
    position: absolute;
    top: -50px;
    right: -50px;
    width: 100px;
    height: 100px;
    background: rgba(100, 149, 237, 0.1);
    border-radius: 50%;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -30px;
    left: -30px;
    width: 60px;
    height: 60px;
    background: rgba(162, 228, 156, 0.1);
    border-radius: 50%;
  }
}
/* 对顶部输入框进行美化 */
.input_id {
  width: 200px;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;

}

.input_id:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.input_id::placeholder {
  color: #909399;
}

.click_id {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 40px;
  margin-left: 10px;
  background-color: #409eff;
  border: 1px solid #409eff;
  border-radius: 4px;
  font-size: 14px;
  color: #fff;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
}

.click_id:hover {
  background-color: #66b1ff;
}

.click_id:active {
  transform: translateY(1px);
}

/* 对主题进行美化*/
.theme {
  display: inline-flex;
  align-items: center;
  font-size: 26px;
  font-weight: 600;
  color: #2c5c98;

  /* 左侧图标 */
  &::before {
    content: '📊';
    margin-right: 10px;
    font-size: 28px;
    transform: translateY(-2px);
    transition: transform 0.3s ease;
  }

  /* 悬停效果：图标旋转 */
  &:hover::before {
    transform: translateY(-2px) rotate(15deg);
  }

  /* 文字动效 */
  letter-spacing: 0.5px;
  transition: all 0.3s ease;

  &:hover {
    letter-spacing: 1px;
  }

}
</style>