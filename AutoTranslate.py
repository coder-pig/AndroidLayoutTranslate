# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File: AutoTranslate.py
  Desc: 翻译脚本
  Author: CoderPig
  Date: 2020/3/20 0022 15:46
-------------------------------------------------
"""
import os
import re

from pythonds import Stack

from Node import Node
from config_getter import get_config

input_dir = os.path.join(os.getcwd(), "input")  # 输入目录
output_dir = os.path.join(os.getcwd(), "output")  # 输出目录

# 读取配置文件
widget_list = get_config('Widget')
attribute_list = get_config('Attribute')
value_list = get_config('Value')
resource_list = get_config('Resource')

# 提取@资源值的正则
resource_pattern = re.compile(r'(@.*?)/(.*)?', re.S)


# 删除文件
def remove_file(path):
    if os.path.exists(path):
        os.remove(path)


# 判断目录是否存在，不存在则创建
def is_dir_existed(path, mkdir=True):
    if mkdir:
        if not os.path.exists(path):
            os.makedirs(path)
    else:
        return os.path.exists(path)


# 遍历构造txt路径字典(构造文件路径列表，过滤txt，拼接)
def init_txt_dict(file_dir):
    apk_path_list = list(filter(lambda fp: fp.endswith(".txt"),
                                list(map(lambda x: os.path.join(file_dir, x), os.listdir(file_dir)))))
    index_list = [str(x) for x in range(1, len(apk_path_list) + 1)]
    return dict(zip(index_list, apk_path_list))


# 检查节点是否匹配
def match_check(node_list):
    # 遍历剔除*节点
    n_list = []
    for n in node_list:
        n_format = n.widget.replace(" ", "").replace("\n", "")
        if n_format[0] != "*":
            n_list.append(n_format)
    # 定义栈，+进
    s = Stack()
    flag = True  # 标记
    for n in n_list:
        # +节点进栈
        if n[0] == "+":
            s.push(n)
        else:
            # 没有+节点，第一个就是-，直接错误
            if s.isEmpty():
                flag = False
            else:
                # 获取栈顶+节点
                top = s.pop()
                # 如果和-节点匹配则正确，否则错误
                if n[1:] == top[1:]:
                    flag = True
                else:
                    return False
    if flag and s.isEmpty():
        return True
    else:
        return False


# 读取节点列表
def read_node_list(file_path):
    node_list = []
    file = open(file_path)
    for line in file:
        # 去掉空格
        line_after = line.replace(" ", "")
        # 如果是关标签，直接写入
        if line_after[0] == "-":
            node_list.append(Node(line_after))
        # 不是关标签，提取标签，id和属性值
        else:
            split_list = line_after.replace(" ", "").split(">")
            if len(split_list) == 1:
                exit("节点提取失败 => %s" % split_list[0])
            elif len(split_list) >= 3:
                attr_value_list = []
                for v in range(2, len(split_list)):
                    attr_value_list.append(split_list[v])
                node_list.append(Node(split_list[0], split_list[1], attr_value_list))
    file.close()
    return node_list


# 解析转换节点
def analysis_node(node):
    node_result = ""
    widget = node.widget
    # 判断是否为标签
    if widget[0] not in "+-*":
        exit("结点类型有误 => %s" % node.widget)
    else:
        widget_format = widget[1:].replace("\n", "")
        # 判断是否包含此控件
        if widget_format not in widget_list:
            exit("找不到控件 => %s" % widget_format)
        else:
            # 判断是否为闭合节点
            if value.widget[0] == "-":
                node_result += "</%s>\n" % widget_list[widget_format]
            else:
                node_result += "<" + widget_list[widget_format] + "\n"
                # 判断是否为首个根节点，需加上xmlns
                if index == 0:
                    node_result += 'xmlns:android="http://schemas.android.com/apk/res/android"\n'
                    node_result += 'xmlns:app="http://schemas.android.com/apk/res-auto"\n'
                # 读取id
                node_result += 'android:id="@+id/%s"\n' % node.id
                # 读取属性
                for kv in node.kv:
                    # 通过 - 对字符串进行切片
                    kv_split = kv.replace("\n", "").split("-")
                    # 切片长度==1，说明没有分隔符
                    if 1 == len(kv_split):
                        # 判断是否在属性集合中，没有直接填充
                        if kv_split[0] in attribute_list:
                            node_result += "%s\n" % attribute_list[kv_split[0]]
                        else:
                            node_result += kv_split[0] + '\n'
                    else:
                        if kv_split[0] in attribute_list:
                            node_result += '%s="' % attribute_list[kv_split[0]]
                            # 判断值是否为数字，是自动加上dp
                            v = kv_split[1]
                            if v.isdigit():
                                node_result += '%sdp"\n' % v
                            else:
                                # 判断值是否为@资源类型
                                result = resource_pattern.search(v)
                                if result is not None:
                                    node_result += '%s/%s"\n' % (resource_list[result.group(1)], result.group(2))
                                else:
                                    if kv_split[1] in value_list.keys():
                                        node_result += value_list[kv_split[1]] + "\n"
                                    else:
                                        node_result += kv_split[1] + '"\n'
                        else:
                            exit("属性%s不存在" % kv_split[0])
                # 添加结尾标记节点提取失败
                if value.widget[0] == "+":
                    node_result += ">\n"
                else:
                    node_result += "/>\n"
    return node_result


def write_file(path, content):
    with open(path, 'a+') as f:
        f.write(content + '\n')


if __name__ == '__main__':
    is_dir_existed(input_dir)
    is_dir_existed(output_dir)
    print("遍历当前目录下所有文件...")
    txt_file_dict = init_txt_dict(input_dir)
    print("遍历完毕...\n\n============ 当前目录下所有的TXT ============\n")
    for (k, v) in txt_file_dict.items():
        print("%s.%s" % (k, v.split(os.sep)[-1]))
    print("\n%s" % ("=" * 45))
    choice_pos = input("%s" % "请输入需要翻译的txt的数字编号：")
    print("=" * 45, )
    choice_txt = txt_file_dict.get(choice_pos)
    txt_name = choice_txt.split(os.sep)[-1][:-4]  # 文件名
    remove_file(os.path.join(output_dir, "%s.xml" % txt_name))  # 删除文件
    output_txt_path = os.path.join(output_dir, "%s.xml" % txt_name)
    nodes = read_node_list(choice_txt)
    if not match_check(nodes):
        exit("节点匹配有误")
    else:
        for index, value in enumerate(nodes):
            nw = analysis_node(value)
            write_file(output_txt_path,nw)
    print("文件生成成功，路径 => %s" % output_txt_path)