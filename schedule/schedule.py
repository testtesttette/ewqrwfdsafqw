"""
调度程序，用于给出小时级别的调度清单。
"""

from collections import defaultdict
import numpy as np
from functools import partial

from utils.exception import *
from utils.util import *

import __config__ as cf
from __global__ import GlobalVariables

# TODO：排除扇区怎么从静态表中筛选，写个程序or人工？
# 当前筛选规则：
#   ‘县市’列为拱墅区
#   ‘覆盖区域（场景）’列为火车站或高铁或高速公路
# 将满足条件的行的'小区中文名称'列去重后复制到一个新csv文件即可


# TODO: 修改对应的变量名
_EXCLUDE_SECTORS_FILE_PATH = r''
_PATH_PLUS = os.path.join(cf.glv_get(GlobalVariables.save_threshold_extend_dir),
                          r'预测结果/设定高负载出现天数不少于5天')
_PATH_REDUCE = os.path.join(cf.glv_get(GlobalVariables.save_threshold_decrease_dir),
                            r'按周粒度操作/1')
_PATH_TRANSLATE = os.path.join(cf.glv_get(GlobalVariables.save_threshold_extend_dir),
                               r'引入最近历史特征/设定高负载出现天数不少于5天')
_PATH_SCHEDULE = cf.glv_get(GlobalVariables.schedule_dir)
_START_TIME = cf.glv_get(GlobalVariables.forecast_start_date)
_FORECAST_DAY_LENGTH = cf.glv_get(GlobalVariables.forecast_days)
_FORECAST_HOUR_LENGTH = _FORECAST_DAY_LENGTH * 24
_REDUCE_VOLUME_FACTOR = cf.glv_get(GlobalVariables.reduce_volume_factor)

# fb_vector中各频段先后顺序为:
# A,D/D1,D2,D3,F1,F2,E1,E2,E3,FDD900,FDD1800,FDD,FDDNB/NB,DCS1800,GSM900
_FREQUENCY_BAND_INDEX_DICT = {
    'D': 0, 'D1': 0, 'D2': 1, 'D3': 2,
    'F1': 3, 'F2': 4,
    'FDD1800': 5, 'FDD-1800': 5,
    'A': 6,
    'FDD900': 7, 'FDD-900': 7,
    'E1': 8, 'E2': 9, 'E3': 10,
    # 'FDD': 11,
    # 'NB': 12, 'FDD-NB': 12,
    # 'DCS1800': 13,
    # 'GSM900': 14
}
_FB_LENGTH = max(_FREQUENCY_BAND_INDEX_DICT.values()) + 1
_FB_LIST = ['D1', 'D2', 'D3', 'F1', 'F2', 'FDD1800', 'A', 'FDD900', 'E1', 'E2', 'E3']


def load_data():
    """
    加载扩减容扇区的需求数据（预测得到）以及现网中的数据
    现网数据与预测数据在同一文件中一并给出，文件名即为扇区名。
    :return:
    """
    have_inited = defaultdict(bool)
    need_fb_dict = defaultdict(lambda: np.zeros((_FORECAST_HOUR_LENGTH, _FB_LENGTH), dtype=bool))
    active_fb_dict = defaultdict(lambda: np.zeros(_FB_LENGTH, dtype=bool))
    busy_before_list = []

    def do_loading(path: str, now_index: int, need_index: int, label: int):
        time_begin = parse(_START_TIME)
        for file_name in os.listdir(path):
            sector_name = file_name[:-4]
            if label == 2:
                busy_before_list.append(sector_name)
            with open(os.path.join(path, file_name), 'r', encoding='gbk') as csvfile:
                reader = iter(csv.reader(csvfile))
                next(reader)
                for line_index, line in enumerate(reader):
                    if line_index == 0:
                        for fb in line[now_index].split(','):
                            active_fb_dict[sector_name][_FREQUENCY_BAND_INDEX_DICT[fb]] = True
                        if not have_inited[sector_name]:
                            for _index in range(_FORECAST_HOUR_LENGTH):
                                need_fb_dict[sector_name][_index] = active_fb_dict[sector_name].copy()
                            have_inited[sector_name] = True
                    time_now = parse(line[0])
                    time_delta = time_now - time_begin
                    index = time_delta.days * 24 + time_delta.seconds // 3600
                    tmp_vector = np.zeros(_FB_LENGTH, dtype=bool)
                    for fb in line[need_index].split(','):
                        tmp_vector[_FREQUENCY_BAND_INDEX_DICT[fb]] = True
                    if label != 2:
                        need_fb_dict[sector_name][index] = tmp_vector.copy()
                    else:
                        need_fb_dict[sector_name][index] = active_fb_dict[sector_name] | tmp_vector

    do_loading(_PATH_PLUS, 4, 2, 0)
    do_loading(_PATH_REDUCE, 4, 2, 1)
    do_loading(_PATH_TRANSLATE, 3, 5, 2)
    return need_fb_dict, active_fb_dict, busy_before_list


