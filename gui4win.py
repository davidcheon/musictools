#!/usr/bin/python
#!-*- coding:utf-8 -*-
import wx
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
import threading
import os
import re
import urllib2
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub  import pub as Publisher
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
			return (False,u'음악 찾지못했습니다')
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
		try:
			path=os.path.join(u'음악',urllib2.unquote(self.searchname)).decode('utf-8','ignore')
			if not os.path.exists(path):
				os.mkdir(path)
			for n in selections:
				title=self.songs[n][0]
				title=title.replace('/','-')
#				try:
#					attach=urllib2.urlopen(url).headers.dict['content-disposition'].strip('"\'').rsplit('.')[-1]
#				except KeyError,e:
				attach='mp3'
				filename=os.path.join(path,title).decode('utf-8','ignore')+'.%s'%(attach)
				if not os.path.exists(filename):
					id=self.songs[n][1]
					url=searchanddownload.DOWNLOAD_URL%id
					with open(filename,'wb+') as f:
						content=urllib2.urlopen(url).read()
						f.writelines(content)
			return True,len(selections)
		except Exception,e:
			return False,str(e)
	def downloadsingle(self,selection):
		try:
			path=os.path.join(u'음악',urllib2.unquote(self.searchname))
			if not os.path.exists(path):
				os.mkdir(path.decode('utf-8','ignore'))
			title=self.songs[selection][0]
			title=title.replace('/','-')
			id=self.songs[selection][1]
			filename=os.path.join(path,title).decode('utf-8','ignore')
			print filename
			if not os.path.exists(filename):
				url=searchanddownload.DOWNLOAD_URL%(id)
				with open(filename,'wb+') as f:
					content=urllib2.urlopen(url).read()
					f.writelines(content)
					return True,u'<%s> 곡 다운됐습니다.'%(title)
			else:
				return False,u'선택하신곡은 이미 다운됐습니다.'
		except Exception,e:
			return False,str(e)
class mygui(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self,None,title=u'음악상자')
		self.flag=True
		self.panel=wx.Panel(self,-1,style=wx.SIMPLE_BORDER)
		self.panel.SetBackgroundColour(wx.Colour(230,255,255))
		self.SetSizeHintsSz((310,400),(310,400))
		self.model=searchanddownload()
		self.Bind(wx.EVT_CLOSE,self.closeaction)
		self.font=wx.Font(20,wx.SWISS,wx.NORMAL,wx.BOLD)
		
		self.welcome_banner=u'        아버지 생신축하합니다'
		self.searching_banner=u'검색중....'
		self.downloading_banner=u'다운로드중....'
		self.headcontent=wx.StaticText(self.panel,label=self.welcome_banner)
		self.headcontent.SetFont(wx.Font(10,wx.SWISS,wx.NORMAL,wx.BOLD))
		self.headcontent.SetForegroundColour(wx.Colour(255,0,0))

		self.searchname=wx.TextCtrl(self.panel,style=wx.TE_PROCESS_ENTER,size=(100,25))
		self.searchname.SetFocus()
		self.searchname.Bind(wx.EVT_TEXT_ENTER,self.searchaction)
		self.searchname.Bind(wx.EVT_TEXT,self.changesearchname)

		self.searchbutton=wx.Button(self.panel,label=u'검색',size=(55,30))
		self.searchbutton.Bind(wx.EVT_BUTTON,self.searchaction)
		self.searchbutton.Enable(False)
		
		self.searchmorebutton=wx.Button(self.panel,label=u'더보기',size=(55,30))
		self.searchmorebutton.Bind(wx.EVT_BUTTON,self.searchmoreaction)
		self.searchmorebutton.Enable(False)

		self.searchlist=wx.CheckListBox(self.panel,-1,(100,100),(280,280),[],wx.LB_SINGLE)
		self.searchlist.SetBackgroundColour(wx.Colour(255,255,255))
		self.searchlist.SetAutoLayout(True)
		self.searchlist.Bind(wx.EVT_CHECKLISTBOX,self.searchlistaction)

		self.fullselect=wx.Button(self.panel,label=u'전체선택')
		self.fullselect.Bind(wx.EVT_BUTTON,self.fullselectaction)
		self.fullselect.Enable(False)

		self.downloadbutton=wx.Button(self.panel,label=u'다운로드')
		self.downloadbutton.Bind(wx.EVT_BUTTON,self.downloadaction)
		self.downloadbutton.Enable(False)

		self.topbox=wx.BoxSizer()
		self.topbox.Add(self.headcontent,proportion=1,flag=wx.EXPAND|wx.ALL,border=1)

		self.midbox=wx.BoxSizer()
		self.midbox.Add(wx.StaticText(self.panel,label=u'가수이름:'),proportion=0,flag=wx.LEFT,border=1)
		self.midbox.Add(self.searchname,proportion=1,flag=wx.EXPAND|wx.ALL,border=1)
		self.midbox.Add(self.searchbutton,proportion=0,flag=wx.RIGHT,border=1)
		self.midbox.Add(self.searchmorebutton,proportion=0,flag=wx.RIGHT,border=1)

		self.bottombox=wx.BoxSizer(orient=wx.VERTICAL)
		self.bottombox.Add(self.searchlist,proportion=1,flag=wx.EXPAND|wx.ALL,border=15)
		self.showresultbox=wx.BoxSizer()
		self.showresultbox.Add(self.fullselect,proportion=1,flag=wx.LEFT,border=60)
		self.showresultbox.Add(self.downloadbutton,proportion=1,flag=wx.RIGHT,border=60)
		self.bottombox.Add(self.showresultbox)


		self.boxsizer=wx.BoxSizer(orient=wx.VERTICAL)
		self.boxsizer.Add(self.topbox,proportion=0)
		self.boxsizer.Add(self.midbox,proportion=0)
		self.boxsizer.Add(self.bottombox,proportion=1)

		self.panel.SetSizer(self.boxsizer)
		
		self.downloadedsongs=0
		self.downloading=False
		Publisher.subscribe(self.getsearchresult,'searchThread')
		Publisher.subscribe(self.getdownloadresult,'downloadThread')
		Publisher.subscribe(self.getdownloadresultupdate,'downloadThreadupdate')
	def getdownloadresult(self,result):
		total=reduce(lambda a,b:a+b,[t.is_alive() for t in self.tds])
		status,msg=result.data
		if status:
			self.headcontent.SetLabel(msg.decode('utf-8','ignore'))
			self.downloadedsongs+=1
		if total==0:
			self.downloadbutton.Enable(True)
			self.fullselect.Enable(True)
			self.headcontent.SetLabel(u'이미 %d 곡 다운됐습니다 .'%(self.downloadedsongs))
	def getdownloadresultupdate(self,result):
		self.downloading=False
		status,msg=result.data
		if status:
			self.headcontent.SetLabel(u'당신은 %d 곡 다운됐습니다.'%(int(msg)))
		else:
			self.headcontent.SetLabel(u'실패:%s'%msg)
		self.downloadbutton.Enable(True)
		self.fullselect.Enable(True)
		self.searchbutton.Enable(True)
		self.searchmorebutton.Enable(True)
	def getsearchresult(self,result):
		self.searchbutton.Enable(True)
		self.searchmorebutton.Enable(True)
		songs=result.data
		if len(songs)>0:
			self.downloadbutton.Enable(True)
			self.fullselect.Enable(True)
		self.headcontent.SetLabel(u'%d 곡 음악 찾았습니다. '%(len(songs)))
		newsongs=[]
		self.newids=[]
		for song in songs:
			newsongs.append(song[0].decode('utf-8','ignore'))
			self.newids.append(song[1])

		self.searchlist.SetItems(newsongs)
	
	def downloadaction(self,evt):
		selections=self.searchlist.GetChecked()
		self.downloadedsongs=0
		if len(selections)==0:
			self.showmessage(u'미리 음악을 선택하셔야합니다.')
		else:
			self.downloading=True
			self.headcontent.SetLabel(self.downloading_banner)
			self.downloadbutton.Enable(False)
			self.fullselect.Enable(False)
			self.searchbutton.Enable(False)
			self.searchmorebutton.Enable(False)
			
			td=downloadThreadupdate(selections,self.model)
			td.start()
