"""
全局变量名称
"""

from enum import Enum, unique


@unique
class GlobalVariables(Enum):
    """
    全局变量名称
    """
    # 路径相关变量
    STATIC_DIR_PATH = 0
    STATIC_FILE_PATH = 1
    PRB_STATIC_FILE_PATH = 2
    DYNAMIC_FILE_PATH = 3

    MERGE_STATIC_PATH = 4
    CLEAN_FILE_PATH = 5
    SAVE_CGI_INFO_PATH = 6
    SAVE_PATH_HIGHLOAD = 7
    SAVE_PATH_ABNORMAL = 8
    save_forecast_file_rootdir = 9

    # 根据预测的负载结果计算每个扇区的License需求量并保存结果
    caculate_forecast_sector_license_save_dir = 10
    # 指定根据预测结果计算出的需扩容扇区结果保存的位置
    extend_sector_by_forecast_save_dir = 11
    # 指定根据预测结果计算出的可减容扇区结果保存的位置
    decreased_sector_by_forecast_save_dir = 12
    # 最终扩容清单（设定阈值之后）
    save_threshold_extend_dir = 13
    # 最终减容清单（设定阈值之后）
    save_threshold_decrease_dir = 14
    # 拿最后一周（如果将最后一周作为验证集则提取倒数第二周负载）估计出的小区高负载情况保存目录
    recent_load_select_save_dir = 15

    # 时间相关变量
    # 格式：'2019-06-18 00:00'
    dynamic_start_date = 16
    dynamic_days = 17
    # 预测结果起始日期
    forecast_start_date = 18
    forecast_days = 19
    training_days = 20
    # 需要用到的预测结果起始日期（开始部署的日期）
    start_analyze_date = 21
    analyze_days = 22
    # 预测数据的开始时间
    forecast_start_time = 23
    # 预测时长，以天计
    forecast_day_length = 24

    # 其他变量
    # 指定扩容阈值
    days_threshold_for_extend = 25
    # 减容系数，<=1
    reduce_volume_factor = 26
