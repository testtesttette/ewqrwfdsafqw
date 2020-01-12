"""
一些公共函数。
"""

import os
import csv
from dateutil.parser import parse
from dateutil.rrule import rrule, HOURLY


def generate_time_list(start_date: str, num_days: int):
    """
    生成一个逐小时的时间列表，供读写数据使用
    :param start_date: 格式为 2018-12-08 00:00, 默认从零点开始
    :param num_days: 列表包含的天数
    :return: 一个逐小时的时间列表
    """
    time_list = rrule(HOURLY, dtstart=parse(start_date), count=num_days * 24)
    format_time_list = [str(time)[:-3] for time in time_list]
    return format_time_list


def get_set_from_dir(*, dir_name: str):
    """
    读取目录下的所有csv文件名
    :param dir_name: 目录名字
    :return 返回的set
    """
    if dir_name == '':
        return set()
    ret_set = set()
    try:
        for file in os.listdir(dir_name):
            ret_set.add(file.split('.csv')[0])
    except OSError as e:
        print('Error: ', e)
    finally:
        return ret_set


def get_set_from_csv(*, csv_name: str, index: int):
    """
    从一个csv文件中读出需要的数据集合
    TODO: 如何传入格式
    :param csv_name: csv文件名字
    :param index: 数据所在的列
    :return 返回的set
    """
    if csv_name == '':
        return set()
    ret_set = set()
    try:
        with open(csv_name, encoding='gbk') as csvfile:
            it = iter(csv.reader(csvfile))
            next(it)
            for line in it:
                ret_set.add(line[index])
    except OSError as e:
        print('Error: ', e)
    finally:
        return ret_set
