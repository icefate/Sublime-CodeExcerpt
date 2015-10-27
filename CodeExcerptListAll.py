# coding=gbk
import sublime, sublime_plugin
import os,sys
import re
import string

from ExcerptTool import ExcerptTool

#@ 本文件ANSI
class CodeExcerptListAllCommand(sublime_plugin.TextCommand):

	files = None
	excerpt_items = None
	currentEditObj = None

	config=sublime.load_settings("codeexcerpt.sublime-settings")
	RES_PATH=config.get("respath")
	CHM_PATH=config.get("chmpath")

	def run(self, edit):
		if self.files == None:
			self.files = []
		if self.currentEditObj == None:
			self.currentEditObj = edit

		if self.excerpt_items == None:
			self.excerpt_items = []	
			
		if len(self.files)==0:
			self.initFiles(self.RES_PATH,".ctl")
			self.initFiles(self.CHM_PATH,".chm")
		self.view.window().show_quick_panel(self.excerpt_items,ExcerptTool(self.excerpt_items,self.view,self.currentEditObj).on_select_done)

	#@ 初始化文件 
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
				
					fitem={"name":clearfilename,"type":type, "filename":sf,"fullfilename":sf_fullname}
					self.files.append(fitem)
					self.loadExcerptByFile(fitem) 


	#@ 在列表选中文件 全部装载
	def loadExcerptByFile(self,thefitem):
		if thefitem["type"]=="template":
			f=open(thefitem["fullfilename"])
			for line in f.readlines(): 
				line=line.decode(sys.getfilesystemencoding()) #@ 解码
				if re.search("^#T=",line):
					self.excerpt_items.append(thefitem["name"]+"__"+line.replace("#T=",""))
		else :
			self.excerpt_items.append(thefitem["name"])


