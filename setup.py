#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: lijin
# Mail: lijin@dingtalk.com
# Created Time:  2019-09-05
#############################################


from setuptools import setup, find_packages		# 没有这个库的可以通过pip install setuptools导入

setup(
    name = "allinpay",
    version = "0.0.3",
    keywords = ("pip", "pathtool","timetool", "magetool", "mage"),							
    description = "通联支付python工具",
    long_description = "通联支付python工具",
    license = "MIT Licence",

    url = "https://github.com/l616769490/allinapy",
    author = "lijin",
    author_email = "lijin@dingtalk.com",

    packages = find_packages(),											# 导入目录下的所有__init__.py包
    include_package_data = True,
    platforms = "any",
    install_requires = []
)