#			self.tds=[]
#			for selection in selections:
#				td=downloadThread(selection,self.model)
#				self.tds.append(td)
#				td.start()

	def fullselectaction(self,evt):
		for n in xrange(len(self.newids)):
			self.searchlist.Check(n,check=self.flag)
		self.flag=False if self.flag else True
	def searchlistaction(self,evt):
		pass

	def changesearchname(self,evt):
		if not self.downloading:
			self.searchbutton.Enable(True)
			self.searchmorebutton.Enable(True)
	def searchaction(self,evt):
		searchname=self.searchname.GetValue().strip().encode('utf-8')
		if searchname=='':
			self.showmessage(u'미리미리 가수이름을 입력하셔야.')
		else:
			self.searchbutton.Enable(False)
			self.searchmorebutton.Enable(False)
			self.searchlist.Clear()
			self.searchlist.Refresh()
			self.headcontent.SetLabel(self.searching_banner)
			ts=searchThread(searchname,self.model)
			ts.start()
	def searchmoreaction(self,evt):
		self.searchlist.Clear()
		searchname=self.searchname.GetValue().strip().encode('utf-8')
		if searchname=='':
			self.showmessage(u'미리미리 가수이름을 입력하셔야.')
		else:
			self.searchbutton.Enable(False)
			self.searchmorebutton.Enable(False)
			self.searchlist.Clear()
			self.searchlist.Refresh()
			self.headcontent.SetLabel(self.searching_banner)
			ts=searchThread(searchname,self.model,more=True)
			ts.start()
	def closeaction(self,evt):
		sys.exit(0)
	def showprogressbar(self,title):
		progressMax=100
		dialog=wx.ProgressDialog(u'진도보기',title,progressMax,style=wx.PD_CAN_ABORT)

	def showmessage(self,msg):
		dlg=wx.MessageDialog(self.panel,msg,caption='Error',style=wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
class downloadThreadupdate(threading.Thread):
	def __init__(self,selections,model):
		threading.Thread.__init__(self)
		self.selections=selections
		self.model=model
	def run(self):
		result=self.model.downloadforgui(self.selections)
		wx.CallAfter(self.postdata,result)
	def postdata(self,result):
		Publisher.sendMessage('downloadThreadupdate',result)
class downloadThread(threading.Thread):
	def __init__(self,selection,model):
		threading.Thread.__init__(self)
		self.selection=selection
		self.model=model
	def run(self):
		result=self.model.downloadsingle(self.selection)
		wx.CallAfter(self.postdata,result)
	def postdata(self,result):
		Publisher.sendMessage('downloadThread',result)
class searchThread(threading.Thread):
	def __init__(self,searchname,model,more=False):
		threading.Thread.__init__(self)
		self.searchname=searchname
		self.model=model
		self.more=more
	def run(self):
		songs=self.model.search(self.searchname,more=self.more)
		wx.CallAfter(self.postdata,songs)
	def postdata(self,songs):
		Publisher.sendMessage('searchThread',songs)

if __name__=='__main__':
	app=wx.App()
	gui=mygui()
	gui.Show()
	app.MainLoop()
