#!/usr/bin/python
#!-*- coding:utf-8 -*-
import wx
import sys
import time
import threading
import urllib2
import os
import re
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
	def search(self,searchname):
		self.searchname=urllib2.quote(searchname)
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
	def downloadforgui(self,selections):
		downloadedsongs=0
		try:
			path=os.path.join('result',urllib2.unquote(self.searchname))
			if not os.path.exists(path):
				os.mkdir(path)
			for n in selections:
				title=self.songs[n][0]
				title=title.replace('/','-')
				id=self.songs[n][1]
				filename=os.path.join(path,title)
				if not os.path.exists(filename):
					url=searchanddownload.DOWNLOAD_URL%id
					downloadedsongs+=1
					with open(filename,'wb+') as f:
						content=urllib2.urlopen(url).read()
						f.writelines(content)
		except Exception,e:
			pass
		return downloadedsongs
	def downloadsingle(self,selection):
		try:
			path=os.path.join('result',urllib2.unquote(self.searchname))
			if not os.path.exists(path):os.mkdir(path.decode('utf-8','ignore'))
			title=self.songs[selection][0]
			title=title.replace('/','-')
			id=self.songs[selection][1]
			filename=os.path.join(path,title).decode('utf-8','ignore')
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
class mygui(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self,None,title=u'Music Tools')
		self.flag=True
		self.panel=wx.Panel(self,-1,style=wx.SIMPLE_BORDER)
		self.panel.SetBackgroundColour(wx.Colour(230,255,255))
		self.SetSizeHintsSz((310,410),(310,410))
		self.model=searchanddownload()
		self.Bind(wx.EVT_CLOSE,self.closeaction)
		self.font=wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD)
		
		self.welcome_banner=u'A tools to help fa    ther\nsearch music and download'
		self.searching_banner=u'searching....'
		self.downloading_banner=u'downloading....'
		self.headcontent=wx.StaticText(self.panel,label=self.welcome_banner)
		self.headcontent.SetFont(wx.Font(10,wx.SWISS,wx.NORMAL,wx.BOLD))
		self.headcontent.SetForegroundColour(wx.Colour(255,0,0))

		self.searchname=wx.TextCtrl(self.panel,style=wx.TE_PROCESS_ENTER,size=(100,25))
		self.searchname.SetFocus()
		self.searchname.Bind(wx.EVT_TEXT_ENTER,self.searchaction)
		self.searchname.Bind(wx.EVT_TEXT,self.changesearchname)

		self.searchbutton=wx.Button(self.panel,label=u'search')
		self.searchbutton.Bind(wx.EVT_BUTTON,self.searchaction)
		self.searchbutton.Enable(False)

		self.searchlist=wx.CheckListBox(self.panel,-1,(100,100),(280,280),[],wx.LB_SINGLE)
		self.searchlist.SetBackgroundColour(wx.Colour(255,255,255))
		self.searchlist.SetAutoLayout(True)
		self.searchlist.Bind(wx.EVT_CHECKLISTBOX,self.searchlistaction)

		self.fullselect=wx.Button(self.panel,label=u'select all')
		self.fullselect.Bind(wx.EVT_BUTTON,self.fullselectaction)
		self.fullselect.Enable(False)

		self.downloadbutton=wx.Button(self.panel,label=u'download')
		self.downloadbutton.Bind(wx.EVT_BUTTON,self.downloadaction)
		self.downloadbutton.Enable(False)

		self.topbox=wx.BoxSizer()
		self.topbox.Add(self.headcontent,proportion=1,flag=wx.EXPAND|wx.ALL,border=1)

		self.midbox=wx.BoxSizer()
		self.midbox.Add(wx.StaticText(self.panel,label=u'SearchName:'),proportion=1,flag=wx.LEFT,border=5)
		self.midbox.Add(self.searchname,proportion=1,flag=wx.EXPAND|wx.ALL,border=1)
		self.midbox.Add(self.searchbutton,proportion=1,flag=wx.RIGHT,border=1)

		self.bottombox=wx.BoxSizer(orient=wx.VERTICAL)
		self.bottombox.Add(self.searchlist,proportion=1,flag=wx.EXPAND|wx.ALL,border=15)
		self.showresultbox=wx.BoxSizer()
		self.showresultbox.Add(self.fullselect,proportion=1,flag=wx.LEFT,border=60)
		self.showresultbox.Add(self.downloadbutton,proportion=1,flag=wx.RIGHT,border=60)
		self.bottombox.Add(self.showresultbox)


		self.boxsizer=wx.BoxSizer(orient=wx.VERTICAL)
		self.boxsizer.Add(self.topbox)
		self.boxsizer.Add(self.midbox)
		self.boxsizer.Add(self.bottombox)

		self.panel.SetSizer(self.boxsizer)
		
		self.downloadedsongs=0
		Publisher.subscribe(self.getsearchresult,'searchThread')
		Publisher.subscribe(self.getdownloadresult,'downloadThread')
		Publisher.subscribe(self.getdownloadupdateresult,'downloadThreadupdate')
	def getdownloadupdateresult(self,result):
		count=int(result.data)
		self.headcontent.SetLabel('you downloaded %d songs'%(count))
		self.downloadbutton.Enable(True)
		self.fullselect.Enable(True)
	def getdownloadresult(self,result):
		total=reduce(lambda a,b:a+b,[t.is_alive() for t in self.tds])
		status,msg=result.data
		if status:
			self.headcontent.SetLabel(msg.decode('utf-8','ignore'))
			self.downloadedsongs+=1
		if total==0:
			self.downloadbutton.Enable(True)
			self.fullselect.Enable(True)
			self.headcontent.SetLabel(u'you downloaded %d songs'%(self.downloadedsongs))
	def getsearchresult(self,result):
		self.searchbutton.Enable(True)
		songs=result.data
		if len(songs)>0:
			self.downloadbutton.Enable(True)
			self.fullselect.Enable(True)
		self.headcontent.SetLabel(u'search %d songs'%(len(songs)))
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
			self.showmessage(u'you should select songs first')
		else:
			self.headcontent.SetLabel(self.downloading_banner.decode('utf-8','ignore'))
			self.downloadbutton.Enable(False)
			self.fullselect.Enable(False)
