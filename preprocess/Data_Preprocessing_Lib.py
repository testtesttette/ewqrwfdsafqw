import os
import csv
import operator
import calendar
import pandas as pd
import numpy as np
import shutil


def mkdir(path):
    '''
    创建路径
    :param path: 待创建的路径
    :return: 无
    '''
    folder=os.path.exists(path)

    if folder:
        print("检测到已有路径",path,"!将删除该路径下的所有文件和文件夹!")
        shutil.rmtree(path)

    os.makedirs(path)
    print("创建了文件夹", path)

# 合并静态表


def get_merge_static_dic(static_dir_path):
    """
    将所有的静态表合并成一个静态表，并以字典的形式返回
    :param static_dir_path: 所有静态表所在的根目录
    :return: merge_static_dic：key:扇区名；value:扇区包含的所有小区的频段号和CGI编号
    """
    static_path_list = get_data_path_list(static_dir_path)
    merge_static_dic = {}
    sector_name_index = -1
    cgi_no_column_list = ['F1', 'F2', 'A', 'D1', 'D2', 'D3', 'E1', 'E2', 'E3', 'F/D/E', 'FDD-900', 'FDD-1800']
    cgi_name_column_list = ["共址小区CGI1", "共址小区CGI2", "共址小区CGI3", "共址小区CGI4", "共址小区CGI5", "共址小区CGI6", "共址小区CGI7",
                            "共址小区CGI8", "共址小区CGI9", "共址小区CGI10", "共址小区CGI12", "共址小区CGI13"]
    cgi_no_index_list = []
    cgi_name_index_list = []

    for static_path in static_path_list:
        with open(static_path, 'r', encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            for i, rows in enumerate(reader):
                if i == 0:
                    title_list = rows

                    # 达州数据的静态表中扇区中文名所在列的列名是：扇区中文名称
                    sector_name_index = get_index_no(static_path, title_list, "扇区中文名称")
                    # 杭州数据的静态表中扇区中文名所在列的列名是：小区中文名称
                    # sector_name_index=get_index_no(static_path, title_list,"小区中文名称")

                    cgi_no_index_list = get_index_list(static_path, title_list, cgi_no_column_list)
                    cgi_name_index_list = get_index_list(static_path, title_list, cgi_name_column_list)
                    break

        with open(static_path, "r", encoding="GBK") as csvfile:
            print("正在读取", os.path.basename(static_path), "……")
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)

            for line in it:
                sector_name = line[sector_name_index]

                if sector_name == "":
                    continue

                if sector_name not in merge_static_dic:
                    merge_static_dic[sector_name] = {}
                for i in range(0, len(cgi_no_index_list)):
                    no_index = cgi_no_index_list[i]
                    name_index = cgi_name_index_list[i]
                    cgi_no = line[no_index]
                    cgi_name = line[name_index]
                    if cgi_no == "":
                        continue
                    if "#" not in cgi_no:

                        # 达州数据：将静态表中FDD-900/FDD-1800列的数据中的FDD900/FDD1800转为FDD-900/FDD-1800
                        if cgi_no == "FDD900":
                            cgi_no = "FDD-900"
                        elif cgi_no == "FDD1800":
                            cgi_no = "FDD-1800"

                        if cgi_no not in merge_static_dic[sector_name]:
                            merge_static_dic[sector_name][cgi_no] = set()
                        merge_static_dic[sector_name][cgi_no].add(cgi_name)
                    else:
                        split_no_list = cgi_no.split("#")
                        split_name_list = cgi_name.split("#")
                        for split_index in range(0, len(split_no_list)):
                            split_no = split_no_list[split_index]
                            split_name = split_name_list[split_index]
                            if split_no not in merge_static_dic[sector_name]:
                                merge_static_dic[sector_name][split_no] = set()
                            merge_static_dic[sector_name][split_no].add(split_name)

    return merge_static_dic


