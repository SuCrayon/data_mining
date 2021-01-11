#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: Crayon
@Date: 2021/1/11 0:34
@Last Modified by: Crayon
@Last Modified time: 2021/1/11 0:34
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

BASE_PATH = os.path.dirname(__file__) or '.'
# 带读取的数据的文件列表
FILE_PATH = f'{BASE_PATH}/data/merged.csv'


def draw_scatter(x, y):
    """
    绘制散点图
    :param x: 作为x轴的数据数组
    :param y: 作为y轴的数据数组
    """
    plt.figure()
    plt.title('C1 and Constitution')
    plt.scatter(x, y)
    plt.xlabel('C1')
    plt.ylabel('Constitution')
    plt.grid(True)  # 显示网格线
    plt.show()


def draw_histogram(x):
    """
    绘制C1的成绩直方图
    :param x: type: numpy.array C1成绩的数组
    """
    group = np.array([i for i in range(0, 100 + 1, 5)])
    plt.figure()
    plt.title('C1 histogram')
    plt.hist(x, group, histtype='bar', rwidth=1.2)
    plt.xlabel('C1 grade')
    plt.ylabel('number of students')
    plt.grid(True)  # 显示网格线
    plt.show()


def cal_mfAndsf(data):
    """
    求均值与标准差
    :param data: type: numpy.array 输入成绩列
    :return: mf: type: number 均值
    :return: sf: type: number 标准差
    """
    mf = 0
    for v in data:
        mf += v
    mf = mf / len(data)

    sf = 0
    for v in data:
        sf += (v - mf) ** 2
    sf = (sf / len(data)) ** 0.5
    return mf, sf


def get_zScoreMat(data):
    """
    成绩矩阵zscore归一化
    :param data: type: numpy.array 学生的成绩矩阵
    :return: zScore_mat type: numpy.array zscore归一化后的矩阵
    """
    zScore_mat = data.copy()
    for c in range(data.shape[1]):
        mf, sf = cal_mfAndsf(data[:, c])
        for r, v in enumerate(data[:, c]):
            zScore_mat[r, c] = (v - mf) / sf

    return zScore_mat


def get_correlationMat(data):
    # 102x102相关矩阵
    length = len(data)
    correlationMat = np.zeros([length, length])
    # i行 0~102
    for i in range(length):
        # j列 i~102
        for j in range(i, length):
            # 原矩阵i行
            mat_i = data[i]
            # 原矩阵j行
            mat_j = data[j]
            # 计算均值与标准差
            mi, si = cal_mfAndsf(data[i])
            mj, sj = cal_mfAndsf(data[j])
            # i,j点乘
            dot_ij = 0
            for idx in range(len(mat_i)):
                # 对应为相乘在相加
                dot_ij += (mat_i[idx] * mat_j[idx])
            cov_ij = (dot_ij / len(mat_i)) - mi * mj
            value_ij = cov_ij / (si * sj)
            # i行j列的值为原矩阵i行和j行的相关系数
            correlationMat[i, j] = value_ij
            # 对称
            correlationMat[j, i] = value_ij
    # print(correlationMat)
    return correlationMat


def find_topThree(data, ID_array):
    topThreeMat = np.zeros([len(data), 3], dtype=np.int64)
    for idx, row in enumerate(data):
        # 从小到大排序返回索引
        indexs = list(np.argsort(row))
        # 去掉本身
        indexs.remove(idx)

        for j in range(3):
            topThreeMat[idx][j] = ID_array[indexs[-(j + 1)]]

    # print(topThreeMat)
    return topThreeMat


def main():
    data = pd.read_csv(FILE_PATH, sep=",")
    draw_scatter(np.array(data['C1']), np.array(data['Constitution']))
    draw_histogram(np.array(data['C1']))
    # 切片取成绩列
    zScore_mat = get_zScoreMat(np.array(data)[:, 5:])
    correlationMat = get_correlationMat(np.array(data)[:, 5:])
    # 绘制矩阵
    sns.heatmap(correlationMat, cmap='Blues')
    plt.show()

    # 找最近的三个样本
    result = find_topThree(correlationMat, data['ID'])
    # 保存为txt文件
    np.savetxt(f'{BASE_PATH}/data/result.txt', result, fmt='%d', delimiter='\t')


if __name__ == "__main__":
    main()
