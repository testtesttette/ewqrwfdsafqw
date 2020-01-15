# 关于预测和License需求量的计算函数，其中关于预测和结果保存等函数需要更新为李启亮那边的最新函数（函数名重合的）

import math
import calendar
import copy
# # #
# 关于各种负载统计和分析的库
import os
import csv
import shutil


# 根据给定的起始时间和持续天数造时间轴
def generate_time_list_for_gen_result(start_date,num_days):
    # start_date的格式为 2019-03-18 00:00，days为天数，默认从start_date的零点开始生成
    year=int(start_date[0:4])
    month=int(start_date[5:7])
    day=int(start_date[8:10])
    time_list=[]

    for hour in range(0,24):
        time = str(year).zfill(4) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + " " + str(hour).zfill(2) + ":00"
        time_list.append(time)

    num_days-=1

    while num_days > 0:
        day+=1
        if day>calendar.monthrange(year,month)[1]:
            day=1
            month+=1
            if month>12:
                month=1
                year+=1

        for hour in range(0, 24):
            time = str(year).zfill(4) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + " " + str(hour).zfill(
                2) + ":00"
            time_list.append(time)

        num_days-=1

    return time_list

# 定义一个由PRB使用数量决定的减容函数，不同于扩容，减容有更多的限制
# 返回的是减容后的列表
# 有智障情况就是本身就没有主小区,所以另一个限制就是不能减到小于1个扇区
def return_decrease_caused_by_PRB(sector_name, CGI_list, PRB_needing_num):
    PRB_redundance_num = -PRB_needing_num
    resource_dic = {'D1': 100, 'D2': 100,'D3': 100,'D4': 100,'D5': 100,'D6': 100,'D7': 100,'D8': 100,'F1': 100,'F2': 50,'A': 75,'E1': 100,'E2': 100,'E3': 50,'FDD-1800': 100,'FDD-900': 50}

    main_list = ['D1', 'F1', 'FDD-1800', 'FDD-900', 'E1']

    new_bounded_list = []

    decrease_order_list = ['E3', 'E2', 'A', 'F2', 'D3', 'D2']

    for i in CGI_list:
        if i in main_list:
            new_bounded_list.append(i)

    remain_list = list(set(CGI_list).difference(set(new_bounded_list)))

    if remain_list != [] and new_bounded_list != []:

        for i in decrease_order_list:
            if i in remain_list:
                PRB_redundance_num -= resource_dic[i]
                if PRB_redundance_num > 0:
                    remain_list.remove(i)
                else:
                    return new_bounded_list + remain_list
        return new_bounded_list + remain_list

    elif remain_list != []:
        for i in decrease_order_list:

            if i in remain_list and len(remain_list) > 1:

                PRB_redundance_num -= resource_dic[i]
                if PRB_redundance_num > 0:
                    remain_list.remove(i)

                else:
                    return remain_list
        return new_bounded_list + remain_list
    else:
        #这一步说明都是主小区，不能减
        return CGI_list



# 定义了由PRB决定的PRB扩容情况
def return_extension_caused_by_PRB(sector_name, CGI_list, PRB_needing_num):
    resource_dic = {'D1': 100, 'D2': 100,'D3': 100,'D4': 100,'D5': 100,'D6': 100,'D7': 100,'D8': 100,'F1': 100,'F2': 50,'A': 75,'E1': 100,'E2': 100,'E3': 50,'FDD-1800': 100,'FDD-900': 50}

    ext_order_list = ['D1', 'D2', 'D3', 'F1', 'F2', 'FDD-1800', 'A', 'FDD-900', 'E1', 'E2', 'E3']
    candidate_list = list(set(ext_order_list).difference(set(CGI_list)))
    # 由PRB导致的扩容列表，当前没有但也许未来有用,同理扇区名也先留着
    Now_needing = PRB_needing_num
    CGI_ext_list = []

    for i in ext_order_list:
        if i in candidate_list:
            Now_needing -= resource_dic[i]
            CGI_ext_list.append(i)
            if Now_needing <= 0:
                return CGI_ext_list

    if Now_needing > 0:
        return []


