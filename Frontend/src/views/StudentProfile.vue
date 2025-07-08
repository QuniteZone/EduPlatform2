<template>
  <div ref="content" class="content" />  
</template>

<script>
import idis from 'uniplore-idis-js-api'
export default {
  name: 'StudentAnalysis',
  data() {
    return {

    }
  },
  mounted() {
    this.va = new idis.VA(this.$refs.content, 'http://demo.uniplore.cn:30887/#/dataScreen/release?shareId=cd240235b47444fda2468402139777df', {}) 
    const targetIframe = document.querySelector('iframe.uniplore-idis-embbed-iframe');
    Object.assign(targetIframe.style, {
      width: '100%',
      height: '100%',
    });
  },
  methods: {
    // 可以添加交互方法
  }
}
</script>

<style scoped>
  html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}

.content {
  width: 100%;
  height: 90vh;
}

</style>