def set2str(tmp_set):
    """
    将一个集合中的相邻两个元素用“#”连接起来，并返回连接后的字符串
    :param tmp_set: 待连接的集合
    :return: tmp_str: 用#连接后的字符串
    """
    tmp_list = list(tmp_set)
    if len(tmp_list) == 1:
        return tmp_list[0]
    else:
        tmp_str = tmp_list[0]
        for i in range(1, len(tmp_list)):
            tmp_str += "#" + tmp_list[i]
    return tmp_str


def save_merge_static_dic(merge_static_dic, save_path):
    """
    保存合并后的静态表
    :param merge_static_dic：key:扇区名；value:扇区包含的所有小区的频段号和CGI编号
    :param save_path: 保存路径
    :return: 无
    """
    with open(save_path, "w", encoding="GBK", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for sector_name in merge_static_dic:
            tmp_list = [sector_name]
            for cgi_no in merge_static_dic[sector_name]:
                tmp_list += [cgi_no, set2str(merge_static_dic[sector_name][cgi_no])]
            writer.writerow(tmp_list)


# 将每个扇区的所有小区的负载数据以扇区为单位保存


class CGI_Value:
    fre_band_No = ""
    prb_avil_num = 0
    time_load_dic = {}
    belong_sector = ""

    # 由于关于FDD1800和FDD900两个频点的备注信息不清楚，因此暂时未加入这两个
    # 由于频段对应的prb可用数更改为读prb配置表获取，所以以下代码没用了
    # def get_prb_avil_num(self, fre_band_No):
    #     if fre_band_No in ['D1', 'D2', 'D3', 'F1', 'E1', 'E2', 'D', 'D4', 'D5', 'D6', 'D7', 'D8']:
    #         return 100
    #     elif fre_band_No in ['A']:
    #         return 75
    #     elif fre_band_No in ['F2', 'E3']:
    #         return 50

    def __init__(self, fre_band_No, prb_avil_num, belong_sector):
        self.fre_band_No = fre_band_No
        self.prb_avil_num = prb_avil_num
        self.belong_sector = belong_sector
        self.time_load_dic = {}


def save_cgi_info(sector_cgi_dic, cgi_info_dic, clean_path):
    title_list=["小区CGI", "时间", "有效RRC连接平均数(次)", "E-RAB建立成功数(个)", "空口上行业务字节数(KByte)", "空口下行业务字节数(KByte)", "上行PRB平均利用率(%)", "下行PRB平均利用率(%)", "频点编号", "PRB可用数"]
    for sector in sector_cgi_dic:
        s = sector.replace("\\", "", len(sector))
        save_path=os.path.join(clean_path, s + ".csv")

        # 若扇区绑定的CGI的time_load_dic的长度为0，不保存
        cgi_list = sector_cgi_dic[sector]
        flag=0
        for cgi_no in cgi_list:
            if len(cgi_info_dic[cgi_no].time_load_dic)!=0:
                flag=1
                break
        if flag == 0:
            continue
        with open(save_path, "w", encoding="GBK", newline="") as csvfile:
            writer=csv.writer(csvfile)
            writer.writerow(title_list)

            for cgi_no in cgi_list:
                tmp_value=cgi_info_dic[cgi_no]
                fre_no=tmp_value.fre_band_No
                prb_avil_num=tmp_value.prb_avil_num
                time_load_dic=tmp_value.time_load_dic
                for time in time_load_dic:
                    writer.writerow([cgi_no, time] + time_load_dic[time] + [fre_no, prb_avil_num])

        print(sector+".csv", "已保存！")


# 判断动态表中现网的高负荷小区的CGI


# 判断cgi是否为高负荷小区，prb利用率直接给出
def is_CGI_highLoad_real(element_load_list):
    for i in range(0, 4):
        element_load_list[i] = float(element_load_list[i])

    rrc = element_load_list[0]
    if element_load_list[1] == 0:
        e_rab = 0
    else:
        e_rab = (element_load_list[2] + element_load_list[3]) / element_load_list[1]

    if element_load_list[4] == "":
        up_prb_util = 0
    else:
        up_prb_util = float(element_load_list[4]) / 100

    if element_load_list[5] == "":
        down_prb_util = 0
    else:
        down_prb_util = float(element_load_list[5]) / 100

    up_traffic = element_load_list[2] / 1000 / 1000
    down_traffic = element_load_list[3] / 1000 / 1000

    if e_rab >= 1000:
        if rrc >= 10 and up_prb_util >= 0.5 and up_traffic >= 0.3:
            return True
        elif rrc >= 10 and down_prb_util >= 0.7 and down_traffic >= 5:
            return True
    elif e_rab >= 300:
        if rrc >= 20 and up_prb_util >= 0.5 and up_traffic >= 0.3:
            return True
        elif rrc >= 20 and down_prb_util >= 0.5 and down_traffic >= 3.5:
            return True
    else:
        if rrc >= 50 and up_prb_util >= 0.5 and up_traffic >= 0.3:
            return True
        elif rrc >= 50 and down_prb_util >= 0.4 and down_traffic >= 2.2:
            return True

    return False


def save_record_list(record_list, save_path, title_list):
    '''
    将列表保存为.csv文件
    :param record_list:需要保存的列表
    :param save_path:保存的路径
    :param title_list:保存的.csv文件的列名
    :return:无
    '''
    with open(save_path, "w", encoding="GBK", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(title_list)

        for line in record_list:
            writer.writerow(line)


# 计算数据集中扇区的负载数据


# 获取动态表重命名后的文件名列表（以动态表第一条记录的时间为该文件的文件名）
# input:data_path_list:所有动态表路径列表
# output:afterlist:动态表重命名后的文件名列表
def get_rename_afterlist(data_path_list):
    afterList = []
    for data_path in data_path_list:
        with open(data_path, 'r', encoding='GBK') as csvfile:
            reader = csv.reader(csvfile)
            for i, rows in enumerate(reader):
                if i == 1:
                    time = rows[0]
                    afterList.append(time + '.csv')
                    break

    return afterList


# 对负载文件进行重命名
# input:load_file_rootdir:动态表所在路径
# output:null
def load_file_rename(load_file_rootdir):
    originList = os.listdir(load_file_rootdir)
    print(load_file_rootdir, ":", originList)

    data_path_list = get_data_path_list(load_file_rootdir)

    afterlist = get_rename_afterlist(data_path_list)

    for i in range(0, len(originList)):
        before = os.path.join(load_file_rootdir, originList[i])
        after = os.path.join(load_file_rootdir, str(afterlist[i]).replace(':', '-'))
        os.rename(before, after)

    print("动态表重命名………………………………OK")


# 校验动态表的列表名是否有异常，防止出现之前部分动态表错位的情况
# input:dynamic_file_path:动态表路径
# output:null
def vertify_column_name(dynamic_file_path):
    data_path_list = get_data_path_list(dynamic_file_path)
    correct_column_name_list = ["时间", "小区CGI", "有效RRC连接平均数(次)", "E-RAB建立成功数(个)", "空口上行业务字节数(KByte)", "空口下行业务字节数(KByte)",
                                "上行PRB平均利用率(%)", "下行PRB平均利用率(%)"]

    flag = 0

    for data_path in data_path_list:
        with open(data_path, 'r', encoding='GBK') as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)

            for line in it:
                name_list = [line[0], line[5], line[12], line[13], line[14], line[15], line[19], line[20]]

                if name_list != correct_column_name_list:
                    print("动态表文件", data_path, "列名损坏，程序退出……")
                    flag = 1
                    exit()
                break

    if flag == 0:
        print("动态表文件列名校验………………………………OK")


def fre_no_list2str(fre_no_list):
    fre_no_str = fre_no_list[0]
    del (fre_no_list[0])
    while len(fre_no_list) != 0:
        fre_no_str += "," + fre_no_list[0]
        del (fre_no_list[0])
    return fre_no_str


def get_merge_sector_cgi_dic(merge_static_path):
    # merge_static_path是合并后的静态表的路径
    # 合并静态表的格式为：扇区名，频段1，频段1CGI编号，频段2，频段2CGI编号...
    merge_sector_cgi_dic = {}
    with open(merge_static_path, "r", encoding="GBK") as csvfile:
        reader = csv.reader(csvfile)
        it = iter(reader)

        for line in it:
            sector_name = line[0]
            merge_sector_cgi_dic[sector_name] = []
            for i in range(1, len(line), 2):
                if "#" not in line[i + 1]:
                    merge_sector_cgi_dic[sector_name].append(line[i + 1])
                else:
                    split_no_list = line[i + 1].split("#")
                    for tmp_no in split_no_list:
                        merge_sector_cgi_dic[sector_name].append(tmp_no)

    return merge_sector_cgi_dic


# 在静态表中根据列名获取列下标
# 19.11.20加入对动态表调用该函数获取下标
# 目前仅在静态表中使用，因为动态表运行前会先调用vertify_column_name校验动态表的列名
def get_index_no(file_name, title_list, target):
    if target not in title_list:
        print("文件", file_name, "数据错误，表中无", target, "列，程序终止！")
        exit()
    return title_list.index(target)


# 在动态表中根据列表列表获取下标列表
def get_index_list(file_name, title_list, target_name_list):
    index_list = []
    for column_name in target_name_list:
        if column_name not in title_list:
            print("文件", file_name, "数据错误，表中无", column_name, "列，程序终止！")
            exit()
        index_list.append(title_list.index(column_name))
    return index_list


# 从静态表中读扇区名和CGI之间的对应关系
# input:static_file_path:静态表路径; sector_name_column_index:扇区名所在列的下标，默认为6；
#       CGI_index_start：CGI所在列开始的下标；CGI_index_end：CGI所在列结束的下标
# output:sector_cgi_dic:字典，key=扇区名，value=CGI列表
def read_sector_cgi_dic(static_file_path, merge_static_path, cgi_prb_dic,
                        delete_ele_list=["GSM900", "DCS1800", "NB", ""],
                        cgi_no_column_list=['F1', 'F2', 'A', 'D1', 'D2', 'D3', 'E1', 'E2', 'E3', 'F/D/E', 'FDD-900',
                                            'FDD-1800']):
    merge_sector_cgi_dic = get_merge_sector_cgi_dic(merge_static_path)
    sector_name_column_index = -1
    all_com_freq_index = -1
    sector_cgi_dic = {}
    sector_num_dic = {}
    sector_fre_no_dic = {}
    cgi_info_dic = {}

    # 用来对prb配置表中没找到的cgi编号的情况进行计数
    counter=0
    all_num=0

    with open(static_file_path, 'r', encoding="GBK") as csvfile:
        reader = csv.reader(csvfile)
        for i, rows in enumerate(reader):
            if i == 0:
                title_list = rows

                # 杭州的静态表中，扇区中文名所在列的列名为：小区中文名称
                # sector_name_column_index=get_index_no(static_file_path, title_list, "小区中文名称")
                # 达州的静态表中，扇区中文名所在列的列名为：扇区中文名称
                sector_name_column_index = get_index_no(static_file_path, title_list, "扇区中文名称")

                all_com_freq_index = get_index_no(static_file_path, title_list, "全量共址频段")
                cgi_no_index_list = get_index_list(static_file_path, title_list, cgi_no_column_list)
                break

    with open(static_file_path, 'r', encoding="GBK") as csvfile:
        reader = csv.reader(csvfile)
        it = iter(reader)
        next(it)
        for line in it:
            # 杭州地区：只选取拱墅区的扇区
            # if line[1]!="拱墅":
            #     continue

            # 防止出现静态表最后有空行的情况
            if line[sector_name_column_index] == "":
                continue

            # 排除扇区名中带有MIMO的扇区
            if line[sector_name_column_index].lower().find('mimo') >= 0:
                continue

            freq_no_list = line[all_com_freq_index].split(",")

            # 达州的静态表中在“全量共址频段”中出现了FDD900M,FDD1800M的频段，要讲后面的M去掉
            freq_no_list = ["FDD-900" if ele in ["FDD900M", "FDD900"] else ele for ele in freq_no_list]
            freq_no_list = ["FDD-1800" if ele in ["FDD1800M", "FDD1800"] else ele for ele in freq_no_list]

            for ele in delete_ele_list:
                while ele in freq_no_list:
                    freq_no_list.remove(ele)

            if len(freq_no_list) == 0:
                continue

            sector_num_dic[line[sector_name_column_index]] = len(freq_no_list)
            sector_fre_no_dic[line[sector_name_column_index]] = fre_no_list2str(freq_no_list)

            # 由于合并后的静态表必定包括最近一次的静态表，所以在读最新的静态表的扇区名时，肯定均能在合并的静态表中找到扇区名对应的CGI清单
            sector_cgi_dic[line[sector_name_column_index]] = merge_sector_cgi_dic[line[sector_name_column_index]]

            # 将sector_cgi_dic中扇区名对应0小区的扇区给删掉
            if len(sector_cgi_dic[line[sector_name_column_index]]) == 0:
                sector_cgi_dic.pop(line[sector_name_column_index])
                continue

            # 搭建cgi_info的框架
            for col_index in cgi_no_index_list:
                cgi_no=line[col_index]
                if cgi_no=="":
                    continue
                if '#' not in cgi_no:

                    # 达州静态表：在FDD-900、FDD-1800列的值为FDD900、FDD1800，要将其改成FDD-900、FDD-1800
                    if cgi_no == "FDD900":
                        cgi_no = "FDD-900"
                    elif cgi_no == "FDD1800":
                        cgi_no = "FDD-1800"

                    cgi_name=line[col_index+1]
                    if cgi_name in cgi_prb_dic:
                        prb_avil_num=cgi_prb_dic[cgi_name]
                        all_num+=1
                    else:
                        prb_avil_num=100
                        counter+=1
                        all_num+=1
                    tmp_value=CGI_Value(cgi_no, prb_avil_num, line[sector_name_column_index])
                    cgi_info_dic[cgi_name]=tmp_value
                else:
                    split_no_list = cgi_no.split('#')
                    cgi_name=line[col_index+1]
                    split_name_list = cgi_name.split('#')
                    for split_index in range(0, len(split_no_list)):
                        if split_name_list[split_index] in cgi_prb_dic:
                            prb_avil_num = cgi_prb_dic[split_name_list[split_index]]
                            all_num += 1
                        else:
                            prb_avil_num = 100
                            counter += 1
                            all_num += 1
                        tmp_value = CGI_Value(split_no_list[split_index], prb_avil_num, line[sector_name_column_index])
                        cgi_info_dic[split_name_list[split_index]] = tmp_value

    print("静态表中涉及的CGI编号数共", all_num, "个，其中在prb配置表中找不到对应prb的CGI编号共", counter, "个！此情况下prb可用数设为100.")

    return sector_cgi_dic, sector_num_dic, sector_fre_no_dic, cgi_info_dic


# 根据动态表路径根目录获取该目录下所有动态表的路径列表
# input:dynamic_file_path:动态表根目录
# output:data_path_list:所有动态表路径列表
def get_data_path_list(dynamic_file_path):
    originList = os.listdir(dynamic_file_path)
    data_path_list = []

    for i in range(0, len(originList)):
        data_path_list.append(os.path.join(dynamic_file_path, originList[i]))
    return data_path_list


# 从小区资源静态表中读取每个cgi的prb可用数是多少
def get_cgi_prb_dic(prb_static_file_path):
    cgi_prb_dic = {}
    print("Reading……", prb_static_file_path)
    prb_static_file = open(prb_static_file_path, encoding="GBK")
    prb_static_df = pd.read_csv(prb_static_file)
    (len_row, len_col) = prb_static_df.shape
    for row_index in range(0, len_row):

        # 杭州的Prb_Static.csv的CGI编号所在列的列名为：CGI; prb可用数所在列的列名为：上行PRB可用数
        # cgi_name=prb_static_df["CGI"][row_index]
        # prb_avil=prb_static_df["上行PRB可用数"][row_index]

        # 达州的Prb_Static.csv的CGI编号所在列的列名为：小区CGI; prb可用数所在列的列名为：PRB可用数
        cgi_name = prb_static_df["小区CGI"][row_index]
        prb_avil = prb_static_df["PRB可用数"][row_index]

        if prb_avil == "未知":
            continue
        cgi_prb_dic[cgi_name] = float(prb_avil)
    return cgi_prb_dic


# 读动态表，读取所有动态表并构成一个大字典
# input:dynamic_file_path:动态表根路径；attr_load_index_list:六个属性在动态表中所在列；cgi_index：cgi下标；time_index：时间下标
# output:CGITime_Load_dic:字典，key=(cgi,time)，value=六个属性的负载列表
def read_cgi_load_dic(dynamic_file_path, cgi_info_dic):
    CGITime_Load_dic = {}
    highload_record_list = []
    abnormal_record_list=[]
    data_path_list = get_data_path_list(dynamic_file_path)
    attr_load_column_list = ["有效RRC连接平均数(次)", "E-RAB建立成功数(个)", "空口上行业务字节数(KByte)", "空口下行业务字节数(KByte)",
                             "上行PRB平均利用率(%)", "下行PRB平均利用率(%)"]

    for data_file_path in data_path_list:
        print("Reading……", data_file_path)
        with open(data_file_path, 'r', encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            for i, rows in enumerate(reader):
                if i == 0:
                    title_list = rows
                    attr_load_index_list = get_index_list(data_file_path, title_list, attr_load_column_list)
                    cgi_index = get_index_no(data_file_path, title_list, "小区CGI")
                    time_index = get_index_no(data_file_path, title_list, "时间")
                    break

        with open(data_file_path, 'r', encoding="GBK") as csvfile:
            reader = csv.reader(csvfile)
            it = iter(reader)
            next(it)

            for line in it:
                cgi = line[cgi_index]
                time = line[time_index]
                load = []
                for index in attr_load_index_list:
                    load.append(line[index])
                CGITime_Load_dic[(cgi, time)] = load

                if cgi in cgi_info_dic:
                    cgi_info_dic[cgi].time_load_dic[time]=load

                if is_CGI_highLoad_real(load)==True:
                    if cgi in cgi_info_dic:
                        sector_name=cgi_info_dic[cgi].belong_sector

                        # 由于在构建cgi_info_dic时已经将名字中带有mimo的扇区跳过了，所以在该条件下的cgi均添加到highload_record_list中
                        freq_no=cgi_info_dic[cgi].fre_band_No
                        highload_record_list.append([time,cgi,sector_name,freq_no])
                    else:
                        abnormal_record_list.append([time,cgi,"共参表中无对应小区"])

    return CGITime_Load_dic, cgi_info_dic, highload_record_list, abnormal_record_list


# 生成包含动态表全部时间的列表
# input:start_date:动态表开始时间，格式为yyyy-mm-dd hh:mm; num_days:动态表的天数
# 从start_date的零点开始生成
def generate_time_list(start_date, num_days):
    # start_date的格式为 2018-12-08 00:00，days为天数，默认从start_date的零点开始生成
    year = int(start_date[0:4])
    month = int(start_date[5:7])
    day = int(start_date[8:10])
    time_list = []

    for hour in range(0, 24):
        time = str(year).zfill(4) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + " " + str(hour).zfill(
            2) + ":00"
        time_list.append(time)

    num_days -= 1

    while num_days > 0:
        day += 1
        if day > calendar.monthrange(year, month)[1]:
            day = 1
            month += 1
            if month > 12:
                month = 1
                year += 1

        for hour in range(0, 24):
            time = str(year).zfill(4) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + " " + str(hour).zfill(
                2) + ":00"
            time_list.append(time)

        num_days -= 1

    return time_list


def get_sum_prb_avil(fre_no):
    fre_list = fre_no.split(",")
    sum_prb_avil = 0
    for i in fre_list:
        if i in ["D1", "D2", "D3", "D", "F1", "E1", "E2", "E"]:
            sum_prb_avil += 100
        elif i in ["A", "FDD-1800"]:
            sum_prb_avil += 75
        elif i in ["F2", "E3"]:
            sum_prb_avil += 50
        elif i in ["FDD-900"]:
            sum_prb_avil += 25

    return sum_prb_avil


# 计算扇区的负载：将每个扇区绑定的CGI的六个指标分别进行加和
# 以扇区为单位保存每个小时六个指标的值
def calculate_sector_load(time_list, clean_file_path, cgi_prb_dic, sector_cgi_dic, sector_num_dic, sector_fre_no_dic,
                          CGITime_Load_dic, attr_num=6,
                          title_list=["时间", "有效RRC连接平均数(次)", "E-RAB建立成功数(个)", "空口上行业务字节数(KByte)", "空口下行业务字节数(KByte)",
                                      "上行PUSCH PRB占用平均数(个)", "下行PDSCH PRB占用平均数(个)", "license总数", "PRB可用总数", "CGI所在频段"]):
    for sector in sector_cgi_dic:
        cgi_list = sector_cgi_dic[sector]
        time_load_dic = {}
        static_license_num = sector_num_dic[sector]
        fre_no = sector_fre_no_dic[sector]

        # 根据扇区绑定的频段，确定该扇区的PRB可用数
        sum_prb_avil = get_sum_prb_avil(fre_no)

        for cgi in cgi_list:
            # 为未出现在cgi_prb_dic的cgi初始化prb可用数为100
            if cgi not in cgi_prb_dic:
                cgi_prb_dic[cgi] = 100

        for time in time_list:
            sum_load_list = []
            for data_index in range(0, attr_num):
                tmp = 0

                if data_index in [4, 5]:
                    for cgi in cgi_list:
                        if (cgi, time) in CGITime_Load_dic:
                            if CGITime_Load_dic[(cgi, time)][data_index] == "":
                                tmp += 0
                            else:
                                tmp += float(CGITime_Load_dic[(cgi, time)][data_index]) * cgi_prb_dic[cgi] / 100
                else:
                    for cgi in cgi_list:
                        if (cgi, time) in CGITime_Load_dic:
                            tmp += float(CGITime_Load_dic[(cgi, time)][data_index])
                sum_load_list.append(tmp)
            sum_load_list.append(static_license_num)
            sum_load_list.append(sum_prb_avil)
            sum_load_list.append(fre_no)
            time_load_dic[time] = sum_load_list

        # 由于扇区名中存在有'/'字符的情况，例如'测试大厅C频段B39\(256QAM\)'，出现这种情况的时候无法使用扇区名保存文件
        # 此处将扇区名中的反斜杠去掉
        sector = sector.replace("\\", "", len(sector))
        filename = os.path.join(clean_file_path, sector + '.csv')
        save_dic2file(time_load_dic, filename, title_list)

        print("文件", sector + ".csv", "已保存")


# 将字典保存成csv文件，保存的字典key是字符串，value是一个列表。保存格式是[key]+value
# input:saving_dic:要保存的字典；filename：要保存的路径；title_list：保存的csv文件的标题
def save_dic2file(saving_dic, filename, title_list):
    with open(filename, "w", newline='', encoding="GBK") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(title_list)

        for key in saving_dic:
            saving_dic[key].insert(0, key)
            writer.writerow(saving_dic[key])
