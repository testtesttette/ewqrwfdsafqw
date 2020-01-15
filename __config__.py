"""
一些全局变量的配置接口
"""


def init():
    """
    在主模块初始化
    """
    global glv
    glv = {}


def glv_set(key, value):
    """
    set
    :param key:
    :param value:
    :return:
    """
    try:
        glv[key] = value
    except KeyError:
        pass


def glv_get(key):
    """
    get
    :param key:
    :return:
    """
    try:
        return glv[key]
    except KeyError:
        print('can not find ' + key + ' in global variables!')
        return None
