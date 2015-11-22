#!/usr/bin/python
#!_*_ coding:utf-8 _*_
import urllib2
import os
import re
import threading
import time
import sys
class myexception(Exception):pass
class searchanddownload(object):
	SEARCH_URL='http://www.zoa123.com/search.php?q=%s'
	SEARCH_URL2='http://www.zoa123.com/search_song.php?q=%s'
	DOWNLOAD_URL='http://mp3.zoa123.com/?id=%s'
	def __init__(self):
		self.songs=None
		self.title_pattern=re.compile(r'<td\sclass="track".*?title="(.*?)"')
		self.id_pattern=re.compile(r'<a href="([^"]+)"\stitle="(?:[^"]+)"\sclass="sp song_mp3"')
	def search(self,searchname,more=False):
		self.searchname=urllib2.quote(searchname)
		if not more:
			content=urllib2.urlopen(searchanddownload.SEARCH_URL%self.searchname).read()
		else:
			content=urllib2.urlopen(searchanddownload.SEARCH_URL2%self.searchname).read()
		titles=self.title_pattern.findall(content)
		titles=[title.strip(' ') for title in titles]
		ids=self.id_pattern.findall(content)
		ids=[id.strip('# ') for id in ids]
		self.songs=zip(titles,ids)
		return self.songs
	def getsonglist(self):
		if self.songs is not None:
			return (True,self.songs)
		else:
			return (False,u'no find songs')
	def download(self,selections):
		path=os.path.join('result',urllib2.unquote(self.searchname))
		if not os.path.exists(path):
			os.mkdir(path)
		for n in selections:
			title=self.songs[n][0]
			id=self.songs[n][1]
			filename=os.path.join(path,title)
			if not os.path.exists(filename):
				url=searchanddownload.DOWNLOAD_URL%id
				t=downloadthread(url,title,filename)
				t.start()

	def downloadforgui(self,selections):
		path=os.path.join('result',urllib2.unquote(self.searchname))
		if not os.path.exists(path):
			os.mkdir(path)
		for n in selections:
			title=self.songs[n][0]
			id=self.songs[n][1]
			filename=os.path.join(path,title)
			if not os.path.exists(filename):
				url=searchanddownload.DOWNLOAD_URL%id
				with open(filename,'wb+') as f:
					content=urllib2.urlopen(url).read()
					f.writelines(content)
	def downloadsingle(self,selection):
		try:
			path=os.path.join('result',urllib2.unquote(self.searchname))
			if not os.path.exists(path):os.mkdir(path)
			title=self.songs[selection][0]
			title=title.replace('/','-')
			id=self.songs[selection][1]
			filename=os.path.join(path,title)
			if not os.path.exists(filename):
				url=searchanddownload.DOWNLOAD_URL%(id)
				with open(filename,'wb+') as f:
					content=urllib2.urlopen(url).read()
					f.writelines(content)
				return True,'download <%s> succeed.'%(title)
			else:
				return False,'you had downloaded selected songs'
		except Exception,e:
			return False,str(e)
class downloadthread(threading.Thread):
	def __init__(self,url,title,filename):
		threading.Thread.__init__(self)
		self.url=url
		self.title=title
		self.filename=filename
	def run(self):
		with open(self.filename,'wb+') as f:
			content=urllib2.urlopen(self.url).read()
			f.writelines(content)
if __name__=='__main__':
	sd=searchanddownload()
	sd.search(sys.argv[1])
	sd.downloadsingle(0)
