# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File: Node.py
  Desc: 节点类
  Author: CoderPig
  Date: 2020/3/19 0022 14:46
-------------------------------------------------
"""


class Node:
    def __init__(self, widget=None, id=None, kv=None):
        self.widget = widget
        self.id = id
        self.kv = kv
