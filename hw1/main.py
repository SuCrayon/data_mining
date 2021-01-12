#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: cmy_ennio
@Date: 2021/1/9 10:37
@Last Modified by: cmy_ennio
@Last Modified time: 2021/1/9 10:37
"""
import pandas as pd
import numpy as np
import os

BASE_PATH = os.path.dirname(__file__) or '.'
# 待读取的数据的文件列表
FILE_PATH = [
    f'{BASE_PATH}/data/data01.xlsx',
    f'{BASE_PATH}/data/data02.txt'
]


def changeIDFormat(data):
    """
    该函数用来改变学生id格式，统一加上202000的前缀
    :param data: type: dataframe 待处理的数据
    """
    baseNum = 202000
    data['ID'] = data['ID'].map(lambda x: x + baseNum)


def changeGenderFormat(data):
    """
    该函数将改变性别的格式，统一映射成boy和girl的格式
    :param data: type: dataframe 待处理的数据
    """
    gender_map = {
        'male': 'boy',
        'female': 'girl',
        'girl': 'girl',
        'boy': 'boy'
    }
    # 性别列的值映射到boy和girl
    data['Gender'] = data['Gender'].map(gender_map)


def changeHeightFormat(data):
    """
    该函数用来改变身高数据的格式，统一以m为单位，数值较小
    :param data: type: dataframe 待处理的数据
    """
    indexs = data[data['Height'] > 5].index
    data.loc[indexs, 'Height'] /= 100


def removeCnRows(data):
    """
    该函数用来删除成绩列有异常的行
    :param data: type: dataframe 待处理的数据
    """
    # 1到5为100分制成绩 超过100分的行就是异常
    for i in range(1, 6):
        data = data.drop(data[data[f'C{i}'] > 100].index)
    # 6到9为10分制成绩，超过10分的行就是异常
    for i in range(6, 10):
        data = data.drop(data[data[f'C{i}'] > 10].index)


def changeConstitutionFormat(data):
    """
    该函数将体测的非数值型数据映射为数值型数据
    :param data: type: dataframe 待处理的数据
    """
    constitution_map = {
        'bad': 25,
        'general': 50,
        'good': 75,
        'excellent': 100
    }
    data['Constitution'] = data['Constitution'].map(constitution_map)


def checkData(xlsx, txt):
    """
    查验数据，以txt为基准数据，对于其中含有空值的行取xlsx中找到空缺的数据并补上，如果处理后还是存在空值，则删去这一行
    从xlsx的不含有空值的数据中查找txt中没有的学生的信息，补充到txt数据中，并重新按学号排序，重置索引值
    :param xlsx: type: dataframe xlsx表中的数据
    :param txt: type: dataframe txt文件中的数据
    :return: txt type: dataframe 处理后的txt数据
    """
    # 获取列名
    cols = txt.columns
    # 包含空值的行
    hasNanRows = txt[txt.isnull().T.any()]
    # 遍历行
    for idx, row in hasNanRows.iterrows():
        ID = row[cols[0]]
        # 遍历每列
        for col in cols[1:]:
            # 判断是否值缺失
            if pd.isnull(row[col]):
                # xlsx的参照表中有对应的第一行
                referRows = xlsx[xlsx['ID'] == ID]
                if len(referRows) > 0:
                    referRow = referRows.iloc[0]
                    if not pd.isnull(referRow[col]):
                        # 修改源数据
                        txt.loc[idx, col] = referRow[col]
    # 去除仍然存在空值的行
    txt = txt.drop(txt[txt.isnull().T.any()].index)

    needID = []
    baseNum = 202000
    for row in txt.iloc:
        differ = row['ID'] - baseNum
        if differ > 1:
            for i in range(baseNum + 1, baseNum + differ):
                needID.append(i)
        baseNum = row['ID']

    needRows = xlsx[xlsx['ID'].isin(needID)]
    insertRows = needRows.drop(needRows[needRows.isnull().T.any()].index)

    txt = txt.append(insertRows)
    # 去重
    txt = txt.drop_duplicates(['ID', 'Name'])
    txt.sort_values(by='ID', inplace=True, ascending=True, ignore_index=True)
    return txt


def merge_data(xlsx, txt):
    """
    对数据进行清晰并合并
    :param xlsx: type: dataframe xlsx表中的数据
    :param txt: type: dataframe txt文件中的数据
    :return: dataTable type: dataframe 合并好的数据
    """
    # 改变xlsx中ID格式
    changeIDFormat(xlsx)
    # 改变txt中gender格式
    changeGenderFormat(txt)
    changeGenderFormat(xlsx)
    # 检查数据
    dataTable = checkData(xlsx, txt)
    # 改变合并后数据的Height的格式 以m为单位
    changeHeightFormat(dataTable)
    # 去除成绩有异常的行
    removeCnRows(dataTable)
    # 将体测数据映射到数值型
    changeConstitutionFormat(dataTable)
    return dataTable


def get_data():
    """
    用来获取源数据，xlsx表中的数据用来模拟数据库中查出的数据
    :return: dataTable type: dataframe 返回由源数据经过清洗合并后的数据
    """
    # 读取excel表中的数据
    data_xlsx = pd.read_excel(FILE_PATH[0])
    # 删掉C10列的数据，因为都为空
    data_xlsx = data_xlsx.drop(columns=['C10'])
    # print(data_xlsx)
    # 读取txt中的数据
    data_txt = pd.read_csv(FILE_PATH[1], sep=",")
    # 删掉C10列的数据，因为都为空
    data_txt = data_txt.drop(columns=['C10'])
    # print(data_txt)
    dataTable = merge_data(data_xlsx, data_txt)
    return dataTable


def task1(data, decimal=2):
    """
    计算学生中家乡在Beijing的所有课程的平均成绩
    :param data: type: dataframe
    :param decimal: int 保留的小数点位数
    :return: avg 均值
    """
    if not isinstance(decimal, int):
        raise TypeError(f'Invalid type(need int but get {type(decimal)})')

    total = 0
    n = 0
    for row in data.iloc:
        # 家乡在Beijing的同学
        if row['City'] == 'Beijing':
            n += 1
            # 5列（包含）之后的是学生成绩
            for col in row[5:]:
                total += col
    # 求均值，n是学生数，10是成绩数目
    avg = round(total / (n * 10), decimal)
    return avg


def task2(data):
    """
    统计家乡在广州，课程1在80分以上，且课程9在9分以上的男同学的数量
    :param data: type: dataframe
    :return: n 统计数
    """
    n = 0
    for row in data.iloc:
        # 家乡在Guangzhou 课程1成绩在80分以上 课程9在9分以上
        if row['City'] == 'Guangzhou' and row['C1'] > 80 and row['C9'] > 9 and row['Gender'] == 'boy':
            n += 1

    return n


def task3(data):
    """
    比较广州和上海两地女生的平均体能测试成绩，哪个地区的更强些
    :param data: type: dataframe
    :return: type: str 返回地区名
    """
    gz_total = 0
    sh_total = 0
    gz_n = 0
    sh_n = 0

    for row in data.iloc:
        # 广州
        if row['City'] == 'Guangzhou':
            gz_total += row[-1]
            gz_n += 1
        # 上海
        if row['City'] == 'Shanghai':
            sh_total += row[-1]
            sh_n += 1
        else:
            pass

    gz_avg = 0
    sh_avg = 0
    gz_avg = gz_total / gz_n
    sh_avg = sh_total / sh_n

    if gz_avg > sh_avg:
        return '广州'
    elif gz_avg < sh_avg:
        return '上海'
    elif gz_avg == sh_avg:
        return '一样'
    else:
        pass


def get_cov(data):
    """
    计算得到协方差矩阵
    :param data: type: numpy.array 数组类型，带计算的矩阵
    :return: cov_mat type: numpy.array 返回协方差矩阵
    """
    # 计算mean 和 std
    total = 0
    for v in data:
        total += v
    mean = total / len(data)
    total = 0
    for v in data:
        total += ((v - mean) ** 2)
    std = (total / (len(data) - 1)) ** 0.5

    # 协方差矩阵
    cov_mat = []
    for i in range(len(data)):
        cov_mat.append((data[i] - mean) / std)

    return np.array(cov_mat)


def task4(data, decimal=2):
    """
    计算九门课的成绩分别与体能成绩计算相关性
    :param data: type: dataframe
    :param decimal: 保留几位小数
    """
    if not isinstance(decimal, int):
        raise TypeError(f'Invalid type(need int but get {type(decimal)})')

    # 体测成绩
    constitution_cov = get_cov(np.array(data['Constitution']))
    # print(constitution_cov)
    for i in range(0, 9):
        correlation = 0
        ci_cov = get_cov(np.array(data[f'C{i + 1}']))
        # 点乘计算，对应位计算并相加
        for idx, v in enumerate(constitution_cov):
            correlation += ci_cov[idx] * v
        print(f'C{i + 1}与Constitution相关性：{round(correlation, decimal)}')


def main():
    # 获取数据
    data = get_data()
    # 保存数据为csv文件 不保留索引值
    data.to_csv(f'{BASE_PATH}/data/merged.csv', index=0)
    print(f'学生中家乡在Beijing的所有课程的平均成绩：【{task1(data)}】')
    print(f'学生中家乡在广州，课程1在80分以上，且课程9在9分以上的男同学的数量：【{task2(data)}】')
    print(f'比较广州和上海两地女生的平均体能测试成绩，哪个地区的更强些：【{task3(data)}】')
    task4(data)


if __name__ == "__main__":
    main()
