from Data_Preprocessing_Lib import *

# 对TDD+A+FDD频段的数据进行清洗
# 通过读取合并的静态表来计算扇区的负载的方式不能再区分TDD，A，FDD
# 由于之前对FDD单独清洗发现FDD是有规律的，所以没必要将频段分为TDD和FDD进行处理


if __name__ == "__main__":
    # 静态表根目录
    STATIC_DIR_PATH = r"C:\Users\USTC\Desktop\合并测试\静态表"

    # 合并的静态表的文件路径
    MERGE_STATIC_PATH = r"C:\Users\USTC\Desktop\合并测试\DZ_Merge_Static.csv"

    # 合并静态表
    merge_static_dic = get_merge_static_dic(STATIC_DIR_PATH)
    save_merge_static_dic(merge_static_dic, MERGE_STATIC_PATH)

    # 静态表文件路径
    STATIC_FILE_PATH = r"C:\Users\USTC\Desktop\合并测试\静态表\0512-更新-静态表.csv"

    # 小区资源静态表文件路径
    PRB_STATIC_FILE_PATH = r"C:\Users\USTC\Desktop\合并测试\Prb_Static.csv"

    # 所有动态表文件所在的文件夹的路径
    DYNAMIC_FILE_PATH = r"C:\Users\USTC\Desktop\合并测试\动态表"

    # 保存每个扇区清洗结果的路径
    CLEAN_FILE_PATH = r"C:\Users\USTC\Desktop\合并测试\Sector_Clean"

    # 保存每个扇区的小区的负载数据结果的路径
    SAVE_CGI_INFO_PATH=r"C:\Users\USTC\Desktop\合并测试\CGI_Clean"

    # 保存高负荷记录和不能解决的高负荷记录的路径
    SAVE_PATH_HIGHLOAD = r"C:\Users\USTC\Desktop\合并测试\DZ_0512_0624_highload_cgi_list.csv"
    SAVE_PATH_ABNORMAL = r"C:\Users\USTC\Desktop\合并测试\DZ_0512_0624_abnormal_cgi_list.csv"

    # 对所有动态表重命名为 该表的开始时刻.csv，保证系统按照时间顺序读取动态表
    load_file_rename(DYNAMIC_FILE_PATH)

    # 校验动态表中是否包含本程序需要的字段
    # vertify_column_name(DYNAMIC_FILE_PATH)

    # 读取PRB配置表，获得key=cgi编号，value=prb可用数的字典
    cgi_prb_dic = get_cgi_prb_dic(PRB_STATIC_FILE_PATH)

    # 读取静态表，获得
    # 1. sector_cgi_dic：字典，扇区绑定的CGI列表
    # 2. sector_num_dic：字典，在静态表中每个扇区有多少license
    # 3. sector_fre_no_dic：字典，每个扇区绑定的频段
    sector_cgi_dic, sector_num_dic, sector_fre_no_dic, cgi_info_dic = read_sector_cgi_dic(STATIC_FILE_PATH,
                                                                                          MERGE_STATIC_PATH,
                                                                                          cgi_prb_dic,
                                                                                          delete_ele_list=["GSM900",
                                                                                                           "DCS1800",
                                                                                                           "NB",
                                                                                                           ""])

    # 读取动态表，获得
    # CGITime_Load_dic：字典，key：元组，(CGI编号,时间)；value：六个指标的值
    # 注：这里的highload_record_list, abnormal_record_list均为现网中所有动态表中的高负荷的清单
    # 但是实际高负荷的记录只需要预测的那一周即可，但是实际预测是预测那一周的高负荷情况是不知道的
    CGITime_Load_dic, cgi_info_dic, highload_record_list, abnormal_record_list= read_cgi_load_dic(DYNAMIC_FILE_PATH, cgi_info_dic)

    # 保存每个扇区的小区的负载数据结果
    save_cgi_info(sector_cgi_dic, cgi_info_dic, SAVE_CGI_INFO_PATH)

    # 保存高负荷记录和不能解决的高负荷记录
    save_record_list(highload_record_list, SAVE_PATH_HIGHLOAD, title_list=["时间", "高负荷CGI", "所在扇区", "所在频段"])
    save_record_list(abnormal_record_list, SAVE_PATH_ABNORMAL, title_list=["时间", "高负荷CGI", "无法解决高负荷的原因"])

    # 生成包含动态表中的所有小时的列表
    time_list = generate_time_list("2019-05-12 00:00", 44)

    # 将以上信息带入calculate_sector_load计算扇区负载，并将结果保存在CLEAN_FILE_PATH下
    calculate_sector_load(time_list, CLEAN_FILE_PATH, cgi_prb_dic, sector_cgi_dic, sector_num_dic, sector_fre_no_dic,
                          CGITime_Load_dic)
