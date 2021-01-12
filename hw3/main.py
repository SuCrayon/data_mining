#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: Crayon
@Date: 2021/1/11 15:37
@Last Modified by: Crayon
@Last Modified time: 2021/1/11 15:37
"""
import os
import random

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

BASE_PATH = os.path.dirname(__file__) or '.'
# 带读取的数据的文件列表
FILE_PATH = [
    f'{BASE_PATH}/data/z_score.txt',
    f'{BASE_PATH}/data/test.txt',
]


def separateByClass(x, y):
    """
    按照标签分离数据
    @param x: numpy.array 特征数据，每一行都是一个特征向量
    @param y: numpy.array 标签数据
    @return: list 返回分好类的特征数据，shape=(类别,该类特征像两个数,特征数)
    """
    ret = []
    data = np.column_stack((x, y))
    # 集合去重
    labels = list(set(y))
    # print(labels)
    # 按标签分开
    for label in labels:
        temp = data[data[:, -1] == label]
        ret.append(temp[:, :-1])
    return ret


def euclidean(x1, x2):
    """
    使用欧式距离计算距离
    @param x1: numpy.array 第一个特征向量
    @param x2: numpy.array 第二个特征向量
    """
    if len(x1) != len(x2):
        raise ValueError('向量维度不一致!')
    d = 0
    for i in range(len(x1)):
        d += ((x1[i] - x2[i]) ** 2)
    return d ** 0.5
    # return np.sqrt(np.sum(np.square(x1 - x2)))


def min_euclidean(x1, arr_x2):
    """
    x1与数组x2中最短的欧式距离
    @param x1: numpy.array 第一个特征向量
    @param arr_x2: [numpy.array] 一组特征向量
    @return 返回最短欧式距离，以及arr_x2中距离最短的点的索引
    """
    min_dist = euclidean(x1, arr_x2[0])
    index = 0
    for idx, x2 in enumerate(arr_x2):
        dist = euclidean(x1, x2)
        if dist < min_dist:
            min_dist = dist
            index = idx
    return min_dist, index


class KmeansCluster:
    def __init__(self, n_cluster=3, epochs=10):
        self.n_cluster = n_cluster
        self.epochs = epochs
        self.x = None
        # self.y = None

    def init_centroid(self):
        """
        初始化质心
        """
        while True:
            cents = np.zeros((self.n_cluster, self.x.shape[1]))
            for i in range(self.x.shape[1]):
                arr = self.x[:, i]
                for c in range(len(cents)):
                    # 随机生成i维度特征的值，一共四个特征，四维的点
                    cents[c][i] = random.uniform(np.min(arr), np.max(arr))

            label = []
            for pt in self.x:
                dist, index = min_euclidean(pt, cents)
                # 标记
                label.append(index)
            # print(len(set(label)))
            if len(set(label)) == self.n_cluster:
                break
        return cents

    def update_centroid(self, cents, labels):
        """
        更新质心
        @param cents: numpy.array 质心特征的数组
        @param labels: list 数据聚类后自标记标签数组
        """
        ret = separateByClass(self.x, np.array(labels))
        for i in range(len(cents)):
            cents[i] = np.mean(ret[i], axis=0)
        return cents

    def doCluster(self):
        # 随机生成质心
        cents = self.init_centroid()
        # 用来存储标签，即数据点被分到哪一簇
        ret_labels = []
        # 存储质心
        ret_cents = []
        # 循环迭代轮次
        for epoch in range(self.epochs):
            # print(f'第{epoch + 1}次迭代...')
            label = []
            # 计算每个点到三个质心的距离，并标记
            for pt in self.x:
                dist, index = min_euclidean(pt, cents)
                # 标记
                label.append(index)
            # 存储标记
            ret_labels.append(label)
            # 存储质心
            ret_cents.append(cents)
            # 更新质心，均值更新
            cents = self.update_centroid(cents, label)

        return ret_cents, ret_labels

    def fit(self, x_train):
        self.x = x_train
        cluster_y = self.doCluster()
        return cluster_y


def main():
    color = ['red', 'blue', 'green', 'yellow', 'purple']
    # 聚多少个类
    classNum = int(input('输入聚类类别数：'))
    # 读取归一化的成绩数据矩阵
    x = np.loadtxt(FILE_PATH[0], delimiter=',')
    cluster = KmeansCluster(n_cluster=classNum, epochs=20)
    ret_cents, ret_labels = cluster.fit(x)
    ret_cent = ret_cents[-1]
    ret_label = ret_labels[-1]

    plt.scatter(x[:, 0], x[:, 1], c=ret_label)
    plt.scatter(ret_cent[:, 0], ret_cent[:, 1], marker='+', c=np.arange(0, classNum),
                s=np.full((classNum,), 500))
    plt.show()

    # 聚多少个类
    classNum = int(input('输入聚类类别数：'))
    # 读取预先存到txt的实验数据
    fig = plt.figure()
    # 1行1列 1号子图
    ax = fig.add_subplot(1, 1, 1)
    test_x = np.loadtxt(FILE_PATH[1], delimiter=',')
    cluster = KmeansCluster(n_cluster=classNum, epochs=20)
    ret_cents, ret_labels = cluster.fit(test_x)
    ret_cent = ret_cents[-1]
    ret_label = ret_labels[-1]

    test_pt = (2, 6)
    distance = euclidean(test_pt, ret_cent[0])
    index = 0
    for idx, pt in enumerate(ret_cent[0:]):
        d = euclidean(test_pt, pt)
        if d < distance:
            index = idx
            distance = d
    print(f'点{test_pt}应分为第{index + 1}类\n距离：{distance}\n颜色归类：{color[index]}')
    plt.scatter(test_pt[0], test_pt[1], c=color[index], marker='*')

    # 绘制散点图
    for class_idx in range(classNum):
        max_distance = 0
        # 将同一类的点画出来
        for idx, v in enumerate(ret_label):
            if v == class_idx:
                plt.scatter(test_x[idx, 0], test_x[idx, 1], c=color[v])
                max_distance = max(euclidean(ret_cent[class_idx], test_x[idx]), max_distance)

        # 画出质心点
        plt.scatter(ret_cent[class_idx, 0], ret_cent[class_idx, 1], c=color[class_idx])

        r = max_distance

        # theta = np.arange(0, 2 * np.pi, 0.01)
        # x = ret_cent[class_idx, 0] + r * np.cos(theta)
        # y = ret_cent[class_idx, 1] + r * np.sin(theta)
        # plt.plot(x, y, color=color[class_idx])

        ax.add_patch(
            Circle(xy=(ret_cent[class_idx, 0],
                       ret_cent[class_idx, 1]),
                   radius=r,
                   alpha=0.1,
                   color=color[class_idx]))

    plt.axis('equal')
    plt.show()


if __name__ == "__main__":
    main()
