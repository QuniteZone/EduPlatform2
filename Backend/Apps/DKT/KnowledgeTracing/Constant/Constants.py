Dpath = '../../KTDataset'

datasets = {
    'DKT_DATA' : 'DKT_DATA'
}

# question number of each dataset
numbers = {
    'DKT_DATA' : 534
}

DATASET = datasets['DKT_DATA']
NUM_OF_QUESTIONS = numbers['DKT_DATA']

# 新增：是否为“多知识点”设置
MULTI_TAG = True  # ← 设置为 True 以启用多知识点处理逻辑

# the max step of RNN model
MAX_STEP = 50
BATCH_SIZE = 64
LR = 0.002
EPOCH = 50
#input dimension
INPUT = NUM_OF_QUESTIONS * 2
# embedding dimension
EMBED = NUM_OF_QUESTIONS
# hidden layer dimension
HIDDEN = 200
# nums of hidden layers
LAYERS = 1
# output dimension
OUTPUT = NUM_OF_QUESTIONS
