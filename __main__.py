import __config__ as cf
from __global__ import GlobalVariables


# TODO：全局变量定义在下面
cf.init()

# TODO：根目录名字？
cf.glv_set(GlobalVariables.reduce_volume_factor, 1.0)

cf.glv_set(GlobalVariables.MERGE_STATIC_PATH, r"C:\Users\USTC\Desktop\合并测试\DZ_Merge_Static.csv")
cf.glv_set(GlobalVariables.CLEAN_FILE_PATH, r"C:\Users\USTC\Desktop\合并测试\Sector_Clean")
cf.glv_set(GlobalVariables.SAVE_CGI_INFO_PATH, r"C:\Users\USTC\Desktop\合并测试\CGI_Clean")
cf.glv_set(GlobalVariables.SAVE_PATH_HIGHLOAD, r"C:\Users\USTC\Desktop\合并测试\DZ_0512_0624_highload_cgi_list.csv")
cf.glv_set(GlobalVariables.SAVE_PATH_ABNORMAL, r"C:\Users\USTC\Desktop\合并测试\DZ_0512_0624_abnormal_cgi_list.csv")
cf.glv_set(GlobalVariables.save_forecast_file_rootdir, r"C:\Users\USTC\Desktop\合并测试\Forecast")

#
cf.glv_set(GlobalVariables.caculate_forecast_sector_license_save_dir, r"C:\Users\USTC\Desktop\合并测试\扇区需求计算结果")
cf.glv_set(GlobalVariables.extend_sector_by_forecast_save_dir, r"C:\Users\USTC\Desktop\合并测试\预测扩容扇区")
cf.glv_set(GlobalVariables.decreased_sector_by_forecast_save_dir, r"C:\Users\USTC\Desktop\合并测试\预测减容扇区")

cf.glv_set(GlobalVariables.recent_load_select_save_dir, r"C:\Users\USTC\Desktop\合并测试\基于近期负载特征优化的扩容扇区")

cf.glv_set(GlobalVariables.save_threshold_extend_dir, r'C:\Users\USTC\Desktop\合并测试\设定阈值的扩容结果')
cf.glv_set(GlobalVariables.save_threshold_decrease_dir, r'C:\Users\USTC\Desktop\合并测试\设定阈值的减容结果')
cf.glv_set(GlobalVariables.days_threshold_for_extend, 5)


def complete_config():
    """
    根据传入的参数完善相关配置
    :return:
    """
    cf.glv_set(GlobalVariables.STATIC_DIR_PATH, r'C:\Users\USTC\Desktop\合并测试\静态表')
    cf.glv_set(GlobalVariables.STATIC_FILE_PATH, r'C:\Users\USTC\Desktop\合并测试\静态表\0512-更新-静态表.csv')
    cf.glv_set(GlobalVariables.PRB_STATIC_FILE_PATH, r'C:\Users\USTC\Desktop\合并测试\Prb_Static.csv')
    cf.glv_set(GlobalVariables.DYNAMIC_FILE_PATH, r'C:\Users\USTC\Desktop\合并测试\动态表')

    cf.glv_set(GlobalVariables.dynamic_start_date, "2019-05-12 00:00")
    cf.glv_set(GlobalVariables.dynamic_days, 44)
    cf.glv_set(GlobalVariables.training_days, 37)
    cf.glv_set(GlobalVariables.forecast_start_date, "2019-06-18 00:00")
    cf.glv_set(GlobalVariables.forecast_days, 7)

    cf.glv_set(GlobalVariables.start_analyze_date, '2019-06-18 00:00')
    cf.glv_set(GlobalVariables.analyze_days, 7)


def main():
    complete_config()
    # TODO：依次调用各个子包下的入口函数
    # TODO：具体模块的导入要在complete_config函数后边
    from forecast.Data_Preprocessing_Forecast_Main import data_preprocessing_and_forecast
    from analysis.Test_Main_Gen_Schedule_Input import extend_decrease_by_forecast
    from analysis.Test_Main_Recent_Select import extend_by_recent_feature_extract
    from analysis.Test_Main_Threshold_Select import final_extend_decrease_by_threshold

    data_preprocessing_and_forecast()
    extend_decrease_by_forecast()
    extend_by_recent_feature_extract()
    final_extend_decrease_by_threshold()


if __name__ == '__main__':
    main()
