<template>
  <div class="grading-container">
    <!-- Header -->
    <div class="grading-header">
      <div class="header-left">
        <span class="header-text">主观题</span>
        <span class="header-text">当前学生：{{studentId}}</span>
      </div>
       <el-button type="primary" @click="studentNext" class="submit-button finish">下一位</el-button>
    </div>

    <!-- 题目和学生答案区域 -->
    <div class="question-answer-container">
      <!-- 题目内容 -->
      <div class="question-container">

        <div class="question-content">
          <p>{{question}}</p>
        </div>
      </div>

      <!-- 学生答案 -->
      <div class="student-answer-container">
        <h3 class="answer-title">学生答案</h3>
        <div class="answer-content">
          <p>{{studentAnswer}}</p>
        </div>
      </div>
    </div>

    <!-- 参考答案 -->
    <div class="grading-content">
      <el-row :gutter="15">
          <!-- 教师评语 -->
        <el-col :span="8">
          <el-card class="teacher-comment">
            <div class="section-title">参考答案</div>
               <label>请输入参考答案</label>
              <el-input
                type="textarea"
                :rows="5"
                placeholder="请输入(可选)"
                v-model="comment"
                readonly
              ></el-input>
          </el-card>
        </el-col>


        <!-- AI 打分和评语 -->
        <el-col :span="8">
          <el-card class="ai-section">
            <div class="section-title">AI 评分</div>
            <div class="score-input">
              <label>AI 给出的分数</label>
              <el-input v-model="aiScore" placeholder="AI 打分" disabled></el-input>
            </div>
               <el-button type="primary" @click="handleAiReview" :loading="aiReviewing" class="submit-button">AI 评阅</el-button>
            <div class="comment-section">
              <label>AI 评语</label>
              <el-input
                type="textarea"
                :rows="5"
                placeholder="AI 评语将在此显示"
                v-model="aiComment"
                readonly
              ></el-input>
            </div>
          </el-card>

        </el-col>

        <!-- 教师打分 -->
        <el-col :span="8">
          <el-card class="teacher-scoring">
            <div class="section-title">教师评分</div>
            <div class="score-input">
              <label>教师打分：</label>
              <el-input
                  :rows="1"
                  placeholder="请输入教师打分"
                  type="number"
                  v-model.number="teacherScore"
              ></el-input>
            </div>
            <label>教师评语：</label>
            <div class="comment-input">
              <el-input
                type="textarea"
                :rows="7"
                placeholder="请输入教师评语"
                v-model="teacherComment"
              ></el-input>
            </div>
          </el-card>
        </el-col>


      </el-row>
    </div>

    <!-- 按钮区域 -->
    <div class="action-buttons">
      <el-button type="primary" @click="questionNext" class="submit-button finish">下一题</el-button>
      <el-button type="primary" @click="handleSubmit" class="submit-button finish">批改完成</el-button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      comment: '', // 参考答案
      studentId: '123456', // 学生ID
      aiScore: '', // AI 打分
      aiComment: '', // AI 评语
      teacherScore: '', // 教师打分
      teacherComment: '无评语', // 教师评语
      aiReviewing: false, // AI 评阅状态
      question: '请简述数据结构中栈和队列的区别，并举例说明它们的应用场景。', // 题目内容
      studentAnswer: '栈是一种后进先出（LIFO）的数据结构，队列是一种先进先出（FIFO）的数据结构。栈的应用场景包括函数调用和表达式求值，队列的应用场景包括任务调度和消息传递。', // 学生答案
    };
  },

  methods: {
    async handleAiReview() {
      this.aiReviewing = true;

      try {
        // 定义 POST 请求的 URL 和参数
        const url = 'api/plan/question_judgment';
        const formData = new FormData();
        formData.append('question', this.question); // 题目
        formData.append('stu_ans', this.studentAnswer); // 学生答案

        // 使用 axios 发送 POST 请求
        const response = await axios.post(url, formData, {
          question: this.question,
          stu_ans: this.studentAnswer,
          headers: {
        'Content-Type': 'application/json', // 设置为 JSON 格式
      },
        });
        //后端返回的json格式
        //{
        // content: '{"ai_score": 85, "ai_comment": "abc"}',
        // status: 1
        // }
        console.log('后端返回的数据:', response);
        // 解析后端返回的数据
        const { content, status } = response.data;
        if (status === 1 && content) {
          try {
            const parsedContent = JSON.parse(content) ; // 解析 JSON 字符串
            this.aiScore = parsedContent.ai_score; // 设置 AI 分数
            this.aiComment = parsedContent.ai_comment; // 设置 AI 评语
            //aiScore 的数据
            console.log('后端返回的aiscore:', this.aiScore);
            //
            this.teacherScore=this.aiScore;
            this.teacherComment=this.aiComment;

          } catch (error) {
            throw new Error('无法解析后端返回的 content 数据');
          }
        } else {
          throw new Error('后端返回的状态不正确或缺少 content 数据');
        }
      } catch (error) {
        this.$message.error(`AI 评阅失败：${error.message}`);
      } finally {
        this.aiReviewing = false;
      }
    },





    handleSubmit() {
      //这里面还要增加把分数和评语提交的代码
      if (!this.teacherScore || !this.teacherComment) {

           this.$message.error({ message: '请完成评分和评语后再提交', duration: 500 });
        return;

      }
      this.$message.success({ message: '学生成绩已提交', duration: 500 });
    },

  studentNext() {
      //这里面还要增加学生更换

      this.$message.success({ message: '下一位学生', duration: 500 });
    },

    questionNext() {
      //这里面还要增加题目更换
      this.$message.success({ message: '下一题', duration: 500 });
    },

  },
};
</script>

<style scoped>
.grading-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* Header 样式 */
.grading-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
}

.grading-header:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
  transform: translateY(-2px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-text {
  font-size: 16px;
  color: #606266;
}

/* 题目和学生答案容器样式 */
.question-answer-container {
  margin-bottom: 20px;
}

.question-container,
.student-answer-container {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
  padding: 20px;
  margin-bottom: 20px;
}

.question-container:hover,
.student-answer-container:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
  transform: translateY(-2px);
}

.question-container {
  background: linear-gradient(135deg, #e0f7fa 0%, #80deea 100%);
  color: #01579b;
}

.student-answer-container {
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
  color: #333;
}

.question-title,
.answer-title {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 20px;
  font-weight: bold;
}

.question-content,
.answer-content {
  line-height: 1.8;
  font-weight: 500;
}

/* 评分和评语区域样式 */
.grading-content {
  margin-bottom: 20px;
  background-color: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
}

.grading-content:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
  transform: translateY(-2px);
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #303133;
}

.score-input {
  margin-bottom: 15px;
}

.ai-actions {
  margin-bottom: 15px;
}

.comment-section,
.comment-input {
  margin-top: 15px;
}

.score-buttons {
  margin-top: 15px;
}

.el-button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.special-scores {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.active {
  background-color: #409eff !important;
  color: white !important;
}

/* 按钮区域样式 */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 20px;
  padding: 15px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.action-buttons:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
  transform: translateY(-2px);
}

.submit-button {
  width: 180px;
  height: 40px;
  font-size: 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.next-button {
  width: 180px;
  height: 40px;
  font-size: 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.next-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 卡片样式 */
.ai-section,
.teacher-scoring,
.teacher-comment {
  height: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.ai-section:hover,
.teacher-scoring:hover,
.teacher-comment:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
  transform: translateY(-2px);
}

.el-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}
</style>