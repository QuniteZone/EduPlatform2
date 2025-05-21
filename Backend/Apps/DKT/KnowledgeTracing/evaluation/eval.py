import sys

import numpy as np

sys.path.append('../')
import tqdm
import torch
import torch.nn as nn
from sklearn import metrics
from torch.autograd import Variable
from DKT.KnowledgeTracing.Constant import Constants as C

def performance(ground_truth, prediction):
    fpr, tpr, thresholds = metrics.roc_curve(ground_truth.detach().numpy(), prediction.detach().numpy())
    auc = metrics.auc(fpr, tpr)

    f1 = metrics.f1_score(ground_truth.detach().numpy(), torch.round(prediction).detach().numpy())
    recall = metrics.recall_score(ground_truth.detach().numpy(), torch.round(prediction).detach().numpy())
    precision = metrics.precision_score(ground_truth.detach().numpy(), torch.round(prediction).detach().numpy())

    print('auc:' + str(auc) + ' f1: ' + str(f1) + ' recall: ' + str(recall) + ' precision: ' + str(precision) + '\n')

class lossFunc(nn.Module):
    def __init__(self):
        super(lossFunc, self).__init__()

    def forward(self, pred, batch):
        loss = torch.tensor(0.0)
        for student in range(pred.shape[0]):
            # 多标签情况：对所有标签位置的加权平均计算 loss
            for t in range(C.MAX_STEP - 1):
                input_vector = pred[student][t]  # 预测的概率向量
                target_vector = batch[student][t + 1]

                q_indices = (target_vector[:C.NUM_OF_QUESTIONS] == 1).nonzero(as_tuple=True)[0]
                nq_indices = (target_vector[C.NUM_OF_QUESTIONS:] == 1).nonzero(as_tuple=True)[0]

                for idx in q_indices:
                    prob = input_vector[idx]
                    loss -= torch.log(prob + 1e-8)

                for idx in nq_indices:
                    prob = input_vector[idx]
                    loss -= torch.log(1 - prob + 1e-8)
        return loss


def train_epoch(model, trainLoader, optimizer, loss_func):
    for batch in tqdm.tqdm(trainLoader, desc='Training:    ', mininterval=2):
        pred = model(batch)
        loss = loss_func(pred, batch)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    return model, optimizer


def test_epoch(model, testLoader):
    gold_epoch = torch.Tensor([])
    pred_epoch = torch.Tensor([])

    for batch in tqdm.tqdm(testLoader, desc='Testing:    ', mininterval=2):
        pred = model(batch)
        for student in range(pred.shape[0]):
            for t in range(C.MAX_STEP - 1):
                input_vector = pred[student][t]  # 模型输出
                target_vector = batch[student][t + 1]

                # 正例
                pos_indices = (target_vector[:C.NUM_OF_QUESTIONS] == 1).nonzero(as_tuple=True)[0]
                # 负例
                neg_indices = (target_vector[C.NUM_OF_QUESTIONS:] == 1).nonzero(as_tuple=True)[0]

                for idx in pos_indices:
                    pred_epoch = torch.cat([pred_epoch, input_vector[idx].unsqueeze(0)])
                    gold_epoch = torch.cat([gold_epoch, torch.tensor([1.0])])

                for idx in neg_indices:
                    pred_epoch = torch.cat([pred_epoch, input_vector[idx].unsqueeze(0)])
                    gold_epoch = torch.cat([gold_epoch, torch.tensor([0.0])])
    return pred_epoch, gold_epoch



def train(trainLoaders, model, optimizer, lossFunc):
    for i in range(len(trainLoaders)):
        model, optimizer = train_epoch(model, trainLoaders[i], optimizer, lossFunc)
    return model, optimizer

def test(testLoaders, model):
    ground_truth = torch.Tensor([])
    prediction = torch.Tensor([])
    for i in range(len(testLoaders)):
        pred_epoch, gold_epoch = test_epoch(model, testLoaders[i])
        prediction = torch.cat([prediction, pred_epoch])
        ground_truth = torch.cat([ground_truth, gold_epoch])
    performance(ground_truth, prediction)



def get_final_step_predictions(model, testLoaders):
    final_preds = []  # 每个元素是 [NUM_OF_QUESTIONS]，代表该学生对每个知识点的掌握程度

    model.eval()
    with torch.no_grad():
        for testLoader in testLoaders:
            for batch in testLoader:
                preds = model(batch)  # [batch_size, MAX_STEP, NUM_OF_QUESTIONS]
                batch = batch.numpy()  # 转为 numpy 处理 easier
                for i in range(batch.shape[0]):
                    student_seq = batch[i]  # shape: [MAX_STEP, 2*NUM_OF_QUESTIONS]
                    # 找到最后一个不是全0的一步（即不是 padding）
                    last_valid_step = -1
                    for t in reversed(range(C.MAX_STEP)):
                        # 判断是否是有效 step
                        if not np.all(student_seq[t] == 0):
                            last_valid_step = t
                            break
                    if last_valid_step == -1:
                        continue  # skip 全是 padding 的
                    final_preds.append(preds[i, last_valid_step].detach().numpy())  # shape: [NUM_OF_QUESTIONS]
    return final_preds
