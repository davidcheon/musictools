#!/usr/bin/python
#!_*_ coding:utf-8 _*_
from distutils.core import setup
import py2exe

#data_files= [('static',glob('static/*.*')),]
includes = []
excludes = []
packages = ['wx.lib.pubsub',]
dll_excludes = ['MSVCP90.dll',]

setup(
	options = {'py2exe':{'includes':includes,
						'excludes':excludes,
						'dll_excludes':dll_excludes,
						'packages':packages,}},
	windows=[{'script':'gui.py'}])