def do_schedule(time, need_matrix, current_num_vector, wait_matrix, frozen, exclude_index_list, busy_index_before_list):
    """
    进行time时刻的调度任务
    :param time: 当前时刻
    :param need_matrix:
    :param current_num_vector:
    :param wait_matrix:
    :param frozen:
    :param exclude_index_list:
    :param busy_index_before_list:
    :return:
    """
    # 根据各个扇区当前license数量和L小时内变换wait_matrix计算L小时后应该有多少license的列表advance_list
    candidate_down = []
    # 保存本次调度调度计划，格式为（调度时刻，源扇区，目的扇区）
    source_list = []
    dest_list = []
    # temp_wait_vector保存下一小时初也即本小时末每个扇区添加的数量
    advance_vector = current_num_vector + np.sum(wait_matrix, axis=1)
    temp_wait_vector = wait_matrix[:, time % frozen].copy()
    advance_needs = 0

    sector_num, time_length = need_matrix.shape
    for index in range(sector_num):
        load = need_matrix[index][time + frozen]
        advance = advance_vector[index]
        current = current_num_vector[index]
        # 可能能拆的扇区:
        if load < advance:
            if index in exclude_index_list or index in busy_index_before_list:
                continue
            # num为某小时该扇区预计绑定的license数
            # min_surplus为某小时多余license的最小值
            num = current
            min_surplus = 100000
            for delta in range(frozen):
                num += wait_matrix[index][(time + delta) % frozen]
                min_surplus = min(num - need_matrix[index][time + delta], min_surplus)
            min_surplus = min(advance - load, min_surplus)
            # min_surplus == 0代表无可拆license
            if min_surplus == 0:
                wait_matrix[index][time % frozen] = 0
                continue
            current_num_vector_for_down = advance
            while min_surplus > 0:
                min_surplus -= 1
                current_num_vector_for_down -= 1
                for t in range(time + frozen, time_length):
                    if current_num_vector_for_down < need_matrix[index][t]:
                        candidate_down.append([index, t])
                        break
                else:
                    candidate_down.append([index, time_length])
            wait_matrix[index][time % frozen] = 0
        # 应该加的扇区：
        # 1.更新本次调度需要加的license数量;2.更新current_num_vector
        else:
            advance_needs += load - advance
            wait_matrix[index][time % frozen] = load - advance
            # 当前扇区下标加入dest_list
            for _ in range(load - advance):
                dest_list.append(index)
    candidate_down.sort(key=lambda x: x[1], reverse=True)

    # 更新current_num_vector
    advance_needs = int(_REDUCE_VOLUME_FACTOR * advance_needs)
    current_num_vector += temp_wait_vector
    for item in candidate_down:
        if advance_needs == 0:
            break
        if current_num_vector[item[0]] <= 1:
            continue
        current_num_vector[item[0]] -= 1
        # 当前扇区下标加入source_list
        source_list.append(item[0])
        advance_needs -= 1

    # if advance_needs > 0:
    #     raise LicenseLackError(advance_needs)
    # 检查current_num_vector数值是否合法
    for x in current_num_vector:
        if x <= 0:
            raise LicenseNumError(x)

    return source_list, dest_list, advance_needs


def generate_schedule_list(schedule_type: str, time: str, target_list: list, sector_list: list,
                           schedule_list: list, schedule_fb_dict: dict, active_vector: np.array, init_vector: np.array):
    conditions = lambda vec_a, vec_b, index: vec_a[index] < vec_b[index]
    if schedule_type == '去激活':
        schedule_types = ['减容去激活', '扩容去激活']
        delta = -1
        less = partial(conditions, active_vector, init_vector)
    else:  # schedule_type == '激活':
        schedule_types = ['扩容激活', '减容激活']
        delta = 1
        less = partial(conditions, init_vector, active_vector)

    flag_dict = defaultdict(int)
    schedule_dict = defaultdict(int)
    schedule_type_dict = {}
    for index in schedule_list:
        schedule_dict[index] += 1
        active_vector[index] += delta
        if less(index):
            if flag_dict[index] == 1:
                continue
            schedule_type_dict[index] = schedule_types[0]
        else:
            schedule_type_dict[index] = schedule_types[1]
            flag_dict[index] = 1

    for index in schedule_dict:
        target_list.append(
            [time, sector_list[index], schedule_dict[index], schedule_fb_dict[index], schedule_type_dict[index]])


