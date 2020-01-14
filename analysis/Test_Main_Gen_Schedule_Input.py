# 生成扩减容清单等可供调度算法进行分析的结果
# 生成的是由预测造成的扩减容

from . import Lib_Load_Forcast

import __config__ as cf
from __global__ import GlobalVariables


def extend_decrease_by_forecast():
    # 输入的数据：
    # 指定预测结果存放的文件夹位置（从集群上运行得到的结果合并到一起）
    forecast_loading_dir = cf.glv_get(GlobalVariables.save_forecast_file_rootdir)

    # 生成的数据：
    # 根据预测的负载结果计算每个扇区的License需求量并保存结果
    save_forecast_CGI_num_dir = cf.glv_get(GlobalVariables.caculate_forecast_sector_license_save_dir)

    # 指定需扩容扇区结果保存的位置
    save_extended_sector_dir = cf.glv_get(GlobalVariables.extend_sector_by_forecast_save_dir)
    # 指定可减容扇区结果保存的位置
    save_decreased_sector_dir = cf.glv_get(GlobalVariables.decreased_sector_by_forecast_save_dir)

    # 指定需要计算License需求量的预测起始日期和持续天数
    # （例如预测了2019-07-18~2019-08-29的数据，但需要的是08-02~08-08号共7天的数据，那就是'2019-08-02 00:00', 7）
    start_time = cf.glv_get(GlobalVariables.start_analyze_date)
    sustain_days = cf.glv_get(GlobalVariables.analyze_days)

    Lib_Load_Forcast.Forecast_handling_Saver(forecast_loading_dir,
                                             save_forecast_CGI_num_dir,
                                             save_extended_sector_dir,
                                             save_decreased_sector_dir,
                                             start_time,
                                             sustain_days)