#			t=downloadThreadupdate(selections,self.model)
#			t.start()
			self.tds=[]
			for selection in selections:
				td=downloadThread(selection,self.model)
				self.tds.append(td)
				time.sleep(100)
				td.start()

	def fullselectaction(self,evt):
		for n in xrange(len(self.newids)):
			self.searchlist.Check(n,check=self.flag)
		self.flag=False if self.flag else True
	def searchlistaction(self,evt):
		pass

	def changesearchname(self,evt):
		self.searchbutton.Enable(True)
	def searchaction(self,evt):
		searchname=self.searchname.GetValue().strip().encode('utf-8')
		if searchname=='':
			self.showmessage(u'Must enter searchname first')
		else:
			self.searchbutton.Enable(False)
			self.searchlist.Clear()
			self.searchlist.Refresh()
			self.headcontent.SetLabel(self.searching_banner)
			ts=searchThread(searchname,self.model)
			ts.start()
	def closeaction(self,evt):
		sys.exit(0)
	def showprogressbar(self,title):
		progressMax=100
		dialog=wx.ProgressDialog('Progress Show',title,progressMax,style=wx.PD_CAN_ABORT)

	def showmessage(self,msg):
		dlg=wx.MessageDialog(self.panel,str(msg),caption='Error',style=wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
class downloadThreadupdate(threading.Thread):
	def __init__(self,selections,model):
		threading.Thread.__init__(self)
		self.selections=selections
		self.model=model
	def run(self):
		counts=self.model.downloadforgui(self.selections)
		wx.CallAfter(self.postdata,counts)
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
	def __init__(self,searchname,model):
		threading.Thread.__init__(self)
		self.searchname=searchname
		self.model=model
	def run(self):
		songs=self.model.search(self.searchname)
		wx.CallAfter(self.postdata,songs)
	def postdata(self,songs):
		Publisher.sendMessage('searchThread',songs)
if __name__=='__main__':
	app=wx.App()
	gui=mygui()
	gui.Show()
	app.MainLoop()