def adapt_fbs(time: int, frozen: int, need_fb_tensor: np.array, active_fb_matrix: np.array, source_list: list,
              dest_list: list):
    source_fb_dict = defaultdict(list)
    dest_fb_dict = defaultdict(list)

    for sector_index in source_list:
        temp_vector = need_fb_tensor[sector_index][time] ^ active_fb_matrix[sector_index]
        fb_index = np.where(temp_vector == True)[0][0]
        active_fb_matrix[sector_index][fb_index] = False
        source_fb_dict[sector_index].append(_FB_LIST[fb_index])
    for key, value in source_fb_dict.items():
        source_fb_dict[key] = ','.join(value)

    for sector_index in dest_list:
        temp_vector = need_fb_tensor[sector_index][time + frozen] ^ active_fb_matrix[sector_index]
        fb_index = np.where(temp_vector == True)[0][0]
        active_fb_matrix[sector_index][fb_index] = True
        dest_fb_dict[sector_index].append(_FB_LIST[fb_index])
    for key, value in dest_fb_dict.items():
        dest_fb_dict[key] = ','.join(value)

    return source_fb_dict, dest_fb_dict


def schedule(frozen=4):
    """
    调度入口
    :param frozen: 禁锢时长
    :return:
    """
    # 读取预测负载数据、现网数据、平移扇区和排除扇区
    need_fb_dict, active_fb_dict, busy_before_list = load_data()
    exclude_set = get_set_from_csv(csv_name=_EXCLUDE_SECTORS_FILE_PATH, index=0)
    # 将扇区名和数据分开存储，调度时只使用索引下标，不使用具体扇区名
    sector_list = list(need_fb_dict.keys())
    need_fb_tensor = np.array(list(need_fb_dict.values()))  # sector * time_len * fb_length
    active_fb_matrix = np.array(list(active_fb_dict.values()))  # sector * fb_length

    # 后续准备工作
    need_matrix = need_fb_tensor.sum(axis=2)  # sector * time_len
    active_vector = active_fb_matrix.sum(axis=1)  # sector * 1
    exclude_index_list = [sector_list.index(sector) for sector in exclude_set if sector in sector_list]
    busy_index_before_list = [sector_list.index(sector) for sector in busy_before_list if sector in sector_list]

    # 拷贝一份，记录下初始化的数据，用于和调度后的数据进行对比
    init_vector = active_vector.copy()
    # current_num_vector记录当前小时各扇区分配license数量
    current_num_vector = active_vector.copy()
    wait_matrix = np.zeros((len(sector_list), frozen), dtype=int)

    # 需要根据预测时间生成日期列表
    global_time_line = _FORECAST_HOUR_LENGTH
    time_list = generate_time_list(_START_TIME, _FORECAST_DAY_LENGTH)

    # 开始生成调度列表，第一个调度时刻时，下一小时在need_fb_dict对应下标为0（例如调度时刻为00:00,那么下一小时为00：00-01：00），故从0开始
    source_large_list = []
    dest_large_list = []
    total_advance_needs = 0
    for time in range(global_time_line):
        if time + frozen >= global_time_line:
            break
        source_list, dest_list, advance_needs = do_schedule(time, need_matrix, current_num_vector, wait_matrix, frozen,
                                                            exclude_index_list, busy_index_before_list)
        total_advance_needs = total_advance_needs + advance_needs
        source_fb_dict, dest_fb_dict = adapt_fbs(time, frozen, need_fb_tensor, active_fb_matrix, source_list, dest_list)
        generate_schedule_list('去激活', time_list[time], source_large_list, sector_list, source_list, source_fb_dict,
                               active_vector, init_vector)
        generate_schedule_list('激活', time_list[time], dest_large_list, sector_list, dest_list, dest_fb_dict,
                               active_vector, init_vector)
    return source_large_list, dest_large_list, total_advance_needs


def main():
    source_large_list, dest_large_list, total_advance_needs = schedule()
    output_dir = _PATH_SCHEDULE
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_data2csv(source_large_list, os.path.join(output_dir, '源扇区.csv'),
                  ["时间", "去激活扇区", "去激活小区数量", '去激活频段', "去激活类型"])
    save_data2csv(dest_large_list, os.path.join(output_dir, '目的扇区.csv'),
                  ["时间", "激活扇区", "激活小区数量", '激活频段', "激活类型"])

    source_num = len(get_set_from_list(data_list=source_large_list, index=1))
    dest_num = len(get_set_from_list(data_list=dest_large_list, index=1))
    print('源扇区{num_1}个，目的扇区{num_2}个，总计{num_3}个'.format(num_1=source_num, num_2=dest_num, num_3=source_num + dest_num))
    if total_advance_needs > 0:
        print('还需要添加' + str(total_advance_needs) + '个license!')


if __name__ == '__main__':
    main()
