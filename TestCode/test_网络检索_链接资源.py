import requests
import json

# url = "https://google.serper.dev/search"
#
# payload = json.dumps({
#   "q": "机器学习资源",
#   "gl": "cn",
#   "hl": "zh-cn",
#   "num": 20
# })
# headers = {
#   'X-API-KEY': '54933bde17093ecd3db9ef1d25f16be7c3a5a6d2',
#   'Content-Type': 'application/json'
# }
#
# response = requests.request("POST", url, headers=headers, data=payload)
#
# json_content=response.json()

json_content={'searchParameters': {'q': '机器学习资源', 'gl': 'cn', 'hl': 'zh-cn', 'type': 'search', 'num': 20, 'engine': 'google'}, 'organic': [{'title': '机器学习资源Machine learning Resources - GitHub', 'link': 'https://github.com/allmachinelearning/MachineLearning', 'snippet': '致力于分享最新最全面的机器学习资料，欢迎你成为贡献者! 快速开始学习：. 周志华的《机器学习》作为通读教材，不用深入，从宏观上了解机器学习. 《机器学习》西瓜书公式 ...', 'position': 1}, {'title': 'howie6879/mlhub123: 机器学习&深度学习网站资源汇总 ... - GitHub', 'link': 'https://github.com/howie6879/mlhub123', 'snippet': '资源收集 · awesome-machine-learning-cn: 机器学习资源大全中文版，包括机器学习领域的框架、库以及软件 · awesome-public-datasets: 各领域公开数据集下载 · Coursera-ML- ...', 'position': 2}, {'title': '机器学习资源列表(AwesomeList)汇总 - 知乎专栏', 'link': 'https://zhuanlan.zhihu.com/p/449876793', 'snippet': '用一个多月时间整理了一份几乎涉及机器学习/深度学习一切主题(学习范式/任务/应用/模型/道德/交叉学科/数据集/框架/教程) 的分类资源列表汇总。由于知乎对多级列表的支持 ...', 'position': 3}, {'title': 'Machine Learning - 机器学习资源 - Google for Developers', 'link': 'https://developers.google.com/machine-learning/managing-ml-projects/resources?hl=zh-cn', 'snippet': '机器学习开发需要使用各种不断发展的工具和框架。随着硬件技术的不断进步以及管道编排技术的不断发展，用于处理复杂数据类型的新机器学习工具不断涌现。', 'position': 4}, {'title': '史上最全机器学习资源整理 - 知乎', 'link': 'https://www.zhihu.com/column/p/26876504', 'snippet': '机器学习资源浩如烟海，本文对机器学习资源做了相关整理，希望大家能够根据自己的细分研究领域，着重关注某些学习资源。可能某几个网页链接打不开，那说明需要“科学”上网。', 'position': 5}, {'title': 'TensorFlow 机器学习资源', 'link': 'https://www.tensorflow.org/resources/learn-ml?hl=zh-cn', 'snippet': '我们将学习流程划分为四个知识领域，每个领域均提供了机器学习的基础知识部分。为帮助您顺利完成学习之旅，我们列出了一些图书、视频和在线课程，不仅有助于您提升能力，还可以 ...', 'position': 6}, {'title': '【推荐】一份超全的机器学习&深度学习网站资源清单(105个AI站点)', 'link': 'https://blog.csdn.net/IT_xiao_bai/article/details/84197510', 'snippet': '社区交流 · AIQ (http://www.6aiq.com ): 机器学习大数据技术社区 · DataTau (https://www.datatau.com): 人工智能领域的Hacker News · MathOverflow ( ...', 'date': '2018年11月18日', 'position': 7}, {'title': '机器学习-学习资源- Gelthin - 博客园', 'link': 'https://www.cnblogs.com/Gelthin2017/p/14076240.html', 'snippet': '书籍： · 机器学习（西瓜书） · 统计学习方法（蓝宝书） · 模式识别 · Pattern Recognition and Machine Learning (PRML) · Elements of Statistical Learning ...', 'date': '2020年12月2日', 'position': 8}, {'title': '【入门必备】史上最全的深度学习资源汇总 - 阿里云天池', 'link': 'https://tianchi.aliyun.com/forum/post/77398', 'snippet': '今天小编有幸为大家介绍一些我自认为不错的深度学习资源，希望帮助热爱深度学习的小伙伴能够走的更远。 教程：. Topal的深度学习教程，从感知机到深度神经网络： ...', 'position': 9}, {'title': 'Coursera: Machine Learning - CS自学指南', 'link': 'https://csdiy.wiki/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/ML/', 'snippet': 'Coursera: Machine Learning. 课程简介. 所属大学：Stanford; 先修要求：AI 入门+ 熟练使用Python; 编程语言：Python; 课程难度： ; 预计学时：100 小时.', 'position': 10}, {'title': '【资源整理】AI学习网站推荐', 'link': 'https://forum.cambricon.com/index.php?m=content&c=index&a=show&catid=55&id=3031', 'snippet': '一、机器学习. 林轩田和李宏毅的机器学习 · 二、深度学习. 吴恩达老师课程- 人人AI - 知学堂(zhihu.com)； · 三、论文相关 · 四、NLP领域 · 五、视觉（CV相关） · 六、数学 ...', 'position': 11}, {'title': '深度学习技术资源| NVIDIA - 英伟达', 'link': 'https://www.nvidia.cn/training/resources/', 'snippet': '初涉AI、加速计算、数据科学或网络领域，还是希望进行深入的研究？获取从初级到高级的丰富技术资源，探寻应对源源不断的艰巨挑战的灵感和方案。 深度学习; 加速计算 ...', 'position': 12}, {'title': 'AI 和机器学习资源| Cloud Architecture Center', 'link': 'https://cloud.google.com/architecture/ai-ml?hl=zh-cn', 'snippet': '管理和扩缩在托管式Kubernetes 上运行的Windows 应用的网络. 参考架构 · 部署架构 · 使用Java 的动态Web 应用 · 使用JavaScript 的动态Web 应用 ...', 'position': 13}, {'title': '《动手学深度学习》 — 动手学深度学习2.0.0 documentation', 'link': 'https://zh.d2l.ai/', 'snippet': '【免费资源】 课件、作业、教学视频等资源可参考伯克利“深度学习导论” 课程 ... 机器学习中的关键组件 · 1.3. 各种机器学习问题 · 1.4. 起源 · 1.5. 深度学习的发展 · 1.6 ...', 'position': 14}, {'title': '人工智能平台PAI_机器学习建模训练部署', 'link': 'https://www.aliyun.com/product/bigdata/learn', 'snippet': '阿里云人工智能平台PAI 涵盖交互式建模、可视化建模、分布式训练到模型在线部署全流程；快速搭建人工智能推荐系统；深度学习模型训练速度提升数十倍；减少50%GPU成本.', 'position': 15}, {'title': '人工智能- AI 和机器学习资源 - AWS', 'link': 'https://aws.amazon.com/cn/ai/resources/', 'snippet': '在机器学习和人工智能方面，AWS 提供全球最丰富的人工智能学习资源，最广泛、最深入的服务和端到端支持，同时致力于不懈创新。了解AWS 如何帮助您以最快速、最简单且最有效的 ...', 'position': 16}, {'title': 'github机器学习和深度学习资源汇总原创 - CSDN博客', 'link': 'https://blog.csdn.net/pilotmickey/article/details/119735062', 'snippet': '本篇为专栏2022年6月刊，对6月发布的日报内容进行了整合分类，将350+学习资源整理成了这本电子月刊，包括工具库、模型框架、项目代码、算法实现、学习路线图 ...', 'date': '2021年8月16日', 'position': 17}, {'title': 'B站最强学习资源汇总（数据科学，机器学习，Python） - 豫南- 博客园', 'link': 'https://www.cnblogs.com/lqshang/p/17281644.html', 'snippet': '这门课程将学会理解业界构建深度神经网络应用最有效的做法； 能够高效地使用神经网络通用的技巧，包括初始化、L2和dropout正则化、Batch归一化、梯度检验；', 'date': '2023年4月2日', 'position': 18}, {'title': '想学习人工智能、大语言模型？这份学习路线与免费学习资源最值得 ...', 'link': 'https://www.digitaloceans.cn/technology/355/', 'snippet': '这篇文章试图创建一份免费的课程路径，希望对大家学习有帮助。（注意：有大量教程、书籍、论文和资源都是英文的，请配合AI 翻译工具来阅读吧。） 自上 ...', 'date': '2024年4月30日', 'position': 19}, {'title': 'GitHub万星的中文机器学习资源：路线图、视频、学习建议全在这', 'link': 'https://www.qbitai.com/2019/04/1909.html', 'snippet': '这套名叫AI Learning的GitHub资源，汇集了30多名贡献者的集体智慧，把学习机器学习的路线图、视频、电子书、学习建议等中文资料全部都整理好了。', 'date': '2019年4月19日', 'position': 20}], 'relatedSearches': [{'query': '机器学习github'}, {'query': '机器学习学习路线'}, {'query': '机器学习pdf'}, {'query': '机器学习教程'}, {'query': '机器学习网站'}, {'query': '机器学习周志华pdf'}, {'query': '机器学习入门'}, {'query': '机器学习书籍'}], 'credits': 2}

# 整理资源信息
resources = json_content['organic']
sorted_resources = []

for resource in resources:
    title = resource.get('title')
    link = resource.get('link')
    snippet = resource.get('snippet')
    position = resource.get('position')

    # 整理成字典
    sorted_resources.append({
        'title': title,
        'link': link,
        'snippet': snippet,
        'position': position
    })

# 输出整理后的资源
for res in sorted_resources:
    print(f"位置: {res['position']}\n标题: {res['title']}\n链接: {res['link']}\n简介: {res['snippet']}\n")
