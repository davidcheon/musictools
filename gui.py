#!/usr/bin/python
#!-*- coding:utf-8 -*-
import model
import wx
import sys
import time
import threading
from wx.lib.pubsub  import Publisher
class mygui(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self,None,title=u'Music Tools')
		self.flag=True
		self.panel=wx.Panel(self,-1,style=wx.SIMPLE_BORDER)
		self.panel.SetBackgroundColour(wx.Colour(230,255,255))
		self.SetSizeHintsSz((310,410),(310,410))
		self.model=model.searchanddownload()
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

		self.searchbutton=wx.Button(self.panel,label=u'search',size=(55,30))
		self.searchbutton.Bind(wx.EVT_BUTTON,self.searchaction)
		self.searchbutton.Enable(False)
		
		self.searchmorebutton=wx.Button(self.panel,label=u'more',size=(55,30))
		self.searchmorebutton.Bind(wx.EVT_BUTTON,self.searchmoreaction)
		self.searchmorebutton.Enable(False)

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
		self.midbox.Add(wx.StaticText(self.panel,label=u'SearchName:'),proportion=0,flag=wx.LEFT,border=1)
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
		self.boxsizer.Add(self.topbox)
		self.boxsizer.Add(self.midbox)
		self.boxsizer.Add(self.bottombox)

		self.panel.SetSizer(self.boxsizer)
		
		self.downloadedsongs=0
		Publisher.subscribe(self.getsearchresult,'searchThread')
		Publisher.subscribe(self.getdownloadresult,'downloadThread')
	def getdownloadresult(self,result):
		total=reduce(lambda a,b:a+b,[t.is_alive() for t in self.tds])
		status,msg=result.data
		if status:
			self.headcontent.SetLabel(msg)
			self.downloadedsongs+=1
		if total==0:
			self.downloadbutton.Enable(True)
			self.fullselect.Enable(True)
			self.headcontent.SetLabel(u'you downloaded %d songs'%(self.downloadedsongs))
	def getsearchresult(self,result):
		self.searchbutton.Enable(True)
		self.searchmorebutton.Enable(True)
		songs=result.data
		if len(songs)>0:
			self.downloadbutton.Enable(True)
			self.fullselect.Enable(True)
		self.headcontent.SetLabel(u'search %d songs'%(len(songs)))
		newsongs=[]
		self.newids=[]
		for song in songs:
			newsongs.append(song[0])
			self.newids.append(song[1])

		self.searchlist.SetItems(newsongs)
	
	def downloadaction(self,evt):
		selections=self.searchlist.GetChecked()
		self.downloadedsongs=0
		if len(selections)==0:
			self.showmessage(u'you should select songs first')
		else:
			self.headcontent.SetLabel(self.downloading_banner)
			self.downloadbutton.Enable(False)
			self.fullselect.Enable(False)
			self.tds=[]
			for selection in selections:
				td=downloadThread(selection,self.model)
				self.tds.append(td)
				td.start()

	def fullselectaction(self,evt):
		for n in xrange(len(self.newids)):
			self.searchlist.Check(n,check=self.flag)
		self.flag=False if self.flag else True
	def searchlistaction(self,evt):
		pass

	def changesearchname(self,evt):
		self.searchbutton.Enable(True)
		self.searchmorebutton.Enable(True)
	def searchaction(self,evt):
		searchname=self.searchname.GetValue().strip().encode('utf-8')
		if searchname=='':
			self.showmessage(u'Must enter searchname first')
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
			self.showmessage(u'Must enter searchname first')
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
		dialog=wx.ProgressDialog('Progress Show',title,progressMax,style=wx.PD_CAN_ABORT)

	def showmessage(self,msg):
		dlg=wx.MessageDialog(self.panel,str(msg),caption='Error',style=wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
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
