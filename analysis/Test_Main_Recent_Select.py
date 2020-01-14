import Lib_Statistic_Tools



if __name__=="__main__":

    ##################################################################################################################################
    # 以历史数据的最后一周特征检出高负载小区（如果将最后一周设为验证集则设置为倒数第二周）

    # 输入数据：
    # 以扇区为单位保存的小区清洗数据目录
    # 指定清洗出来的以小区为粒度保存的负载信息数据的目录（属于同一扇区的小区保存在同一文件，由李启亮给出）
    src_cleaned_sector_CGI_matching_loading_dir = r'C:\projects\IFLYTEK\license\DZ_0512_0624_CGI_Clean'
    src_sector_load_dir = r'C:\projects\IFLYTEK\license\DZ_0512_0624_Sector_Clean'
    # 输出数据：
    # 拿最后一周（如果将最后一周作为验证集则平移倒数第二周负载）估计出的小区高负载情况保存目录
    overload_CGI_save_dir = r'C:\projects\IFLYTEK\license\扩容清单-基于近期负载特征优化'  # 2019-07-19~2019-07-25

    # 指定小区清洗数据的起始时间和负载数据的天数
    # 以及平移“最后一周”相对于真实数据末尾的天数：
        # 即，如果需要的预测结果是08-02~08-08，但负载数据是05-04~07-27，则平移的最后一周是07-19~07-25，相对于历史数据的末尾相差两天
    time_line_start = '2019-05-12 00:00'
    sustain_days = 44   # 一共的长度

    # 指定提取特征的最后一周落在预测结果的时刻的起始位置，例如想验证倒数第二周对最后一周高负载的影响，则before_Load_data设为7，即平移截至时间为“最后一周”之前
    recent_select_start_date = '2019-06-18 00:00'
    before_Load_data = 7



    Lib_Statistic_Tools.judge_and_save_overload_CGI(src_cleaned_sector_CGI_matching_loading_dir,
                                                    src_sector_load_dir,
                                                    overload_CGI_save_dir,
                                                    time_line_start,
                                                    sustain_days,
                                                    before_Load_data,
                                                    recent_select_start_date)

