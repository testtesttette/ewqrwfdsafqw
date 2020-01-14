# 关于各种负载统计和分析的库
import os
import csv
import shutil
from . import Lib_Load_Forcast


# 倒数第二周平移检出高负载小区
# 分析小区扩容，有扩容的保存日期时刻，以扇区为单位保存
# 最后两个参数为要分析的数据的起始时间和持续长度，用来构造完整的时间轴
# 默认验证一周的长度，如果需要改变长度需调整函数内部数值和下标等
# 在测试的时候改一下参数
def judge_and_save_overload_CGI(src_cleaned_sector_CGI_matching_loading_dir,
                                src_sector_load_dir,
                                overload_CGI_save_dir,
                                time_line_start,
                                sustain_days,
                                before_Load_data,
                                recent_select_start_date):

    test_past_days = 7

    sector_CGI_dir = src_cleaned_sector_CGI_matching_loading_dir
    judge_save_dir_hours = overload_CGI_save_dir

    # 完整时间轴的长度
    whole_time_sustain_hours = sustain_days * 24

    # 小区负载
    sector_matching_CGI_dic = {}
    # 构造扇区对应的小区负载字典也模块化一下
    # 这个扇区长度是实际有小区工作的扇区长度
    sector_list = os.listdir(sector_CGI_dir)
    # 一个扇区保存了其对应小区的所有负载信息，但时间轴不完整

    # CGI信息的完整目录，应该是李启亮的风格
    path_info_list = []
    for i in range(0, len(sector_list)):
        path_info_list.append(os.path.join(sector_CGI_dir, sector_list[i]))

    for j in path_info_list:
        sector_name = os.path.basename(j).split(".csv")[0]

        # 定义完整时间轴
        full_timeline = Lib_Load_Forcast.generate_time_list_for_gen_result(time_line_start, sustain_days)
        with open(j, "r", encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)

            # 初始化#############################
            # 必要的几个小参数
            current_CGI = ''
            time_counter = 0
            padding_num = 0

            for line in it:
                if current_CGI != line[0] and current_CGI == '':
                    time_counter = 0
                    current_CGI = line[0]
                    sector_matching_CGI_dic[current_CGI] = []
                    sector_matching_CGI_dic[current_CGI].append(line[8])

                # CGI变了，说明换新的CGI信息了
                elif current_CGI != line[0] and current_CGI != '':
                    if time_counter < whole_time_sustain_hours:
                        for k in range(time_counter, whole_time_sustain_hours):
                            # 没有出现过的时间段就补-99
                            sector_matching_CGI_dic[current_CGI].append(-99)

                    time_counter = 0
                    current_CGI = line[0]
                    sector_matching_CGI_dic[current_CGI] = []
                    sector_matching_CGI_dic[current_CGI].append(line[8])

                if str(line[1]) != str(full_timeline[time_counter]):
                    for i in range(time_counter, whole_time_sustain_hours):
                        if str(line[1]) == str(full_timeline[i]):
                            padding_num = i - time_counter
                            time_counter = i
                            break

                    for j in range(0, padding_num):
                        sector_matching_CGI_dic[current_CGI].append(-99)

                if str(line[1]) == str(full_timeline[time_counter]):
                    if overload_judge_CGI(line) > 0:
                        sector_matching_CGI_dic[current_CGI].append(1)
                    # 高负载就是1，没高负载就是0
                    else:
                        sector_matching_CGI_dic[current_CGI].append(0)
                    time_counter += 1

            if time_counter != whole_time_sustain_hours:
                for k in range(time_counter, whole_time_sustain_hours):
                    # 没信息的继续给-99
                    sector_matching_CGI_dic[current_CGI].append(-99)

        # 真正未知的预测结果，构建平移后的“日期时间轴”
        recent_feature_time_list = Lib_Load_Forcast.generate_time_list_for_gen_result(recent_select_start_date, 7)


        # 以小时为粒度输出根据上个月最后一周高负载情况做粗略估计的小区未来一周高负载情况
        # 由于根据前24天预测最后七天，指定规则由第18天到第24天的小区高负载情况作为对最后七天的一个估计
        # 与真实情况做对比观察效果
        # 可能能分为一个新的函数
        CGI_for_sector_list = sector_matching_CGI_dic.keys()

        # 保存结果
        save_path_for_hours = os.path.join(judge_save_dir_hours, str(sector_name) + '.csv')

        title_list = ["时间", "小区CGI", "自身频点编号","扇区当前全部频段", "需要扩容的数量","扩容频段"]

        save_flag = 0
        # 判断这个扇区里是不是有CGI需要扩容，只起一个判断作用，保存正确的信息交给生产文件函数
        for i in CGI_for_sector_list:
            # 这是考虑连续两周出现高负载的情况进行平移
            # first_index_list = [i for i, x in enumerate(sector_matching_CGI_dic[i][-336-168: -336]) if x == 1]
            # second_index_list = [i for i, x in enumerate(sector_matching_CGI_dic[i][-336:-168]) if x == 1]

            # intersection = list(set(first_index_list).intersection(second_index_list))

            # if intersection != []:

            # 平移“一周”，所以是168
            start = -test_past_days * 24 - 24 * before_Load_data
            end = -24 * before_Load_data
            if end != 0:
                if 1 in sector_matching_CGI_dic[i][start:end]:
                    save_flag = 1
                    break
            else:
                if 1 in sector_matching_CGI_dic[i][start:]:
                    save_flag = 1
                    break

        if save_flag:
            with open(save_path_for_hours, "w", encoding="GBK", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(title_list)
                for output in range(0, 24 * 7):
                    # verify_time_list[output]
                    temp = []
                    counter = 0
                    CGI_type = []
                    for CGI in CGI_for_sector_list:
                        if sector_matching_CGI_dic[CGI][-test_past_days * 24 - 24 * before_Load_data + output] == 1:
                            counter += 1
                            temp.append(CGI)
                            CGI_type.append(sector_matching_CGI_dic[CGI][0])
                        # 这也是平移连续两周出现高负载的函数
                        # if temp == 1 and sector_matching_CGI_dic[CGI][-168-168-168 + output] == 1:
                    if counter > 0:
                        current_CGI_str = ''
                        current_CGI_list = []
                        with open(os.path.join(src_sector_load_dir, sector_name + '.csv'), "r", encoding="GBK") as csvfile:
                            reader = csv.reader(csvfile)
                            it = iter(reader)
                            next(it)
                            for line in it:
                                current_CGI_str = line[9]
                                current_CGI_list = line[9].split(',')
                                break

                        needing_extend_CGI = ''
                        for ec in range(0, len(temp)):
                            if ec == 0:
                                needing_extend_CGI += temp[ec]
                            else:
                                needing_extend_CGI = needing_extend_CGI + ',' + temp[ec]
                        ect_res = ''
                        for ect in range(0, len(CGI_type)):
                            if ect == 0:
                                ect_res += CGI_type[ect]
                            else:
                                ect_res = ect_res + ',' + CGI_type[ect]
                        extend_CGI_list = list(set(Lib_Load_Forcast.return_ext_list(sector_name, len(current_CGI_list) + counter, current_CGI_list)).difference(set(current_CGI_list)))

                        ecl_res = ''
                        for ecl in range(0, len(extend_CGI_list)):
                            if ecl == 0:
                                ecl_res += extend_CGI_list[ecl]
                            else:
                                ecl_res = ecl_res + ',' + extend_CGI_list[ecl]
                        writer.writerow([recent_feature_time_list[output]] + [needing_extend_CGI]  +[ect_res] + [current_CGI_str]+ [counter] + [ecl_res])
        sector_matching_CGI_dic.clear()



# 判断小区的一条负载是不是高负载
# 输入参数格式：[小区CGI	时间	有效RRC连接平均数(次)	E-RAB建立成功数(个)	空口上行业务字节数(KByte)	空口下行业务字节数(KByte)	上行PRB平均利用率(%)	下行PRB平均利用率(%)	频点编号	PRB可用数]
# 返回值：是否需要扩容，是则为1，否则为0
# 因为无法判断这个小区对应的扇区已经有了哪些频段，所以无法判断该给这个小区扩几个
def overload_judge_CGI(CGI_load_records_per_hour):
    # PRB_available = float(CGI_load_records_per_hour[9])
    RRC = float(CGI_load_records_per_hour[2])
    E_rab = float(CGI_load_records_per_hour[3])
    up_traf = float(CGI_load_records_per_hour[4])
    down_traf = float(CGI_load_records_per_hour[5])
    PUSCH = float(CGI_load_records_per_hour[6])
    PDSCH = float(CGI_load_records_per_hour[7])

    if E_rab > 0:
        E_rab_traf = (float(CGI_load_records_per_hour[4]) + float(CGI_load_records_per_hour[5]))/ E_rab
    else:
        E_rab_traf = 0

    if E_rab_traf >= 1000:
        if (RRC > 10 and up_traf/1000/1000 > 0.3 and PUSCH/100 > 0.5) or (RRC > 10 and down_traf/1000/1000 > 5 and PDSCH/100 > 0.7):
            return 1
        else:
            return 0

    elif E_rab_traf >= 300:
        if (RRC > 20 and up_traf/1000/1000 > 0.3 and PUSCH/100 > 0.5) or (RRC > 20 and down_traf/1000/1000 > 3.5 and PDSCH/100 > 0.5):
            return 1
        else:
            return 0

    else:
        if (RRC > 50 and up_traf/1000/1000 > 0.3 and PUSCH/100 > 0.5) or (RRC > 50 and down_traf/1000/1000 > 2.2 and PDSCH/100 > 0.4):
            return 1
        else:
            return 0







def threshold_extend(forecast_extend_dir,
                     recent_feature_extend_dir,
                     save_threshold_extend_dir,
                     days_threshold_for_extend):

    save_threshold_forecast_dir = os.path.join(save_threshold_extend_dir, '预测结果')
    save_threshold_recent_feature_dir = os.path.join(save_threshold_extend_dir, '引入最近历史特征')

    if not os.path.exists(save_threshold_forecast_dir):
        os.makedirs(save_threshold_forecast_dir)
    if not os.path.exists(save_threshold_recent_feature_dir):
        os.makedirs(save_threshold_recent_feature_dir)

    forecast_list = os.listdir(forecast_extend_dir)

    trans_list = os.listdir(recent_feature_extend_dir)

    for i in forecast_list:
        time_dic = {}
        days_counter = 0
        with open(os.path.join(forecast_extend_dir, i), "r", encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)

            for line in it:
                if line[0].split(' ')[0] not in time_dic.keys():
                    time_dic[line[0].split(' ')[0]] = 1
                    days_counter += 1
                else:
                    time_dic[line[0].split(' ')[0]] += 1

        # for j in range(0, 5):
        save_last_dir = os.path.join(save_threshold_forecast_dir,'设定高负载出现天数不少于{0}天'.format(days_threshold_for_extend))
        if days_counter >= days_threshold_for_extend:
            if not os.path.exists(save_last_dir):
                os.makedirs(save_last_dir)
            shutil.copy(os.path.join(forecast_extend_dir, i), save_last_dir)

    for i in trans_list:
        time_dic = {}
        days_counter = 0
        with open(os.path.join(recent_feature_extend_dir, i), "r", encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)

            for line in it:
                if line[0].split(' ')[0] not in time_dic.keys():
                    time_dic[line[0].split(' ')[0]] = 1
                    days_counter += 1
                else:
                    time_dic[line[0].split(' ')[0]] += 1

        # for j in range(0, 5):
        save_last_dir = os.path.join(save_threshold_recent_feature_dir,'设定高负载出现天数不少于{0}天'.format(days_threshold_for_extend))
        if days_counter >= days_threshold_for_extend:
            if not os.path.exists(save_last_dir):
                os.makedirs(save_last_dir)
            shutil.copy(os.path.join(recent_feature_extend_dir, i),save_last_dir)





def threshold_decrease(forecast_decrease_dir,
                       save_threshold_decrease_dir):


    save_whole_week_decrease_ops_dir = os.path.join(save_threshold_decrease_dir,'按周粒度操作')
    save_days_decrease_ops_dir = os.path.join(save_threshold_decrease_dir,'按天粒度操作')

    if not os.path.exists(save_whole_week_decrease_ops_dir):
        os.makedirs(save_whole_week_decrease_ops_dir)
    if not os.path.exists(save_days_decrease_ops_dir):
        os.makedirs(save_days_decrease_ops_dir)

    # days_decrease = r'C:\projects\IFLYTEK\license\减容扇区属性调查\按天粒度减容'

    decrease_list = os.listdir(forecast_decrease_dir)

    for i in decrease_list:
        time_dic = {}
        days_counter = 0
        license_counter = 0

        with open(os.path.join(forecast_decrease_dir,i), "r", encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)

            for line in it:
                if line[0].split(' ')[0] not in time_dic.keys():
                    time_dic[line[0].split(' ')[0]] = [1]
                    days_counter += 1
                    license_counter = int(line[5])
                    time_dic[line[0].split(' ')[0]].append(license_counter)
                else:
                    time_dic[line[0].split(' ')[0]][0] += 1
                    license_counter = min(license_counter,int(line[5]))
                    time_dic[line[0].split(' ')[0]][1] = license_counter

        # 基本信息都有了
        # days_counter 几天
        # time_dic[line[0].split(' ')[0]][1] 能省几个

        # 按周来
        if days_counter == 7:
            week_reduction = 99
            save_flag = 1
            for j in time_dic.keys():
                if time_dic[j][0] < 24:
                    save_flag = 0
                    break
                else:
                    week_reduction = min(week_reduction, time_dic[j][1])
            if save_flag == 1:
                if not os.path.exists(os.path.join(save_whole_week_decrease_ops_dir,str(week_reduction))):
                    os.mkdir(os.path.join(save_whole_week_decrease_ops_dir,str(week_reduction)))
                shutil.copy(os.path.join(forecast_decrease_dir, i), os.path.join(save_whole_week_decrease_ops_dir,str(week_reduction)))


        # 按天来
        if days_counter > 0:
            for j in time_dic.keys():
                if time_dic[j][0] == 24:
                    days_reduction_dir = os.path.join(save_days_decrease_ops_dir,str(j))
                    if not os.path.exists(days_reduction_dir):
                        os.mkdir(days_reduction_dir)
                    if not os.path.exists(os.path.join(days_reduction_dir,str(time_dic[j][1]))):
                        os.mkdir(os.path.join(days_reduction_dir,str(time_dic[j][1])))
                    shutil.copy(os.path.join(forecast_decrease_dir, i), os.path.join(days_reduction_dir,str(time_dic[j][1])))