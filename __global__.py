"""
全局变量名称
"""

from enum import Enum, unique


@unique
class GlobalVariables(Enum):
    """
    全局变量名称
    建议：
        文件路径的变量尽量用path结尾
        目录路径的变量尽量用dir结尾
    """
    # 源数据相关
    static_file_path = 0
    dynamic_data_dir = 1
    exclude_sectors_file_path = 2

    # output_root_dir 是输出结果的根目录，使用绝对路径
    output_root_dir = 3
    # 以下是具体输出的内容，使用相对上述根目录的路径
    plus_sectors_dir = 4
    reduce_sectors_dir = 5
    translation_sectors_dir = 6
    scheduel_list_dir = 7

    # 开始时间
    # 格式：'2019-06-18 00:00'
    start_time = 8
    # 预测数据的开始时间
    forecast_start_time = 9
    # 预测时长，以天计
    forecast_day_length = 10
    # 减容系数，<=1
    reduce_volume_factor = 11
