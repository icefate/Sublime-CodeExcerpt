# coding=gbk
import sublime, sublime_plugin
import os,sys
import re
import string

from ExcerptTool import ExcerptTool

#@ ���ļ�ANSI
class CodeExcerptCommand(sublime_plugin.TextCommand):

	files = None
	file_items = None
	excerpt_items = None
	currentEditObj = None

	config=sublime.load_settings("CodeExcerpt.sublime-settings")
	RES_PATH=config.get("respath")
	CHM_PATH=config.get("chmpath")

	def run(self, edit):
		if self.files == None:
			self.files = []
		if self.file_items == None:
			self.file_items = []	
		if self.currentEditObj == None:
			self.currentEditObj = edit

		if len(self.files)==0:
			self.initFiles(self.RES_PATH,".ctl")
			self.initFiles(self.CHM_PATH,".chm")
		self.view.window().show_quick_panel(self.file_items,self.on_select_file)

	#@ ��ʼ���ļ�
	def initFiles(self,path,ext):
		sfiles=os.listdir(path)
		for sf in sfiles:
			sf_fullname=os.path.join(path,sf)
			if os.path.isfile(sf_fullname):
				sfp=os.path.splitext(sf_fullname) #@ [file name without extension , file extension]
				if sfp[1].lower()==ext:
					clearfilename=sf[0:(len(sf)-len(sfp[1]))]
					if ext==".chm":
						clearfilename="[ CHM ] - "+clearfilename
						type="doc"
					else:
						type="template"
					self.files.append({"name":clearfilename,"type":type, "filename":sf,"fullfilename":sf_fullname})
					self.file_items.append(clearfilename)

	#@ ���б�ѡ���ļ� ִ��
	def on_select_file(self,picked):
		if picked == -1:
			return
		self.excerpt_items=[]
		file_selected = self.files[picked]
		if file_selected["type"]=="template":
			f=open(file_selected["fullfilename"])
			for line in f.readlines(): 
				line=line.decode(sys.getfilesystemencoding()) #@ ����
				if re.search("^#T=",line):
					self.excerpt_items.append(file_selected["name"]+"__"+line.replace("#T=",""))
			self.view.window().show_quick_panel(self.excerpt_items,ExcerptTool(self.excerpt_items,self.view,self.currentEditObj ).on_select_done)
		else:
			#@ �����chm�ļ� ���������д�
			import subprocess
			subprocess.Popen(["start /max ",file_selected["fullfilename"].encode(sys.getfilesystemencoding())],shell=True) #@ �������е������������shell=True
