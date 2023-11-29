# -- coding: utf-8 --
# @Time : 2023/11/24 10:19
# @Author : 马劲松
# @Email : mjs1263153117@163.com
# @File : BayesianOptimization.py
# @Software: PyCharm
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from bayes_opt import BayesianOptimization

from sklearn.datasets import make_classification
x, y = make_classification(n_samples=1000, n_features=5, n_classes=2)

def RF_evaluate(n_estimators, min_samples_split, max_features, max_depth):
    val = cross_val_score(
            RandomForestClassifier(n_estimators=int(n_estimators),
                       min_samples_split=int(min_samples_split),
                       max_features=min(max_features, 0.999),
                       max_depth=int(max_depth),
                       random_state=2,
                       n_jobs=-1),
            x, y, scoring='f1', cv=5
        ).mean()

    return val

# 确定取值空间
pbounds = {'n_estimators': (50, 250),  # 表示取值范围为10至250
               'min_samples_split': (2, 10),
               'max_features': (3, 5),
               'max_depth': (5, 12)}

RF_bo = BayesianOptimization(
        f=RF_evaluate,   # 目标函数
        pbounds=pbounds,  # 取值空间
        verbose=2,  # verbose = 2 时打印全部，verbose = 1 时打印运行中发现的最大值，verbose = 0 将什么都不打印
        random_state=1,
)

RF_bo.maximize(init_points=5,   # 随机搜索的步数
                   n_iter=10,   # 执行贝叶斯优化迭代次数
)

print(RF_bo.max)
res = RF_bo.max
params_max = res['params']


def RandomForest(train_x, train_y, n_estimators, min_samples_split, max_features, max_depth):
    # n_estimators：森林中树的数量,随机森林中树的数量默认100个树，精度递增显著，但并不是越多越好，加上verbose=True，显示进程使用信息
    # n_jobs  整数 可选（默认=1） 适合和预测并行运行的作业数，如果为-1，则将作业数设置为核心数
    forest_model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth,
                                          min_samples_split=min_samples_split,
                                          random_state=0, n_jobs=-1)
    x_train, x_test, y_train, y_test = train_test_split(train_x, train_y, test_size=0.3)

    forest_model.fit(x_train, y_train)

    joblib.dump(forest_model, 'rf.jobl')  # 存储

    y_pred = forest_model.predict(x_test)
    # 模型评估
    # 混淆矩阵
    print(confusion_matrix(y_test, y_pred))
    print("准确率: %.3f" % accuracy_score(y_test, y_pred))

    precision = precision_score(
        y_test, y_pred, average='macro')
    print('precision Score: %.2f%%' % (precision * 100.0))

    recall = recall_score(y_test, y_pred, average='macro')
    print('Recall Score: %.2f%%' % (recall * 100.0))
