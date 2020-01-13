from Data_Forecast_Lib import *
from Data_Preprocessing_Lib import *

if __name__ == "__main__":
    # 保存计算扇区负载结果的路径
    CLEAN_FILE_PATH = r"C:\Users\USTC\Desktop\合并测试\Sector_Clean"

    # 获取CLEAN_FILE_PATH下所有文件的路径
    clean_file_path_list = get_data_path_list(CLEAN_FILE_PATH)

    # 预测的时间范围
    forecast_time_list=generate_time_list("2019-06-18 00:00", 7)

    # 读取所有扇区负载结果的文件
    sector_time_record_dic = get_sector_time_record_dic(clean_file_path_list)

    # 根据扇区历史负载预测未来扇区的负载
    # training_days：训练天数
    # testing_days：预测天数
    # save_forecast_file_rootdir：保存预测结果的路径
    # forecast_file_prefix：保存预测结果的文件名的前缀，保存预测结果的文件名为：前缀_扇区名.csv
    # 修正预测结果文件时间轴的保存的预测结果的前缀以后默认是 forecast_
    # yhat_choice的三种选择：'yhat', 'yhat_lower', 'yhat_upper'
    forecast_sector_load(forecast_time_list, sector_time_record_dic, training_days=37, testing_days=7,
                                         save_forecast_file_rootdir=r"C:\Users\USTC\Desktop\合并测试\Forecast",
                                         forecast_file_prefix='forecast_', yhat_choice="yhat_upper")

