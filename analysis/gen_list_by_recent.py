from . import analysis_lib

import __config__ as cf
from __global__ import GlobalVariables

from datetime import datetime
from utils.util import mkdir

def which_weekday(time: str):
    """
    time是星期几？
    :param time: 格式为 2018-12-08 00:00
    :return: 返回一个int，表示该日期为星期几：0表示星期一，1表示星期二，...，6表示星期日
    """
    return datetime.strptime(time, '%Y-%m-%d %H:%M').weekday()


# 判断“预测时间范围”是否在历史数据之间（如果是说明正在利用历史数据作为验证测试）
def during_history(history_finish_date, forecast_start_date):
    return forecast_start_date <= history_finish_date


def calculate_date_interval(date1,date2):
    return int(str(datetime.strptime(date1, '%Y-%m-%d') - datetime.strptime(date2, '%Y-%m-%d')).split(' ')[0]) + 1


def calculate_history_select_startdate_move_delta(history_last_date, forecast_start_date):
    forecast_start_weekday = which_weekday(forecast_start_date)
    history_last_weekday = which_weekday(history_last_date)
    delta1 = forecast_start_weekday - history_last_weekday
    return (-delta1 + 1) % 7


def extend_by_recent_feature_extract():

    ##################################################################################################################################
    # 以历史数据的最后一周特征检出高负载小区（如果将最后一周设为验证集则设置为倒数第二周）

    # 输入数据：
    # 以扇区为单位保存的小区清洗数据目录
    # 指定清洗出来的以小区为粒度保存的负载信息数据的目录（属于同一扇区的小区保存在同一文件，由李启亮给出）
    src_cleaned_sector_CGI_matching_loading_dir = cf.glv_get(GlobalVariables.SAVE_CGI_INFO_PATH)
    src_sector_load_dir = cf.glv_get(GlobalVariables.CLEAN_FILE_PATH)
    # 输出数据：
    # 拿最后一周（如果将最后一周作为验证集则平移倒数第二周负载）估计出的小区高负载情况保存目录
    overload_CGI_save_dir = cf.glv_get(GlobalVariables.recent_load_select_save_dir)  # 2019-07-19~2019-07-25
    mkdir(overload_CGI_save_dir)


    # 指定小区清洗数据的起始时间和负载数据的天数
    # 以及平移“最后一周”相对于真实数据末尾的天数：
        # 即，如果需要的预测结果是08-02~08-08，但负载数据是05-04~07-27，则平移的最后一周是07-19~07-25，相对于历史数据的末尾相差两天
    time_line_start = cf.glv_get(GlobalVariables.dynamic_start_date)
    sustain_days = cf.glv_get(GlobalVariables.dynamic_days)   # 一共的长度

    # 指定提取特征的最后一周落在预测结果的时刻的起始位置，例如想验证倒数第二周对最后一周高负载的影响，则before_Load_data设为7，即平移截至时间为“最后一周”之前
    recent_select_start_date = cf.glv_get(GlobalVariables.start_analyze_date)

    history_time_line = analysis_lib.generate_time_list_for_gen_result(time_line_start, sustain_days)

    last_day_date = history_time_line[-1]

    # 预测起始日期落在历史数据中，说明是在进行验证，提取验证集前一周的数据
    if during_history(last_day_date,recent_select_start_date):
        before_Load_data = calculate_date_interval(last_day_date.split(' ')[0], recent_select_start_date.split(' ')[0])
    else:
        before_Load_data = calculate_history_select_startdate_move_delta(last_day_date,recent_select_start_date)

    analysis_lib.judge_and_save_overload_CGI(src_cleaned_sector_CGI_matching_loading_dir,
                                             src_sector_load_dir,
                                             overload_CGI_save_dir,
                                             time_line_start,
                                             sustain_days,
                                             before_Load_data,
                                             recent_select_start_date)
