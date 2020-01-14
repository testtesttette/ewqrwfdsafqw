"""
评价模型的准确率和召回率。
"""

from utils.util import get_set_from_csv, get_set_from_dir


def evaluate(*, nowadays: str, forecast: str, translate: str):
    """
    评价预测和平移的结果
    :param nowadays: 现网高负荷扇区文件/所在目录
    :param forecast: 预测高负荷扇区文件/所在目录
    :param translate: 平移高负荷扇区文件/所在目录
    :return: 高负荷预测结果评价指标：准确率，召回率。
    """
    nowadays_sectors = get_set_from_csv(csv_name=nowadays, index=0)
    forecast_sectors = get_set_from_dir(dir_name=forecast)
    translate_sectors = get_set_from_dir(dir_name=translate)
    result_sectors = forecast_sectors | translate_sectors
    intersection = nowadays_sectors & result_sectors
    assert len(nowadays_sectors) != 0
    assert len(result_sectors) != 0
    return len(intersection) / len(result_sectors), len(intersection) / len(nowadays_sectors)
