# coding=gbk
import sublime, sublime_plugin
import os,sys
import re
import string

#@ 本文件ANSI
class CodeExcerptCommand(sublime_plugin.TextCommand):

	files = None
	file_items = None
	excerpt_items = None
	currentEditObj = None

	config=sublime.load_settings("codeexcerpt.sublime-settings")
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
					self.files.append({"name":clearfilename,"type":type, "filename":sf,"fullfilename":sf_fullname})
					self.file_items.append(clearfilename)

	#@ 在列表选中文件 执行
	def on_select_file(self,picked):
		if picked == -1:
			return
		self.excerpt_items=[]
		file_selected = self.files[picked]
		if file_selected["type"]=="template":
			f=open(file_selected["fullfilename"])
			for line in f.readlines(): 
				line=line.decode(sys.getfilesystemencoding()) #@ 解码
				if re.search("^#T=",line):
					self.excerpt_items.append(file_selected["name"]+"__"+line.replace("#T=",""))
			self.view.window().show_quick_panel(self.excerpt_items,self.on_select_done)
		else:
			#@ 如果是chm文件 调用命令行打开
			import subprocess
			subprocess.Popen(["start /max ",file_selected["fullfilename"].encode(sys.getfilesystemencoding())],shell=True) #@ 用命令行的命令打开需设置shell=True

	#@ 返回选区起始行前的缩进	
	def getPreTab(self,point):
		regionSelectedFirstLine=self.view.line(point)
		#print self.view.substr(regionSelectedFirstLine)
 		m = re.match("^(\t|\s)+", self.view.substr(regionSelectedFirstLine))
		retStr=""
		if m!=None:
			retStr=m.group(0)
		return retStr

	#@ 在列表中选择素材片段 执行
	def on_select_done(self, picked):
		if picked == -1:
			return 
		item = self.excerpt_items[picked]
		filename=self.RES_PATH+"\\"+re.sub("__.*",".ctl",item)
		filename=re.sub("\r|\n","",filename)
		title = re.sub(".*__","#T=",item)

		f=open(filename)
		templateStr=""
		lines=f.readlines()

		for i in range(len(lines)): 
			line=lines[i].decode(sys.getfilesystemencoding())
			
			if line==title:
				templateStr += line
			else:
				if templateStr!="":
					if not re.search("^#T=",line) and i<len(lines)-1: #@  素材文件最后一行是：#  不加入
						templateStr += line
					else:
						templateStr += re.sub(".*","",line) #@ 加一个 \n
						break

		tStr=re.sub("^#T=.*\n","",templateStr) 
		if tStr=="\n":  #@ 仅有一行的情况, 例如 CSS2.ctl 里的样式
			templateStr=re.sub("^(#T=)|\n|\r","",templateStr) 
		else:
			templateStr=tStr

		templateStr=re.sub("(\n|\r)$","",templateStr) #@ 最末尾的行符
		templateStr= templateStr.replace("^#T=","#T=") #@ 代码片断内容中若有 #T= ,Editplus为了避免与格式冲突,会自动加^在其前面 
		pat=re.compile(r"^\^#",re.MULTILINE) #@ ^#开头 
		templateStr= re.sub(pat,"#",templateStr)  
		templateStr= templateStr.replace("^^","^")  #@ ^^ 开头

		tempCursorFlagOffset=string.find(templateStr,"^!") #@ 查设置的光标位置


		res=self.view.sel()
		newRegins=[] #@ 新选区记录

		for regi in res:
			pos_x=regi.a
			pos_y=regi.b
			if regi.empty(): #@ 无选中字符
				newPointPos=-1
				if tempCursorFlagOffset>=0: 
					newPointPos=pos_x+tempCursorFlagOffset

				pretabstr=self.getPreTab(pos_x)
				pat=re.compile(r"\n",re.MULTILINE)

				if newPointPos==-1: #@ 无^! 标记的
					finalStr= re.sub(pat,"\n"+pretabstr,templateStr)
					self.view.replace(self.currentEditObj,regi,finalStr)
					ncp=pos_x+len(finalStr)
					newRegins.append(sublime.Region(ncp,ncp))
				else: # @ 有^! 标记的
					finalStr=re.sub(pat,"\n"+pretabstr,templateStr.replace("^!",""))  #@ 去除 ^! 并在除了第一行外的每一行前加缩进
					self.view.replace(self.currentEditObj,regi,finalStr)

					#@ templateStr 起始 到 ^! 标记中间有换行的，光标位置需要加: 行数*len(pretabstr)
 					ncount=len(re.split("\n",templateStr[0:tempCursorFlagOffset]))-1;
 					#print ncount
					newPointPos=newPointPos+ncount*len(pretabstr) #@ 光标位置
					newRegins.append(sublime.Region(newPointPos,newPointPos))
			else: #@ 有选区的
				'''
				PS:
					无 ^!  标记的 : 删除原选定, 插入代码片断
					有 ^!  标记的 : 不可删除原选定字符串, 应该提取出来记录，在插入代码片断后 , 于^! 标记处插入原选定字符串
				'''
				pos_min=regi.begin()

				if tempCursorFlagOffset<0: #@ 无 ^!  标记的
					self.view.replace(self.currentEditObj, regi, templateStr)
					ncp=pos_min+len(templateStr)
					newRegins.append(sublime.Region(ncp,ncp))
				else: #@ 有 ^!  标记的

					newPointPos=pos_min+tempCursorFlagOffset
					regionStr=self.view.substr(regi)

					pretabstr=self.getPreTab(pos_min) 
					pat=re.compile(r"\n", re.MULTILINE)
					finalStr=re.sub(pat,"\n"+pretabstr,templateStr) #@ 除了第一行外,每一行前加缩进

					#@ 选区的前缀缩进 处理
					regionStr_noPreTab=re.sub("^(\t|\s)+","",regionStr)
					regionStrPreTab_len=len(regionStr)-len(regionStr_noPreTab)
					regionStrPreTab=regionStr[0:regionStrPreTab_len]
 
					finalStr=regionStrPreTab+finalStr #@ 最终字符前 加上 选区的前缀缩进
					finalStr=finalStr.replace("^!",regionStr_noPreTab) #@ 替换掉前缀缩进的选区

					self.view.replace(self.currentEditObj, regi, finalStr)

					newPointStart=pos_min
					newPointEnd=newPointStart+len(finalStr)
					newRegins.append(sublime.Region(newPointStart,newPointEnd)) 

		#@ 清掉所有选区 并重新设置新的选区
		
		self.view.sel().clear()
		for regi in newRegins:
			self.view.sel().add(regi)
		
		#@ 以下是针对光标bug , 执行删除/ 撤销,使光标定位正确
		'''	
			如果不加最后面的两行代码（删除/ 撤销），当使用高亮时(例如代码用PHP高亮) 会出现光标定位失常的Bug （若是不选择高亮时，使用 Plain Text ，不会出现这个问题。）
			Bug的出现：
				在非反选字符的情况下插入设置有^!标记的素材,最后光标定位确实是已经定位到 ^! 标记处，但光标的闪烁显示是在末尾 
			原因：
				代码用show_quick_panel调出的列表，通过敲击这个下拉列表插入字符,就会导致这个问题。 若直接在代码里调用函数on_select_done则光标正常 

			因此, 在最后面，执行删除 / 撤销 命令，令光标正常显示...
		'''
		self.view.window().run_command("left_delete")
		self.view.window().run_command("undo")