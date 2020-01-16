"""
一些公共函数。
"""

import os
import csv
from shutil import rmtree
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


def get_set_from_list(*, data_list: list, index: int):
    """
    统计列表中某一“列”含有的元素（不重复）
    :param data_list: 数据列表
    :param index: 需要的数据的索引下标
    :return:
    """
    result_set = set()
    for line in data_list:
        result_set.add(line[index])
    return result_set


def mkdir(path):
    """
    创建路径
    :param path: 待创建的路径
    :return: 无
    """
    if os.path.exists(path):
        print("检测到已有路径", path, "!将删除该路径下的所有文件和文件夹!")
        rmtree(path)
    os.makedirs(path)
    print("创建了文件夹", path)


def save_data2csv(data_list, file_name, title_list):
    """
    将数据与相应表头写入csv文件
    :param data_list: 数据列表
    :param file_name: 文件名
    :param title_list: 表头
    :return:
    """
    with open(file_name, "w", encoding="GBK", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(title_list)
        for line in data_list:
            writer.writerow(line)
