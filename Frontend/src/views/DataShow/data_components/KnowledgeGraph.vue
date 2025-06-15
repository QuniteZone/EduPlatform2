<template>
  <div ref="chart" class="knowledge-graph"></div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "KnowledgeGraph",
  props: {
    // 接收从后端返回的 JSON 文件路径
    graphDataUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      graphData: null, // 存储加载的JSON数据
      simulation: null, // 力模拟实例
      svg: null, // SVG 容器引用
      linkGroup: null, // 边容器
      nodeGroup: null, // 节点容器
      linkLabelGroup: null, // 边标签容器
      link: null, // 边元素集合
      node: null, // 节点元素集合
      linkLabel: null // 边标签元素集合
    };
  },
  watch: {
    // 当 graphDataUrl 发生变化时重新加载数据
    graphDataUrl: {
      immediate: true,
      handler(newUrl) {
        if (newUrl) {
          this.loadJson(newUrl);
        }
      }
    }
  },
  methods: {
    // 根据传入的 URL 加载 JSON 数据
    async loadJson(url) {
      try {
        const response = await fetch(url); // 使用传入的 URL 加载数据
        this.graphData = await response.json();
        this.$nextTick(() => {
          this.drawGraph(); // 数据加载完成后绘制图表
        });
      } catch (error) {
        console.error("Failed to load JSON:", error);
      }
    },

    // 绘制或更新知识图谱
    drawGraph() {
      const container = this.$refs.chart;
      const { width, height } = container.getBoundingClientRect();

      // 清理旧图表状态
      if (this.simulation) {
        this.simulation.stop();
        this.simulation = null;
      }

      if (this.svg) {
        this.svg.remove();
      }

      // 创建新的 SVG 容器
      this.svg = d3
        .select(this.$refs.chart)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      const group = this.svg.append("g");

      // 创建箭头标记
      const markerDefs = this.svg.append("defs");
      markerDefs
        .selectAll("marker")
        .data(["先修", "后修"])
        .enter()
        .append("marker")
        .attr("id", d => `arrow-${d}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", d => (d === "先修" ? "#ff7f0e" : "#1f77b4"));

      // 创建力导向图布局
      this.simulation = d3
        .forceSimulation(this.graphData.nodes)
        .force(
          "link",
          d3.forceLink(this.graphData.links).id(d => d.id).distance(150)
        )
        .force("charge", d3.forceManyBody().strength(-200))
        .force("center", d3.forceCenter(width / 2, height / 2));

      // 初始化边
      this.linkGroup = group.append("g");
      this.link = this.linkGroup
        .selectAll(".link")
        .data(this.graphData.links)
        .enter()
        .append("line")
        .attr("class", "link")
        .attr("stroke", d => (d.label === "先修" ? "#ff7f0e" : "#1f77b4"))
        .attr("stroke-width", 2)
        .attr("stroke-opacity", 0.8)
        .attr("marker-end", d => `url(#arrow-${d.label})`);

      // 初始化边标签
      this.linkLabelGroup = group.append("g");
      this.linkLabel = this.linkLabelGroup
        .selectAll(".link-label")
        .data(this.graphData.links)
        .enter()
        .append("text")
        .attr("class", "link-label")
        .text(d => d.label)
        .attr("font-size", "10px")
        .attr("fill", d => (d.label === "先修" ? "#ff7f0e" : "#1f77b4"));

      // 初始化节点
      this.nodeGroup = group.append("g");
      this.node = this.nodeGroup
        .selectAll(".node")
        .data(this.graphData.nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(
          d3
            .drag()
            .on("start", event => this.dragStarted(event))
            .on("drag", event => this.dragged(event))
            .on("end", event => this.dragEnded(event))
        );

      // 添加节点圆圈
      this.node
        .append("circle")
        .attr("r", 10)
        .attr("fill", "#69b3a2");

      // 添加节点标签
      this.node
        .append("text")
        .text(d => d.label)
        .attr("dy", -15)
        .attr("text-anchor", "middle")
        .style("font-size", "12px");

      // tick 更新函数
      const tickHandler = () => {
        this.link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);

        this.node.attr("transform", d => `translate(${d.x},${d.y})`);

        this.linkLabel
          .attr("x", d => (d.source.x + d.target.x) / 2)
          .attr("y", d => (d.source.y + d.target.y) / 2);
      };

      this.simulation.on("tick", tickHandler);
    },

    // 拖拽开始事件
    dragStarted(event) {
      if (!event.active) {
        this.simulation.alphaTarget(0.3).restart();
      }
      event.fx = event.x;
      event.fy = event.y;
    },

    // 拖拽中
    dragged(event) {
      event.fx = event.x;
      event.fy = event.y;
    },

    // 拖拽结束
    dragEnded(event) {
      if (!event.active) {
        this.simulation.alphaTarget(0);
      }
      event.fx = null;
      event.fy = null;
    }
  }
};
</script>



<style scoped>
.knowledge-graph {
  width: 100%;
  height: 100%;
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