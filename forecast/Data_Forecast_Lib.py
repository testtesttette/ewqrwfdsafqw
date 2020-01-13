from fbprophet import Prophet
import pandas as pd
import csv
import math
import os
from multiprocessing import Pool, cpu_count
from tqdm import tqdm


# 190726-14:47:增加了节日0607；调整了拟合模型时的参数


# 读取扇区负载文件并组织成字典
# sector_time_record_dic：key:扇区名；value：列表，列表元素为每小时的负载记录
def get_sector_time_record_dic(clean_file_path_list):
    sector_time_record_dic = {}
    for file_path in clean_file_path_list:
        sector_name = os.path.basename(file_path).split(".csv")[0]
        sector_time_record_dic[sector_name] = []

        with open(file_path, "r", encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)
            for line in it:
                sector_time_record_dic[sector_name].append(line)

    return sector_time_record_dic


# 预测单扇区负载
def run_prophet(tmp_turple):
    time_series = tmp_turple[0]
    testing_days = tmp_turple[1]

    # 节假日
    playoffs = pd.DataFrame({
        'holiday': 'playoff',
        'ds': pd.to_datetime(['2019-04-05']),
        'lower_window': 0,
        'upper_window': 2,
    })

    ldjs = pd.DataFrame({
        'holiday': 'ldj',
        'ds': pd.to_datetime(['2019-05-01']),
        'lower_window': 0,
        'upper_window': 3,
    })

    dwjs = pd.DataFrame({
        'holiday': 'dwj',
        'ds': pd.to_datetime(['2019-06-07']),
        'lower_window': -1,
        'upper_window': 3,
    })

    holidays = pd.concat((playoffs, ldjs, dwjs))
    holidays = holidays.reset_index()

    m = Prophet(holidays=holidays, holidays_prior_scale=20,  # 假日参数
                n_changepoints=8, changepoint_range=0.8, changepoint_prior_scale=5,  # 突变点参数  ,  突变点选成节假日天数如何
                weekly_seasonality=20, daily_seasonality=10, seasonality_prior_scale=20.0,  # 季节性参数
                interval_width=0.20).fit(time_series)

    # periods为预测时间，粒度为小时粒度
    future = m.make_future_dataframe(periods=testing_days * 24, freq='H')

    fcst = m.predict(future)

    # periods为预测时间，粒度为小时粒度
    return fcst[['yhat', 'yhat_lower', 'yhat_upper']].tail(testing_days * 24)


def forecast_by_record(forecast_time_list, sector_name, time_load_record, training_days, testing_days,
                       save_forecast_file_rootdir,
                       forecast_file_prefix, yhat_choice="yhat"):
    df = pd.DataFrame(time_load_record)
    df.rename(columns={0: '时间', 1: '有效RRC连接平均数(次)', 2: 'E-RAB建立成功数(个)', 3: '空口上行业务字节数(KByte)', 4: '空口下行业务字节数(KByte)',
                       5: '上行PUSCH PRB占用平均数(个)', 6: '下行PUSCH PRB占用平均数(个)', 7: 'license总数', 8: 'PRB可用总数', 9: 'CGI所在频段'},
              inplace=True)

    all_license_num = float(df["license总数"][0])
    all_prb_avil = float(df["PRB可用总数"][0])
    prb_no_str = df["CGI所在频段"][0]

    fcst_element_list = []

    for index in range(1, 7):
        # 选择数据集的行数：要用所有数据,iloc的第一个参数是冒号
        element_df = df.iloc[0:training_days * 24, [0, index]]
        element_df.columns = ['ds', 'y']

        fcst_element_list.append((element_df, testing_days))

    p = Pool(cpu_count())
    compute_element_list = list(tqdm(p.imap(run_prophet, fcst_element_list), total=len(fcst_element_list)))

    p.close()
    p.join()

    forecast_time_record_list = []

    for hour in range(training_days * 24, training_days * 24 + testing_days * 24):
        element_load_list = []
        for i in range(0, 6):
            element_load_list.append(compute_element_list[i].loc[hour, yhat_choice])

        forecast_time_record_list.append([forecast_time_list[hour - training_days * 24]] + element_load_list)

    save_record2file(forecast_time_record_list, all_license_num, all_prb_avil, prb_no_str,
                     forecast_file_prefix + sector_name + ".csv", save_forecast_file_rootdir)


# 保存预测结果
def save_record2file(forecast_time_record_list, all_license_num, all_prb_avil, prb_no_str, filename,
                     save_forecast_file_rootdir):
    filepath = os.path.join(save_forecast_file_rootdir, filename)
    with open(filepath, 'w', newline='', encoding='GBK') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["时间", "有效RRC连接平均数(次)", "E-RAB建立成功数(个)", "空口上行业务字节数(KByte)", "空口下行业务字节数(KByte)", "上行PUSCH PRB占用平均数(个)",
             "下行PUSCH PRB占用平均数(个)", "license总数", "PRB可用总数", "CGI所在频段"])

        for list in forecast_time_record_list:
            writer.writerow(list + [all_license_num, all_prb_avil, prb_no_str])

    print(filename, "已保存！")


def forecast_sector_load(forecast_time_list, sector_time_record_dic, training_days, testing_days,
                         save_forecast_file_rootdir=r"./Forcast_Data",
                         forecast_file_prefix='forecast_', yhat_choice="yhat"):
    for sector in sector_time_record_dic:
        forecast_by_record(forecast_time_list, sector, sector_time_record_dic[sector], training_days, testing_days,
                           save_forecast_file_rootdir, forecast_file_prefix, yhat_choice)
