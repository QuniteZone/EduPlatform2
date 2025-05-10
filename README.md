# EduPlatform（编写中）
EduPlatform 是一个基于 Python 和 Vue.js 的在线教育平台，旨在为教师和学生提供便捷、高效的教学工具。平台集成了多种功能，包括教案生成、班会稿生成、主观题判题、个性化学习推荐等，以帮助提高教师的教学效率和学生的学习效果。

<div style="display: flex; justify-content: space-between;">
    <img src="TestCode/git演示-PPT功能-GIF.gif" alt="Image 1" />
</div>

---

## 一、项目概述
**EduPlatform** 是一个全功能的在线教育平台，专为教育工作者与学习者设计。其主要目标是通过智能化的工具带来方便的教学体验。平台的关键功能包括：

- 教案生成：教师可以快速生成标准化教学计划，节省备课时间。
- 班会稿生成：教师可根据某一主题自动生成班会方案，为管理班级活动提供支持。
- 主观题判题：一键自动评分与反馈，帮助教师高效管理学生的主观题答卷。
- 个性化学习推荐：依据学生的学习习惯与成绩提供个性化的学习资源和建议。
- 知识跟踪：能智能分析学生知识点掌握情况，实时明晰学生学习效果。

通过这些功能，EduPlatform 旨在为教师和学生提供全面、灵活的在线学习和教学支持。


---

## 二、安装说明
在安装 **EduPlatform** 之前，请确保您的系统满足以下要求：

- Python 3.x
- Node.js
- MySQL 数据库

### 安装步骤：

1. **克隆项目仓库：**

   ```bash
   git clone https://github.com/yourusername/EduPlatform.git
   ```

2. **设置后端：**

   - 进入后端目录并安装依赖：

   ```bash
   cd EduPlatform/backend
   pip install -r requirements.txt
   ```

3. **配置数据库：**

   - 在 MySQL 中创建一个数据库，例如 **edu_platform_db**。
   - 修改 `config.py` 中的数据库连接配置，填入你的 MySQL 数据库信息。

4. **启动后端服务器：**

   ```bash
   python app.py
   ```

5. **设置前端：**

   - 进入前端目录并安装依赖：

   ```bash
   cd EduPlatform/frontend
   npm install
   ```

6. **启动前端服务器：**

   ```bash
   npm run serve
   ```
---

## 三、使用方法
如何使用 EduPlatform：

1. **注册与登录**

   - 用户首次使用需进行注册，填写您的信息，注册完成后可登录使用平台。

2. **功能模块**

   - 在平台首页，用户可以看到所有功能模块的入口，依次点击相应模块以开始使用。

   - **教案生成**：填写教学计划要求后生成教案。
   - **班会策划**：设定班会主题后可以自动生成班会方案。
   - **判题功能**：上传学生的主观题答卷后进行自动评分。
   - **个性化推荐**：系统会依据学生数据推荐学习资源。
---

## 四、项目结构
下面是项目的基本结构：

```
EduPlatform/
├── backend/
│   ├── app.py                 # 后端主应用
│   ├── config.py              # 后端配置文件
│   ├── models/                # 后端数据模型
│   ├── routes/                # 后端路由处理
│   └── templates/             # 后端相关模板文件
└── frontend/
    ├── src/
    │   ├── components/        # Vue.js 组件
    │   ├── views/             # Vue.js 视图
    │   ├── App.vue            # 入口组件
    │   └── main.js            # 入口文件
    └── public/                # 公共资源
```
---

## 五、技术选型
- **后端**：
  - **框架**：使用 Python Flask 框架，提供灵活的后端解决方案。
  
- **数据库**：
  - **选择**：MySQL 数据库，支持数据的稳定存储与检索。
  
- **前端**：
  - **框架**：Vue.js 框架，具备良好的组件化能力与响应式特性。
  
- **UI 组件库**：
  - **选择**：Element Plus，提供高质量的 UI 组件支持，增强用户体验。

- **Markdown 解析**：
  - **工具**：使用 `marked.js` 进行 Markdown 解析，方便内容的编辑与展示。
  
- **富文本编辑器**：
  - **工具**：WangEditor，为用户提供简单易用的文本编辑解决方案。
---

## 六、配置说明
EduPlatform 的主要配置文件包括：

- **app.py**：后端主应用配置，包括应用路由与应用程序初始化。
- **config.py**：后端全局配置文件，包括数据库连接配置及其他应用参数。
- **package.json**：前端依赖包配置文件，管理前端使用的 npm 包及脚本。
- **jsconfig.json**：前端 JavaScript 配置文件，提供类型识别与 IntelliSense 支持。
- **babel.config.js**：前端 Babel 的配置文件，适配 ES6+ 环境。
- **tsconfig.json**：前端 TypeScript 配置文件，提供类型检查与编译设置。
