import numpy as np
import itertools
import tqdm

class DataReader():
    def __init__(self, path, maxstep, numofques):
        self.path = path
        self.maxstep = maxstep
        self.numofques = numofques

    def getTrainData(self):
        trainqus = []
        trainans = []
        with open(self.path, 'r') as train:
            lines = train.readlines()
            for i in range(0, len(lines), 3):
                length = int(lines[i].strip().strip(','))
                ques_raw = lines[i + 1].strip().strip(',').split(',')
                ans_raw = lines[i + 2].strip().strip(',').split(',')
                ques = []
                for q in ques_raw:
                    if '|' in q:
                        ques.append([int(k) for k in q.split('|')])
                    else:
                        ques.append([int(q)])
                ans = [int(a) for a in ans_raw]

                # 补齐至 maxstep
                mod = self.maxstep - length
                ques += [[-1] for _ in range(mod)]
                ans += [-1] * mod

                trainqus.append(ques)
                trainans.append(ans)
        return trainqus, trainans

    def getTestData(self):
        testqus = []
        testans = []
        with open(self.path, 'r') as test:
            lines = test.readlines()
            for i in range(0, len(lines), 3):
                length = int(lines[i].strip().strip(','))
                ques_raw = lines[i + 1].strip().strip(',').split(',')
                ans_raw = lines[i + 2].strip().strip(',').split(',')
                ques = []
                for q in ques_raw:
                    if '|' in q:
                        ques.append([int(k) for k in q.split('|')])
                    else:
                        ques.append([int(q)])
                ans = [int(a) for a in ans_raw]

                # 补齐至 maxstep
                mod = self.maxstep - length
                ques += [[-1] for _ in range(mod)]
                ans += [-1] * mod

                testqus.append(ques)
                testans.append(ans)
        return testqus, testans