# 可根据载波频段计算License数量
# 输入参数格式：[时间	有效RRC连接平均数(次)	E-RAB建立成功数(个)	空口上行业务字节数(KByte)	空口下行业务字节数(KByte)	上行PUSCH PRB占用平均数(个)	下行PDSCH PRB占用平均数(个)	license总数	PRB可用总数	CGI所在频段]
def extension_for_sector(sector_name, sector_load_info_per_hour):
    # 记录当前绑定了哪些小区
    CGI_list = sector_load_info_per_hour[9].split(',')
    RRC = float(sector_load_info_per_hour[1])
    E_RAB = float(sector_load_info_per_hour[2])
    UP_Tra = float(sector_load_info_per_hour[3])
    Down_Tra = float(sector_load_info_per_hour[4])
    PUSCH = float(sector_load_info_per_hour[5])
    PDSCH = float(sector_load_info_per_hour[6])
    AVAL_PRB = round(float(sector_load_info_per_hour[8]))

    if E_RAB > 0:
        E_RAB_Tra = (UP_Tra + Down_Tra) / E_RAB
    else:
        E_RAB_Tra = 0

    CGI_num = len(CGI_list)
    # 以平均方式先判断
    if E_RAB_Tra >= 1000:
        RRC_needing = math.ceil(RRC / 10)
        UP_Tra_needing = math.ceil(UP_Tra / 1000 / 1000 / 0.3)
        Down_Tra_needing = math.ceil(Down_Tra / 1000 / 1000 / 5)

        # AVAL_PRB每次都得由李启亮给出
        PUSCH_PRB_needing_num = math.ceil(PUSCH / 0.5) - AVAL_PRB
        PDSCH_PRB_needing_num = math.ceil(PDSCH / 0.7) - AVAL_PRB
        if PUSCH_PRB_needing_num > 0:
            PUSCH_needing = len(return_extension_caused_by_PRB(sector_name, CGI_list, PUSCH_PRB_needing_num))
            if PUSCH_needing == 0:
                # PUSCH_needing为零即return_extension_caused_by_PRB返回空列表，说明频段耗尽无法返回能满足需求的频段数量，设置异常值-99
                return -99
            else:
                PUSCH_needing += CGI_num
        else:
            # 这里留着给减容方式，先暂定为够用则不扩容也不减容
            # PUSCH_needing = CGI_num 接口启动
            PUSCH_needing = len(return_decrease_caused_by_PRB(sector_name, CGI_list, PUSCH_PRB_needing_num))


        if PDSCH_PRB_needing_num > 0:
            PDSCH_needing = len(return_extension_caused_by_PRB(sector_name, CGI_list, PDSCH_PRB_needing_num))
            if PDSCH_needing == 0:
                return -99
            else:
                PDSCH_needing += CGI_num
        else:
            # 启动接口
            PDSCH_needing = len(return_decrease_caused_by_PRB(sector_name, CGI_list, PDSCH_PRB_needing_num))

        sector_needing = max(min(RRC_needing,UP_Tra_needing,PUSCH_needing), min(RRC_needing, Down_Tra_needing,PDSCH_needing))
        return max(sector_needing, 1)

    elif E_RAB_Tra >= 300:
        RRC_needing = math.ceil(RRC / 20)
        UP_Tra_needing = math.ceil(UP_Tra / 1000 / 1000 / 0.3)
        Down_Tra_needing = math.ceil(Down_Tra / 1000 / 1000 / 3.5)

        PUSCH_PRB_needing_num = math.ceil(PUSCH / 0.5) - AVAL_PRB
        PDSCH_PRB_needing_num = math.ceil(PDSCH / 0.5) - AVAL_PRB
        if PUSCH_PRB_needing_num > 0:
            PUSCH_needing = len(return_extension_caused_by_PRB(sector_name,CGI_list, PUSCH_PRB_needing_num))
            if PUSCH_needing == 0:
                return -99
            else:
                PUSCH_needing += CGI_num
        else:
            PUSCH_needing = len(return_decrease_caused_by_PRB(sector_name, CGI_list, PUSCH_PRB_needing_num))

        if PDSCH_PRB_needing_num > 0:
            PDSCH_needing = len(return_extension_caused_by_PRB(sector_name,CGI_list, PDSCH_PRB_needing_num))
            if PDSCH_needing == 0:
                return -99
            else:
                PDSCH_needing += CGI_num
        else:
            PDSCH_needing = len(return_decrease_caused_by_PRB(sector_name, CGI_list, PDSCH_PRB_needing_num))

        sector_needing = max(min(RRC_needing, UP_Tra_needing, PUSCH_needing),
                             min(RRC_needing, Down_Tra_needing, PDSCH_needing))
        return max(sector_needing, 1)

    else:
        RRC_needing = math.ceil(RRC / 50)
        UP_Tra_needing = math.ceil(UP_Tra / 1000 / 1000 / 0.3)
        Down_Tra_needing = math.ceil(Down_Tra / 1000 / 1000 / 2.2)

        PUSCH_PRB_needing_num = math.ceil(PUSCH / 0.5) - AVAL_PRB
        PDSCH_PRB_needing_num = math.ceil(PDSCH / 0.4) - AVAL_PRB
        if PUSCH_PRB_needing_num > 0:
            PUSCH_needing = len(return_extension_caused_by_PRB(sector_name,CGI_list, PUSCH_PRB_needing_num))
            if PUSCH_needing == 0:
                return -99
            else:
                PUSCH_needing += CGI_num
        else:
            PUSCH_needing = len(return_decrease_caused_by_PRB(sector_name, CGI_list, PUSCH_PRB_needing_num))

        if PDSCH_PRB_needing_num > 0:
            PDSCH_needing = CGI_num
            if PDSCH_needing == 0:
                return -99
            else:
                PDSCH_needing += CGI_num
        else:
            PDSCH_needing = len(return_decrease_caused_by_PRB(sector_name, CGI_list, PDSCH_PRB_needing_num))
        sector_needing = max(min(RRC_needing, UP_Tra_needing, PUSCH_needing),
                             min(RRC_needing, Down_Tra_needing, PDSCH_needing))
        return max(sector_needing, 1)



