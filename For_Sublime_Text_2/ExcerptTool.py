# coding=gbk
import sublime, sublime_plugin
import os,sys
import re
import string

#@ 本文件ANSI

class ExcerptTool:

	excerpt_items = None
	config=sublime.load_settings("CodeExcerpt.sublime-settings")
	RES_PATH=config.get("respath")
	CHM_PATH=config.get("chmpath")
	view=None
	currentEditObj=None

	def __init__(self,_eitems,_view,_currentEditObj):  
		self.excerpt_items=_eitems
		self.view=_view
		self.currentEditObj=_currentEditObj

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
		
		if item.find("[ CHM ]") ==0:
			#@ 如果是chm文件 调用命令行打开
			import subprocess
			chmfile=self.CHM_PATH+"\\"+re.sub("^\[\sCHM\s\]\s-\s","",item)+".chm"
			print(chmfile)
			subprocess.Popen(["start /max ",chmfile.encode(sys.getfilesystemencoding())],shell=True) #@ 用命令行的命令打开需设置shell=True
			return 
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

					'''
						分别取两个行前缩进
						1. pretabstr               选区起点的那行的全部缩进 
						2. regionStrPreTab    选区范围内 第一个以tab 或空格开头的那行的 被选中的缩进
						这两个 可能相等 也可能不相等，取决于选取的情况

						最终仍然是有BUG，影响不大
					'''
					pretabstr=self.getPreTab(pos_min) 
					pat=re.compile(r"\n", re.MULTILINE)
					finalStr=re.sub(pat,"\n"+pretabstr,templateStr) #@ 除了第一行外,每一行前加 起点行缩进

					regionStr_noPreTab=re.sub("^(\t|\s)+","",regionStr) 
					regionStrPreTab_len=len(regionStr)-len(regionStr_noPreTab)
					regionStrPreTab=regionStr[0:regionStrPreTab_len] #@ 得到的是第一个以 tab 或 空格 开头的那行的缩进
					# print 'the region first line pre tab is:'+regionStrPreTab

					# print len(regionStrPreTab)
					if len(pretabstr)==0:
						finalStr=pretabstr+finalStr.replace("^!",regionStr) #@ 
					else:
						finalStr=regionStrPreTab+finalStr.replace("^!",regionStr_noPreTab) #@ 

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