import sys
import os
import torch
from DKT.KnowledgeTracing.model.RNNModel import DKT
from DKT.KnowledgeTracing.data.dataloader import getTrainLoader, getTestLoader, getLoader
from DKT.KnowledgeTracing.Constant import Constants as C
import torch.optim as optim
from DKT.KnowledgeTracing.evaluation import eval


def dkt_train():
    print('Dataset: ' + C.DATASET + ', Learning Rate: ' + str(C.LR) + '\n')

    model = DKT(C.INPUT, C.HIDDEN, C.LAYERS, C.OUTPUT)
    optimizer_adam = optim.Adam(model.parameters(), lr=C.LR)
    optimizer_adgd = optim.Adagrad(model.parameters(), lr=C.LR)

    loss_func = eval.lossFunc()

    trainLoaders, testLoaders = getLoader(C.DATASET)

    for epoch in range(C.EPOCH):
        print('epoch: ' + str(epoch))
        model, optimizer = eval.train(trainLoaders, model, optimizer_adgd, loss_func)
        eval.test(testLoaders, model)

    final_knowledge_states = eval.get_final_step_predictions(model, testLoaders)

    # 示例：打印前3个学生的掌握程度（每个都是 NUM_OF_QUESTIONS 的概率分布）
    for i in range(1):
        print(f"Student {i + 1} mastery:", final_knowledge_states[i])

    # 保存模型参数
    torch.save(model.state_dict(), 'dkt_model_final.pth')
    print("模型参数已保存为 dkt_model_final.pth")


def predict_with_trained_model(model_path):
    # 1. 初始化模型结构
    model = DKT(C.INPUT, C.HIDDEN, C.LAYERS, C.OUTPUT)

    # 2. 加载训练好的参数
    model.load_state_dict(torch.load(model_path))
    model.eval()  # 切换到评估模式

    # 3. 准备测试数据加载器
    _,testLoaders = getLoader(C.DATASET)

    # # 4. 运行测试并获得结果
    # eval.test(testLoaders, model)

    # 5. 获取最终的知识状态预测
    final_knowledge_states = eval.get_final_step_predictions(model, testLoaders)

    # 打印前3个学生的最终掌握度
    for i in range(min(3, len(final_knowledge_states))):
        print(f"Student {i + 1} mastery:", final_knowledge_states[i])

    return final_knowledge_states


if __name__ == "__main__":
    # dkt_train()
    model_path = 'dkt_model_final.pth'
    predict_with_trained_model(model_path)