# 根据给定的扇区需求量和当前绑定的频段列表给出调度后够用的频段，包含整个TDD和FDD，也是返回最终数量和频段类型的函数
def return_ext_list(sector_name, real_needing, CGI_list):
    resource_dic = {'D1': 100, 'D2': 100,'D3': 100,'D4': 100,'D5': 100,'D6': 100,'D7': 100,'D8': 100,'F1': 100,'F2': 50,'A': 75,'E1': 100,'E2': 100,'E3': 50,'FDD-1800': 100,'FDD-900': 50}

    ext_order_list = ['D1', 'D2', 'D3', 'F1', 'F2', 'FDD-1800', 'A', 'FDD-900', 'E1', 'E2', 'E3']

    main_list = ['D1','F1','FDD-1800', 'FDD-900','E1']

    result_list = []
    # 减容操作
    if real_needing < len(CGI_list):
        counter = 0
        for i in ext_order_list:
            if i in CGI_list:
                if i in main_list:
                    counter += 1
                    result_list.append(i)
        if len(result_list) >= real_needing:
            return result_list
        else:
            for i in ext_order_list:
                if i in list(set(CGI_list).difference(set(main_list))):
                    counter += 1
                    result_list.append(i)
                    if counter >= real_needing:
                        return result_list

    # 扩容操作
    elif real_needing > len(CGI_list):
        ext_num = real_needing - len(CGI_list)
        counter = 0
        result_list = copy.deepcopy(CGI_list)
        candidate_list = list(set(ext_order_list).difference(set(CGI_list)))
        for i in ext_order_list:
            if i in candidate_list:
                counter += 1
                result_list.append(i)
                if counter >= ext_num:
                    return result_list
        if counter < ext_num:
            return ["无法满足扩容需求—频段种类耗尽"]

    else:
        return CGI_list



