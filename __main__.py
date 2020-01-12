import __config__ as cf

# TODO：需要的全局变量全都定义在下面
# TODO：以下待定：
# TODO：文件路径的变量尽量用path结尾
# TODO：目录路径的变量尽量用dir结尾
cf.init()
cf.glv_set('static_file_path', 'qwe')
cf.glv_set('dynamic_data_dir', 'ewewqeqwe')
cf.glv_set('sector_', '')


def main():
    # TODO：程序运行时，需要开辟一个新文件夹
    # TODO：考虑从命令行接受参数，还是硬编码好需要的所有数据的layout?
    # TODO：依次调用各个子包下的入口函数
    # TODO：入口函数名不强制命名为main，可根据模块功能来
    from schedule.schedule import sche
    sche()


if __name__ == '__main__':
    main()