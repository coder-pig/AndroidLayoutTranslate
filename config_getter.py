# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File: config_getter.py
  Desc: 获取配置信息
  Author: CoderPig
  .Date: 2020/3/20 0022 14:48
-------------------------------------------------
"""

import configparser


def get_config(section):
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf8')
    value_dict = {}
    for key in config[section]:
        value_dict[key] = config[section][key]
    return value_dict


if __name__ == '__main__':
    c = get_config('Widget')
    print(c)
