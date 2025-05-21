import sys
sys.path.append('../')
import os
import torch
import torch.utils.data as Data
from Apps.DKT.KnowledgeTracing.Constant import Constants as C
from Apps.DKT.KnowledgeTracing.data.readdata import DataReader
from Apps.DKT.KnowledgeTracing.data.DKTDataSet import DKTDataSet
import pandas as pd

def getTrainLoader(train_data_path):
    handle = DataReader(train_data_path ,C.MAX_STEP, C.NUM_OF_QUESTIONS)
    trainques, trainans = handle.getTrainData()
    dtrain = DKTDataSet(trainques, trainans)
    trainLoader = Data.DataLoader(dtrain, batch_size=C.BATCH_SIZE, shuffle=True)
    return trainLoader

def getTestLoader(test_data_path):
    handle = DataReader(test_data_path, C.MAX_STEP, C.NUM_OF_QUESTIONS)
    testques, testans = handle.getTestData()
    dtest = DKTDataSet(testques, testans)
    testLoader = Data.DataLoader(dtest, batch_size=C.BATCH_SIZE, shuffle=False)
    return testLoader

def getLoader(dataset):
    trainLoaders = []
    testLoaders = []
    if dataset == 'DKT_DATA':
        train_path=os.path.join('static','DKT_DATA','train.txt')
        test_path=os.path.join('static','DKT_DATA','test.txt')
        # 初试的调用方式，需修改
        # trainLoader = getTrainLoader(C.Dpath + '/DKT_DATA/train.txt')
        # trainLoaders.append(trainLoader)
        # testLoader = getTestLoader(C.Dpath + '/DKT_DATA/test.txt')
        # testLoaders.append(testLoader)
        trainLoader = getTrainLoader(train_path)
        trainLoaders.append(trainLoader)
        testLoader = getTestLoader(test_path)
        testLoaders.append(testLoader)
    return trainLoaders, testLoaders


import pandas as pd

import pandas as pd

def clean_data():
    # 读取数据
    df = pd.read_csv(r'C:\code\Deep-Knowledge-Tracing-DKT-Pytorch-master\DKT\KTDataset\DKT_data.csv')

    # 过滤掉 review_result 为 0 的行
    df = df[df['review_result'] != 0]

    # 映射是否正确
    df['is_correct'] = df['review_result'].map({1: 1, 3: 0})

    # 分组
    grouped = df.groupby('user_id')

    # 打开输出文件
    output_path = r'C:\code\Deep-Knowledge-Tracing-DKT-Pytorch-master\DKT\KTDataset\cleaned_output.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        for user_id, group in grouped:
            count = len(group)
            knowledges = ','.join(group['Konwledge'].astype(str))
            correctness = ','.join(group['is_correct'].astype(str))

            # 写入三行：数量、知识点串、正误串
            f.write(f"{count},\n")
            f.write(knowledges + ",\n")
            f.write(correctness + ",\n")  # 空一行分隔不同用户

    print(f"处理完成，输出保存至：{output_path}")


def split_cleaned_output():
    input_path = r'C:\code\Deep-Knowledge-Tracing-DKT-Pytorch-master\DKT\KTDataset\cleaned_output.txt'
    train_path = r'/DKT/KTDataset/DKT_DATA/train.txt'
    test_path = r'/DKT/KTDataset/DKT_DATA/test.txt'

    # 读取所有非空行
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() != '']

    # 保证行数是3的倍数
    assert len(lines) % 3 == 0, "文件格式错误，行数不是3的倍数"

    # 每三个连续的行为一个样本
    samples = [lines[i:i+3] for i in range(0, len(lines), 3)]

    # 打乱顺序并划分
    import random
    random.shuffle(samples)
    total = len(samples)
    test_size = int(total * 0.2)

    test_samples = samples[:test_size]
    train_samples = samples[test_size:]

    # 写入训练集
    with open(train_path, 'w', encoding='utf-8') as f:
        for sample in train_samples:
            f.write('\n'.join(sample) + '\n')

    # 写入测试集
    with open(test_path, 'w', encoding='utf-8') as f:
        for sample in test_samples:
            f.write('\n'.join(sample) + '\n')

    print(f"划分完成，训练集：{len(train_samples)}，测试集：{len(test_samples)}")


import pandas as pd

def find_max_knowledge_id():
    # 读取原始数据
    df = pd.read_csv(r'C:\code\Deep-Knowledge-Tracing-DKT-Pytorch-master\DKT\KTDataset\DKT_DATA\DKT_data.csv')

    # 拆分 Konwledge 字符串并提取所有知识点编号
    knowledge_ids = set()
    for item in df['Konwledge']:
        if pd.isna(item):
            continue
        parts = str(item).split('|')
        for p in parts:
            try:
                knowledge_ids.add(int(p))
            except ValueError:
                pass  # 忽略非整数的情况

    max_id = max(knowledge_ids) if knowledge_ids else None
    print(f"Konwledge 列中最大的知识点编号是：{max_id}")


def check_data_file(file_path):
    print(f"正在检查文件：{file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() != '']

    assert len(lines) % 3 == 0, "文件格式错误：非3行一组"

    has_error = False
    for i in range(0, len(lines), 3):
        count_line = lines[i]
        knowledge_line = lines[i + 1]
        correctness_line = lines[i + 2]

        try:
            expected_count = int(count_line.rstrip(','))
        except ValueError:
            print(f"❌ 第{i + 1}行 count 解析失败：'{count_line}'")
            has_error = True
            continue

        # 去除末尾的多余逗号，拆分为元素列表
        knowledge_list = [k for k in knowledge_line.strip(',').split(',') if k]
        correctness_list = [c for c in correctness_line.strip(',').split(',') if c]

        # 检查长度是否一致
        if len(knowledge_list) != expected_count or len(correctness_list) != expected_count:
            print(
                f"❌ 第 {i + 1}-{i + 3} 行数据不一致：count={expected_count}, 实际 Konwledge={len(knowledge_list)}, correctness={len(correctness_list)}")
            has_error = True

    if not has_error:
        print("✅ 文件检查通过，没有发现格式错误。")
    else:
        print("⚠️ 文件存在问题，请检查上方提示。")


# 执行检查
# check_data_file(r'C:\code\Deep-Knowledge-Tracing-DKT-Pytorch-master\DKT\KTDataset\DKT_DATA\test.txt')
# check_data_file(r'C:\code\Deep-Knowledge-Tracing-DKT-Pytorch-master\DKT\KTDataset\DKT_DATA\test.txt')
