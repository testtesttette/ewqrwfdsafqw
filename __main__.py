import __config__ as cf
from __global__ import GlobalVariables


# TODO：全局变量定义在下面
cf.init()

cf.glv_set(GlobalVariables.static_file_path, r'/home/wm775825/达州-0512-0624-数据/静态表/0512-更新-静态表.csv')
cf.glv_set(GlobalVariables.dynamic_data_dir, r'')
cf.glv_set(GlobalVariables.exclude_sectors_file_path, r'')

# TODO：根目录名字？
cf.glv_set(GlobalVariables.output_root_dir, r'')
cf.glv_set(GlobalVariables.plus_sectors_dir, r'plus')
cf.glv_set(GlobalVariables.reduce_sectors_dir, r'reduce')
cf.glv_set(GlobalVariables.translation_sectors_dir, r'translate')
cf.glv_set(GlobalVariables.scheduel_list_dir, r'schedule')

# TODO：这些时间相关的参数从输入得到还是从csv中读出？
cf.glv_set(GlobalVariables.start_time, '')
cf.glv_set(GlobalVariables.forecast_start_time, '')
cf.glv_set(GlobalVariables.forecast_day_length, 0)

cf.glv_set(GlobalVariables.reduce_volume_factor, 1.0)


def complete_config():
    """
    TODO: 根据传入的参数完善相关配置
    :return:
    """
    cf.glv_set(GlobalVariables.static_file_path, r'/home/wm775825/input/0715_Static_Origin.csv')
    cf.glv_set(GlobalVariables.exclude_sectors_file_path, r'/home/wm775825/input/GS_exclude_sector_0715.csv')

    cf.glv_set(GlobalVariables.output_root_dir, r'/home/wm775825/output/')

    cf.glv_set(GlobalVariables.start_time, '')
    cf.glv_set(GlobalVariables.forecast_start_time, '2019-08-02 00:00')
    cf.glv_set(GlobalVariables.forecast_day_length, 7)


def main():
    complete_config()
    # TODO：程序运行时，需要开辟一个新文件夹?
    # TODO：考虑从命令行接受参数，还是硬编码好需要的所有数据的layout?
    # TODO：依次调用各个子包下的入口函数
    # TODO：入口函数名不强制命名为main，可根据模块功能来
    # TODO：具体模块的导入要在complete_config函数后边
    from schedule.schedule import sche
    sche()


if __name__ == '__main__':
    main()
