import numpy as np
from torch.utils.data.dataset import Dataset
from DKT.KnowledgeTracing.Constant import Constants as C
import torch

class DKTDataSet(Dataset):
    def __init__(self, ques, ans):
        self.ques = ques
        self.ans = ans

    def __len__(self):
        return len(self.ques)

    def __getitem__(self, index):
        questions = self.ques[index]
        answers = self.ans[index]
        onehot = self.onehot(questions, answers)
        return torch.FloatTensor(onehot.tolist())

    def onehot(self, questions, answers):
        result = np.zeros(shape=[C.MAX_STEP, 2 * C.NUM_OF_QUESTIONS])
        for i in range(C.MAX_STEP):
            q_list = questions[i] if isinstance(questions[i], list) else [questions[i]]
            for q in q_list:
                if q == -1:
                    continue
                if answers[i] > 0:
                    result[i][q] = 1
                elif answers[i] == 0:
                    result[i][q + C.NUM_OF_QUESTIONS] = 1
        return result
