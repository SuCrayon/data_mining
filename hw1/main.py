#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: Crayon
@Date: 2021/1/9 10:37
@Last Modified by: Crayon
@Last Modified time: 2021/1/9 10:37
"""
import pandas as pd
import numpy as np
from numpy import nan

FILE_PATH = [
    'data/data01.xlsx',
    'data/data02.txt'
]


def changeIDFormat(data):
    baseNum = 202000
    data['ID'] = data['ID'].map(lambda x: x + baseNum)


def changeGenderFormat(data):
    gender_map = {
        'male': 'boy',
        'female': 'girl',
        'girl': 'girl',
        'boy': 'boy'
    }
    # 性别列的值映射到boy和girl
    data['Gender'] = data['Gender'].map(gender_map)


def changeHeightFormat(data):
    indexs = data[data['Height'] > 5].index
    data.loc[indexs, 'Height'] /= 100


def removeCnRows(data):
    """
    该函数用来删除成绩列有异常的行
    :param data: type: dataframe 待处理的数据列表
    """
    # 1到5为100分制成绩 超过100分的行就是异常
    for i in range(1, 6):
        data = data.drop(data[data[f'C{i}'] > 100].index)
    # 6到9为10分制成绩，超过10分的行就是异常
    for i in range(6, 10):
        data = data.drop(data[data[f'C{i}'] > 10].index)


def checkData(xlsx, txt):
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
    # 改变xlsx中ID格式
    changeIDFormat(xlsx)
    # 改变txt中gender格式
    changeGenderFormat(txt)
    changeGenderFormat(xlsx)
    # 检查数据
    dataTable = checkData(xlsx, txt)
    # 改变合并后数据的Height的格式 以m为单位
    changeHeightFormat(dataTable)
    removeCnRows(dataTable)
    return dataTable


def get_data():
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


def main():
    # 获取数据
    data = get_data()
    # 保存数据为csv文件 不保留索引值
    data.to_csv('data/merged.csv', index=0)


if __name__ == "__main__":
    main()
