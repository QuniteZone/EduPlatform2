<template>
  <div class="data-table-container" style="max-height: 300px; overflow-y: auto;">
    <div class="data-table">
      <table>
        <thead>
          <tr>
            <th>日期</th>
            <th>时间</th>
            <th>课程名称</th>
            <th>课时名称</th>
            <th>分钟</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in data" :key="index">
            <td>{{ item.data }}</td>
            <td>{{ item.time }}</td>
            <td>{{ item.lesson }}</td>
            <td>{{ item.teach.length>10?item.teach.slice(0,10)+"...":item.teach }}</td>
            <td>{{ Math.floor(item.times )}}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- 分页组件 -->
  <Pagination
    :total="data.length"
    :page-size="pageSize"
    :current-page="currentPage"
    @page-change="handlePageChange"
  />
</template>

<script setup>
defineProps({
  data: {
    type: Array,
    required: true,
  },
});
</script>

<style scoped>
.data-table {
  height: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden; /* 确保内容不超出圆角边界 */
  transition: all 0.3s ease;
}

.data-table table {
  width: 100%;
  height: 300px;
  border-collapse: collapse;
  margin: 0;
  background-color: #fff;
}

.data-table th,
.data-table td {
  padding: 12px 18px;
  text-align: left;
  position: relative;
  transition: all 0.3s ease;
}

.data-table td {
  padding: 5px 15px;
}

/* 表头美化 */
.data-table th {
  color: white;
  background-color: #9abff6; /* 调整表头背景颜色 */
  font-weight: 600;

}

/* 表格行样式 */
.data-table tbody tr {
  border-bottom: 1px solid #e8eef9; /* 调整行的底部分隔线颜色 */
  background-color: white;
}

.data-table tbody tr:last-child {
  border-bottom: none; /* 最后一行不显示底边 */
}

/* 表格行悬停效果 */
.data-table tbody tr:hover {
  background-color: #f0f4ff; /* 调整悬停时的背景颜色 */
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(64, 153, 255, 0.1);
}

/* 隔行变色效果 */
.data-table tbody tr:nth-child(even) {
  background-color: #fafbfd; /* 调整偶数行的背景颜色 */
}

/* 数据单元格样式 */
.data-table td {
  color: #333;
  font-size: 14px;
  border-top: 1px solid #fafbfd; /* 添加轻微的顶部边框，增强行的分隔效果 */
}

/* 为滚动条添加样式 */
.data-table-container::-webkit-scrollbar {
  width: 6px;
}

.data-table-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.data-table-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.data-table-container::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

.data-table th:nth-child(1),
.data-table td:nth-child(1) {
  width: 15%; /* 日期列宽度 */
}
.data-table td:nth-child(1) {
  width: 18%; /* 日期列宽度 */
}
.data-table th:nth-child(2),
.data-table td:nth-child(2) {
  width: 10%; /* 时间列宽度 */
}

.data-table th:nth-child(3),
.data-table td:nth-child(3) {
  width: 20%; /* 课程名列宽度 */
}

.data-table th:nth-child(4),
.data-table td:nth-child(4) {
  width: 25%; /* 课时名列宽度（内容最长） */
}
.data-table td:nth-child(4) {
  width: 30%; /* 课时名列宽度（内容最长） */
}


.data-table th:nth-child(5),
.data-table td:nth-child(5) {
  width: 15%; /* 分钟列宽度 */
}
</style>