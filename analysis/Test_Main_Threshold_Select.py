# 调查减容清单里的相关情况，看看天粒度下能否减容，周粒度下能否减容

import Lib_Statistic_Tools



if __name__=="__main__":

    forecast_decrease_dir = r'C:\projects\IFLYTEK\license\预测减容扇区'
    forecast_extend_dir = r'C:\projects\IFLYTEK\license\预测扩容扇区'

    recent_feature_extend_dir = r'C:\projects\IFLYTEK\license\扩容清单-基于近期负载特征优化'

    days_threshold_for_extend = 5

    save_threshold_decrease_dir = r'C:\projects\IFLYTEK\license\设定阈值的减容结果'

    save_threshold_extend_dir = r'C:\projects\IFLYTEK\license\设定阈值的扩容结果'

    Lib_Statistic_Tools.threshold_decrease(forecast_decrease_dir,
                       save_threshold_decrease_dir)

    Lib_Statistic_Tools.threshold_extend(forecast_extend_dir,
                     recent_feature_extend_dir,
                     save_threshold_extend_dir,
                     days_threshold_for_extend)

