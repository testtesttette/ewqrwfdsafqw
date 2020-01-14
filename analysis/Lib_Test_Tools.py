# 关于各种负载统计和分析的库
import os
import csv
from . import Lib_Load_Forcast


def CGI_loading_padding(ori_CGI_load_dir,
                        ori_sector_load_dir,
                        refine_CGI_load_dir):

    ori_CGI_load_list = os.listdir(ori_CGI_load_dir)

    start_time = '2019-05-12 00:00'
    sustain_days = 44

    time_line = Lib_Load_Forcast.generate_time_list_for_gen_result(start_time, sustain_days)

    refiner_title = ["小区CGI", "时间", "有效RRC连接平均数(次)", "E-RAB建立成功数(个)", "空口上行业务字节数(KByte)", "空口下行业务字节数(KByte)",
                     "上行PRB平均利用率(%)", "下行PRB平均利用率(%)", "频点编号", "PRB可用数", "扇区当前绑定全部频段"]
    for i in ori_CGI_load_list:
        current_CGI_list = []
        with open(os.path.join(ori_sector_load_dir,i), "r", encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)
            for line in it:
                current_CGI_list = line[9]
                break


        sector_name = i.split('.cs')[0]


        CGIs_dic = {}

        time_line_index_counter = len(time_line)
        temp_counter = 0

        current_CGI = ''
        current_CGI_type = ''
        current_CGI_PRB = ''

        with open(os.path.join(ori_CGI_load_dir,i), "r", encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)

            for line in it:

                # 这个if用来初始化
                if line[0] not in CGIs_dic.keys():
                    if time_line_index_counter == len(time_line):
                        current_CGI = line[0]
                        current_CGI_type = line[8]
                        current_CGI_PRB = line[9]
                        CGIs_dic[current_CGI] = []
                        time_line_index_counter = 0

                    # 发生else说明当前CGI非文件起始CGI，且上一个CGI时间轴并不完整,补末尾
                    else:
                        padding_start = time_line_index_counter
                        for i in range(padding_start, len(time_line)):
                            CGIs_dic[current_CGI].append([current_CGI] + [time_line[i]] + [-1, -1, -1, -1, -1, -1] + [current_CGI_type] + [current_CGI_PRB] + [current_CGI_list])
                            time_line_index_counter = i + 1
                        current_CGI = line[0]
                        current_CGI_type = line[8]
                        current_CGI_PRB = line[9]
                        CGIs_dic[current_CGI] = []
                        time_line_index_counter = 0


                # print(time_line_index_counter)
                # 说明当前CGI正在被处理
                if time_line[time_line_index_counter] != line[1]:
                    temp_counter = 0
                    for i in range(0, len(time_line)):
                        temp_counter += 1
                        if time_line[time_line_index_counter + temp_counter] == line[1]:
                            break

                    for j in range(0, temp_counter):
                        CGIs_dic[current_CGI].append([current_CGI] + [time_line[time_line_index_counter + j]] + [-1,-1,-1,-1,-1,-1] + [current_CGI_type] + [current_CGI_PRB] + [current_CGI_list])

                    time_line_index_counter += temp_counter
                    # 从这一层出来说明时间轴就对上了


                CGIs_dic[current_CGI].append(line + [current_CGI_list])
                time_line_index_counter += 1

        # 补最后一个CGI的时间轴
        if time_line_index_counter != len(time_line):
            padding_start = time_line_index_counter
            for i in range(padding_start, len(time_line)):
                CGIs_dic[current_CGI].append(
                    [current_CGI] + [time_line[i]] + [-1, -1, -1, -1, -1, -1] + [current_CGI_type] + [
                        current_CGI_PRB] + [current_CGI_list])
                time_line_index_counter = i + 1



        with open(os.path.join(refine_CGI_load_dir,sector_name + '.csv'), "w", encoding="GBK", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(refiner_title)
            for i in CGIs_dic.keys():
                for j in CGIs_dic[i]:
                    writer.writerow(j)
#
#
#
#
#
#
#


# # 降高负载函数,用于分析性能
# # 输入现网高负载CGI清单，扇区预测结果，以及倒数第二周平移结果，最后一个参数为结果保存目录
def reduction_CGI_overload(real_result, picker_dir, forecast_dir, overcomed_path):
    forecast_file_list = os.listdir(forecast_dir)

    if picker_dir == '':
        picker_list = []
    else:
        picker_list = os.listdir(picker_dir)

    # 两下还没消掉的负载
    still_overload_list = []

    with open(real_result, "r", encoding="GBK") as csvfile:
        reader = csv.reader(csvfile)
        it = iter(reader)
        next(it)
        for line in it:
            correct_flag = 0
            if line[2] + '.csv' in forecast_file_list:
                # counter += 1
                with open(os.path.join(forecast_dir,line[2] + '.csv'), "r", encoding="GBK") as sector_csvfile:
                    sector_reader = csv.reader(sector_csvfile)
                    sector_it = iter(sector_reader)
                    next(sector_it)
                    for sector_line in sector_it:
                        if sector_line[0] == line[0]:
                            correct_flag = 1
            if line[2] + '.csv' in picker_list:
                with open(os.path.join(picker_dir ,line[2] + '.csv'), "r", encoding="GBK") as picker_csvfile:
                    picker_reader = csv.reader(picker_csvfile)
                    picker_it = iter(picker_reader)
                    next(picker_it)
                    for picker_line in picker_it:
                        if picker_line[0] == line[0]:
                            correct_flag = 1
            if correct_flag == 0:
                still_overload_list.append(line)

    title_list = ["时间", "高负荷CGI", "所在扇区", "所在频段"]
    with open(overcomed_path, "w", encoding="GBK", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(title_list)
        for i in still_overload_list:
            writer.writerow(i)


# 定义根据CGI高负载情况表计算系统内日峰值的函数
# overload_data_path即“forecast_path”或“picker_path”
# forecast_path表示经过预测算法优化后的高负载情况
# picker_path表示经过预测+平移算法优化后的高负载情况
def overload_result_by_days(overload_data_path, CGI_info_path, res_save_path, start_time, sus_days):
    CGI_num_per_hour_dic = {}

    with open(CGI_info_path, "r", encoding="GBK") as csvfile:
        reader = csv.reader(csvfile)
        it = iter(reader)
        next(it)
        for line in it:
            CGI_num_per_hour_dic[line[0]] = int(line[2])

    time_line= Lib_Load_Forcast.generate_time_list_for_gen_result(start_time, sus_days)

    overload_by_hours_dic = {}

    for i in time_line:
        overload_by_hours_dic[i] = 0

    day_separator = start_time.split(' ')[0]

    with open(overload_data_path, "r", encoding="GBK") as csvfile:
        reader = csv.reader(csvfile)
        it = iter(reader)
        next(it)

        for line in it:
            overload_by_hours_dic[line[0]] += 1

    result_list = []
    overload = 0
    max_hour = ''


    for i in overload_by_hours_dic.keys():
        now_day = i.split(' ')[0]
        if now_day != day_separator:
            result_list.append([day_separator, max_hour, overload])
            day_separator = now_day
            overload = 0

        else:
            if overload_by_hours_dic[i] / CGI_num_per_hour_dic[i] > overload:
                overload = overload_by_hours_dic[i] / CGI_num_per_hour_dic[i]
                max_hour = i

    result_list.append([day_separator, max_hour, overload])

    title_list = ["时间(天)","最大高负荷占比所在小时","高负荷占比"]
    with open(res_save_path, "w", encoding="GBK", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(title_list)
        for i in result_list:
            writer.writerow(i)