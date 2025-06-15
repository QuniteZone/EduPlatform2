<template>
  <div ref="chart" class="knowledge-graph"></div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "KnowledgeGraph",
  data() {
    return {
      graphData: null, // 存储加载的JSON数据
    };
  },
  async mounted() {
    await this.loadJson();
    this.$nextTick(() => {
      if (this.graphData) {
        this.drawGraph();
      }
    });
  },
  methods: {
    // 加载JSON数据
    async loadJson() {
      try {
        const response = await fetch("/All_shuzi_Xiaorong.json"); // 从public目录加载
        this.graphData = await response.json();
      } catch (error) {
        console.error("Failed to load JSON:", error);
      }
    },
    // 绘制知识图谱
    drawGraph() {
      // const width = window.innerWidth;
      // const height = window.innerHeight;
      const container = this.$refs.chart;
      const { width, height } = container.getBoundingClientRect();

      // 创建SVG容器
      const svg = d3
          .select(this.$refs.chart)
          .append("svg")
          .attr("width", width)
          .attr("height", height);

      const group = svg.append("g");

      // 力导向图布局
      const simulation = d3
          .forceSimulation(this.graphData.nodes)
          .force(
              "link",
              d3.forceLink(this.graphData.links).id((d) => d.id).distance(150)
          )
          .force("charge", d3.forceManyBody().strength(-200))
          .force("center", d3.forceCenter(width / 2, height / 2));

      // 定义箭头标记
      svg
          .append("defs")
          .selectAll("marker")
          .data(["先修", "后修"]) // 根据边的类型定义不同箭头
          .enter()
          .append("marker")
          .attr("id", (d) => `arrow-${d}`)
          .attr("viewBox", "0 -5 10 10")
          .attr("refX", 15) // 箭头位置
          .attr("refY", 0)
          .attr("markerWidth", 6)
          .attr("markerHeight", 6)
          .attr("orient", "auto")
          .append("path")
          .attr("d", "M0,-5L10,0L0,5")
          .attr("fill", (d) => (d === "先修" ? "#ff7f0e" : "#1f77b4")); // 不同类型的边用不同颜色

      // 绘制链接
      const link = group
          .append("g")
          .selectAll(".link")
          .data(this.graphData.links)
          .enter()
          .append("line")
          .attr("class", "link")
          .attr("stroke", (d) => (d.label === "先修" ? "#ff7f0e" : "#1f77b4")) // 设置边的颜色
          .attr("stroke-width", 2) // 增加边的宽度
          .attr("stroke-opacity", 0.8) // 设置边的透明度
          .attr("marker-end", (d) => `url(#arrow-${d.label})`); // 添加箭头

      // 添加链接标签
      const linkLabels = group
          .append("g")
          .selectAll(".link-label")
          .data(this.graphData.links)
          .enter()
          .append("text")
          .attr("class", "link-label")
          .text((d) => d.label)
          .attr("font-size", "10px")
          .attr("fill", (d) => (d.label === "先修" ? "#ff7f0e" : "#1f77b4")); // 链接标签颜色与边一致

      // 绘制节点
      const node = group
          .append("g")
          .selectAll(".node")
          .data(this.graphData.nodes)
          .enter()
          .append("g")
          .attr("class", "node")
          .call(
              d3
                  .drag()
                  .on("start", dragStarted)
                  .on("drag", dragged)
                  .on("end", dragEnded)
          );

      // 添加节点圆圈
      node
          .append("circle")
          .attr("r", 10)
          .attr("fill", "#69b3a2");

      // 添加节点标签
      node
          .append("text")
          .text((d) => d.label)
          .attr("dy", -15)
          .attr("text-anchor", "middle")
          .style("font-size", "12px");

      // 更新位置
      simulation.on("tick", () => {
        link
            .attr("x1", (d) => d.source.x)
            .attr("y1", (d) => d.source.y)
            .attr("x2", (d) => d.target.x)
            .attr("y2", (d) => d.target.y);

        node.attr("transform", (d) => `translate(${d.x},${d.y})`);

        linkLabels
            .attr("x", (d) => (d.source.x + d.target.x) / 2)
            .attr("y", (d) => (d.source.y + d.target.y) / 2);
      });

      // 拖拽事件
      function dragStarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }

      function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
      }

      function dragEnded(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }
    },
  },
};
</script>

<style scoped>
.knowledge-graph {
  width: 100vw;
  height: 100vh;
}

.link {
  stroke: #ccc;
  stroke-width: 2px;
  stroke-opacity: 0.8;
}

.link-label {
  font-size: 10px;
  fill: #555;
}

.node circle {
  fill: #69b3a2;
  stroke: #fff;
  stroke-width: 2px;
}

.node text {
  font-size: 12px;
  fill: #333;
}
</style>