# 根据汇总后的扇区负载预测结果，计算出扇区的License需求数量并筛选出扩减容扇区
def Forecast_handling_Saver(forecast_loading_dir,
                            save_forecast_CGI_num_dir,
                            save_extended_sector_dir,
                            save_decreased_sector_dir,
                            start_time,
                            sustain_days):
    full_time_line = generate_time_list_for_gen_result(start_time, sustain_days)


    # 指定扇区License需求量保存的数据结构（字典）
    all_sector_needing_dic = {}

    # 指定需扩容扇区的保存结果
    extend_by_int_needing_dic = {}

    # 指定可减容扇区的保存结果
    decrease_by_int_needing_dic = {}

    # 设置扇区需求量计算保存结果的表头（扩容与其一致）
    title = ["时间","新需求个数","新需求频段","静态表当前绑定的个数","静态表当前绑定的频段"]

    # 设置需扩容扇区结果保存的表头
    extend_title = ["时间", "新需求个数", "新需求频段", "静态表当前绑定的个数", "静态表当前绑定的频段", "需要扩容的数量","扩容频段"]


    # 设置可减容扇区结果保存的表头，由于减容存在不能减去主频段和至少保证有一个频段在应用等约束，多加了一列“真正能拆的数量”和“对应的频段”
    decrease_title = ["时间", "新需求个数", "新需求频段", "静态表当前绑定的个数", "静态表当前绑定的频段", "真正能拆的数量","拆除频段"]

    # 初始化字典
    all_sector_needing_dic.clear()
    extend_by_int_needing_dic.clear()
    decrease_by_int_needing_dic.clear()

    # 扩容扇区的标记位，之后如果判断出一个扇区需要扩容则会变为1，保存完结果后重置
    ext_flag = 0

    forecast_load_sector_list = os.listdir(forecast_loading_dir)

    for i in forecast_load_sector_list:
        full_path = os.path.join(forecast_loading_dir, i)
        sector_name = i.split('st_')[1].split('.cs')[0]

        all_sector_needing_dic[sector_name] = []
        extend_by_int_needing_dic[sector_name] = []
        decrease_by_int_needing_dic[sector_name] = []

        # 预测结果含有负值，需要整体抬高至0值以上，设置修正变量
        ruler = [0,0,0,0,0,0]
        with open(full_path, "r", encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)
            for line in it:
                if float(line[1]) < ruler[0]:
                    ruler[0] = float(line[1])
                if float(line[2]) < ruler[1]:
                    ruler[1] = float(line[2])
                if float(line[3]) < ruler[2]:
                    ruler[2] = float(line[3])
                if float(line[4]) < ruler[3]:
                    ruler[3] = float(line[4])
                if float(line[5]) < ruler[4]:
                    ruler[4] = float(line[5])
                if float(line[6]) < ruler[5]:
                    ruler[5] = float(line[6])

        # 以扇区预测结果为单位分析该扇区的需求和扩减容情况
        with open(full_path, "r", encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)

            for line in it:
                # 判断预测结果信息是否是需要的
                if line[0] in full_time_line:
                    # 当前静态表绑定的频段类型
                    static_table_CGI_type_list = line[9].split(',')

                    # print(static_table_CGI_type_list)
                    # 计算出的扇区需求数
                    line[1] = float(line[1]) - ruler[0] + 0.001
                    line[2] = float(line[2]) - ruler[1] + 0.001
                    line[3] = float(line[3]) - ruler[2] + 0.001
                    line[4] = float(line[4]) - ruler[3] + 0.001
                    line[5] = float(line[5]) - ruler[4] + 0.001
                    line[6] = float(line[6]) - ruler[5] + 0.001

                    # 计算当前负载下扇区的License需求量
                    real_needing = extension_for_sector(sector_name, line)

                    # 根据License需求量和当前扇区绑定的频段类型（静态表）得到扇区扩减容后的频段类型
                    integer_list = return_ext_list(sector_name, real_needing, static_table_CGI_type_list)

                    # 对integer_list进行格式整理使其按指定格式保存在csv文件中
                    res = ''
                    #######################
                    # print(sector_name)
                    for i in range(0, len(integer_list)):

                        if i == 0:
                            res += integer_list[i]
                        else:
                            res = res + ',' + integer_list[i]

                    all_sector_needing_dic[sector_name].append([line[0]] + [real_needing] + [res] + [line[7]] + [line[9]])

                    # 判断是否需要扩容
                    need_extend_num = int(real_needing) - round(float(line[7]))


                    # print("????????????????????????????????")
                    # print(real_needing)
                    # print(round(float(line[7])))
                    # print(static_table_CGI_type_list)
                    if need_extend_num > 0:
                        # print(static_table_CGI_type_list)

                        # print(need_extend_num)
                        need_extend_list = list(set(integer_list).difference(set(static_table_CGI_type_list)))
                        # print(sector_name)
                        # print("/////////////////////////////////////////////////")
                        # print(integer_list)
                        # print(static_table_CGI_type_list)
                        # print(need_extend_list)
                        nel_res = ''
                        for nel in range(0, len(need_extend_list)):
                            if nel == 0:
                                nel_res += need_extend_list[nel]
                            else:
                                nel_res = nel_res + ',' + need_extend_list[nel]

                        extend_by_int_needing_dic[sector_name].append([line[0]] + [real_needing] + [res] + [line[7]] + [line[9]] + [need_extend_num] + [nel_res])
                        # ext_flag = 1

                    # 判断是否可以减容
                    if int(real_needing) < round(float(line[7])):
                        # 注意，需求数少于绑定数不代表扇区一定能拆，如果都是主小区则不能拆
                        can_decrease_num = round(float(line[7])) - len(integer_list)
                        if can_decrease_num > 0:
                            #########################
                            can_decrease_list = list(set(static_table_CGI_type_list).difference(set(integer_list)))
                            cdl_res = ''
                            for cdl in range(0, len(can_decrease_list)):
                                if cdl == 0:
                                    cdl_res += can_decrease_list[cdl]
                                else:
                                    cdl_res = cdl_res + ',' + can_decrease_list[cdl]
                            # print(can_down_list)
                            decrease_by_int_needing_dic[sector_name].append([line[0]] + [real_needing] + [res] + [line[7]] + [line[9]] + [can_decrease_num] + [cdl_res])

    # 保存结果——每个扇区的需求结果
    for j in all_sector_needing_dic.keys():
        full_path = os.path.join(save_forecast_CGI_num_dir, j + '.csv')
        with open(full_path, "w", encoding="GBK", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(title)
            for i in all_sector_needing_dic[j]:
                writer.writerow(i)

    # 保存结果——需扩容扇区的结果
    for k in extend_by_int_needing_dic.keys():
        if extend_by_int_needing_dic[k] != []:
            full_path = os.path.join(save_extended_sector_dir, k + '.csv')
            with open(full_path, "w", encoding="GBK", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(extend_title)
                for i in extend_by_int_needing_dic[k]:
                    writer.writerow(i)

    # 保存结果——可减容扇区的结果
    for j in decrease_by_int_needing_dic.keys():
        if decrease_by_int_needing_dic[j] != []:
            full_path = os.path.join(save_decreased_sector_dir, j + '.csv')
            with open(full_path, "w", encoding="GBK", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(decrease_title)
                for i in decrease_by_int_needing_dic[j]:
                    writer.writerow(i)




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
        full_timeline = generate_time_list_for_gen_result(time_line_start, sustain_days)
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
        recent_feature_time_list = generate_time_list_for_gen_result(recent_select_start_date, 7)


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
                        extend_CGI_list = list(set(return_ext_list(sector_name, len(current_CGI_list) + counter, current_CGI_list)).difference(set(current_CGI_list)))

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
    # save_days_decrease_ops_dir = os.path.join(save_threshold_decrease_dir,'按天粒度操作')

    if not os.path.exists(save_whole_week_decrease_ops_dir):
        os.makedirs(save_whole_week_decrease_ops_dir)
    # if not os.path.exists(save_days_decrease_ops_dir):
    #     os.makedirs(save_days_decrease_ops_dir)



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

        #
        # # 按天来
        # if days_counter > 0:
        #     for j in time_dic.keys():
        #         if time_dic[j][0] == 24:
        #             days_reduction_dir = os.path.join(save_days_decrease_ops_dir,str(j))
        #             if not os.path.exists(days_reduction_dir):
        #                 os.mkdir(days_reduction_dir)
        #             if not os.path.exists(os.path.join(days_reduction_dir,str(time_dic[j][1]))):
        #                 os.mkdir(os.path.join(days_reduction_dir,str(time_dic[j][1])))
        #             shutil.copy(os.path.join(forecast_decrease_dir, i), os.path.join(days_reduction_dir,str(time_dic[j][1])))









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

    time_line= generate_time_list_for_gen_result(start_time, sus_days)

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