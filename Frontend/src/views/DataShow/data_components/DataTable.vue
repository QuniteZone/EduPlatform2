<template>
  <div class="data-table">
    <table>
      <thead>
        <tr>
          <th>排名</th>
          <th>名称</th>
          <th>数量</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in data" :key="index">
          <td>{{ item.ranking }}</td>
          <td>{{ item.unitName || item.supplierName }}</td>
          <td>{{ item.quantity }}</td>
        </tr>
      </tbody>
    </table>
  </div>
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
.data-table table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.data-table th {
  background-color: #e9f7fd;
  font-weight: bold;
}
</style>