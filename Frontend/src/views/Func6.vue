<template>
  <div id="app">
    <el-container>
      <el-main>
        <PageMainContent />
      </el-main>
    </el-container>
  </div>
</template>

<script>

import PageMainContent from './Func6_page/PageMainContent.vue';

export default {
  components: {
    PageMainContent
  }
};

</script>

<style scoped>
.func6-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  height: 100vh;
}

.el-aside {
  background-color: #f5f7fa;
}

.el-main {
  padding: 20px;
}
</style>