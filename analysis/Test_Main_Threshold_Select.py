# 调查减容清单里的相关情况，看看天粒度下能否减容，周粒度下能否减容

from . import Lib_Statistic_Tools

import __config__ as cf
from __global__ import GlobalVariables
from utils.util import mkdir

def final_extend_decrease_by_threshold():

    forecast_decrease_dir = cf.glv_get(GlobalVariables.decreased_sector_by_forecast_save_dir)
    forecast_extend_dir = cf.glv_get(GlobalVariables.extend_sector_by_forecast_save_dir)

    recent_feature_extend_dir = cf.glv_get(GlobalVariables.recent_load_select_save_dir)

    days_threshold_for_extend = cf.glv_get(GlobalVariables.days_threshold_for_extend)

    save_threshold_decrease_dir = cf.glv_get(GlobalVariables.save_threshold_decrease_dir)
    mkdir(save_threshold_decrease_dir)

    save_threshold_extend_dir = cf.glv_get(GlobalVariables.save_threshold_extend_dir)
    mkdir(save_threshold_extend_dir)

    Lib_Statistic_Tools.threshold_decrease(forecast_decrease_dir,
                       save_threshold_decrease_dir)

    Lib_Statistic_Tools.threshold_extend(forecast_extend_dir,
                     recent_feature_extend_dir,
                     save_threshold_extend_dir,
                     days_threshold_for_extend)

