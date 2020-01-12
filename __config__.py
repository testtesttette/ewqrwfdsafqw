"""
一些全局变量
"""


def init():
    """
    在主模块初始化
    """
    global glv
    glv = {}


def glv_set(name, value):
    """

    :param name:
    :param value:
    :return:
    """
    try:
        glv[name] = value
    except KeyError:
        pass


def glv_get(name):
    """

    :param name:
    :return:
    """
    try:
        return glv[name]
    except KeyError:
        return 'can not find ' + name + ' in global variables!'
