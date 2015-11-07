import sublime, sublime_plugin
import os,sys
import re
import string

class ETool:
	
	config=None
	RES_PATH=None
	CHM_PATH=None
	view=None
	files=[]
	file_items=[]
	excerpt_items = []
	excerpt_items_all = []
	listType="" #@ 装载方式 默认为分部装载;  设置 all 则为全部装载

	def __init__(self,_view,_config):  
		self.view=_view
		self.config=_config
		self.RES_PATH=_config.get("respath")
		self.CHM_PATH=_config.get("chmpath")
		if len(self.files)==0:
			print('初次加载文件和素材....')
			self.initFiles(self.RES_PATH,".ctl") 
			self.initFiles(self.CHM_PATH,".chm")
		print(self.RES_PATH)

	#@ 初始化文件
	def initFiles(self,path,ext):
		sfiles=os.listdir(path)
		for sf in sfiles:
			sf_fullname=os.path.join(path,sf)
			if os.path.isfile(sf_fullname):
				sfp=os.path.splitext(sf_fullname) # [file name without extension , file extension]
				if sfp[1].lower()==ext:
					clearfilename=sf[0:(len(sf)-len(sfp[1]))]
					if ext==".chm":
						clearfilename="[ CHM ] - "+clearfilename
						ftype="doc"
					else:
						ftype="template"
					fitem={"name":clearfilename,"type":ftype, "filename":sf,"fullfilename":sf_fullname}
					self.files.append(fitem)
					self.file_items.append(clearfilename)
					self.loadExcerptByFile(fitem)

	#@ 全部装载 加载所有素材 
	def loadExcerptByFile(self,thefitem):
		if thefitem["type"]=="template":
			#@ ANSI.ctl Code.ctl等特殊编码的文件 会读取出错，这里跳过
			try:
				f=open(thefitem["fullfilename"],"r")
				for line in f.readlines(): 
					if re.search("^#T=",line):
						self.excerpt_items_all.append(thefitem["name"]+"__"+line.replace("#T=",""))
			except Exception as e:
				print(e)

		else :
			self.excerpt_items_all.append(thefitem["name"])


	#@ 分部装载 . 在列表选中文件 执行
	def on_select_file(self,picked):
		if picked == -1:
			return
		try:
			self.excerpt_items=[] #@ 必须重设为空，否则上次加载的会遗留
			file_selected = self.files[picked]
			if file_selected["type"]=="template":
				f=open(file_selected["fullfilename"])
				for line in f.readlines(): 
					if re.search("^#T=",line):
						self.excerpt_items.append(file_selected["name"]+"__"+line.replace("#T=",""))

				self.view.window().show_quick_panel(self.excerpt_items,self.on_select_done) 
			else:
				#@ 如果是chm文件 调用命令行打开
				self.openCHM(file_selected["fullfilename"])
		except Exception as e:
			print(e)

	def openCHM(self,_fname):
		#@ 如果是chm文件 调用命令行打开
		import subprocess
		subprocess.Popen([_fname],None,shell=True) #@ 用命令行的命令打开需设置shell=True

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
		if self.listType=="all": #@ 全部装载
			item = self.excerpt_items_all[picked]
			if item.find("[ CHM ] - ")==0: #@ CHM
				self.openCHM(self.CHM_PATH+"\\"+re.sub("^\[\sCHM\s\]\s-\s","",item)+".chm")
			else:
				self.doInsertExcerpt(item)
		else:#@ 分部装载 - 默认
			item = self.excerpt_items[picked]
			self.doInsertExcerpt(item)

	def doInsertExcerpt(self,_item):

		filename=self.RES_PATH+"\\"+re.sub("__.*",".ctl",_item)
		filename=re.sub("\r|\n","",filename)
		title = re.sub(".*__","#T=",_item)

		try:
			f=open(filename,"r")
			templateStr=""
			lines=f.readlines()

			for i in range(len(lines)): 
				line=lines[i]
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

			tempCursorFlagOffset=templateStr.find("^!") #@ 查设置的光标位置 


			res=self.view.sel()
			reslen=len(res)

			tempRegins=[] #@ 新临时选区记录
			tempRegins_final=[] #@ 最终选区记录

			finalStr_list=[]
			regionStr_len_list=[]

			#@ 在打开quick panel后，run已返回，无法获取到edit对象。那么想在此处使用 self.view.insert(edit对象, point, str)  的方式是行不通的
			#@ 改为：访问粘贴板，以粘贴方式插入字符
			clipboard_oldstr=sublime.get_clipboard() 

			pat=re.compile(r"\n",re.MULTILINE)

			for i in range(reslen):
				regi=res[i]
				if regi.a>regi.b: #@ 选区也有方向 ，从右往左选在 a>b
					pos_x=regi.b
					pos_y=regi.a
				else:
					pos_x=regi.a
					pos_y=regi.b

				regionStr=self.view.substr(regi)
				
				m = re.match("^(\t|\s)+", regionStr) #@ 取选中的部分的前缀tab
				regionStr_selected_pre_tab=""
				if m!=None:
					regionStr_selected_pre_tab=m.group(0)
				pos_x_notab=pos_x+len(regionStr_selected_pre_tab) #@ 取选中的部分的前缀tab 的长度，得到 新临时选区 起始位置
				tempRegins.append(str(pos_x_notab)+"-"+str(pos_y)) #@ 新临时选区位置

				regi_notab=sublime.Region(pos_x_notab,pos_y)
				regionStr=self.view.substr(regi_notab)
				

				#@ 生成最终字符串 finalStr  
				pretabstr=self.getPreTab(pos_x) 
				finalStr = re.sub(pat,"\n"+pretabstr,templateStr) #@ 加前缀缩进： pretabstr 
				tempCursorFlagOffset_withtab=finalStr.find("^!") #@ 加了前缀缩进后 ^! 的位置
				finalStr = finalStr.replace("^!",regionStr) #@ 最后再替换 ^! 为选中的字符串

				finalStr_list.append(finalStr)
				regionStr_len_list.append(len(regionStr)) #@ 只要长度


				pos_x_final=pos_x_notab #@ 新临时选区起始位置，而非
				added_plus=0
				for p in range(i):
					#@ 每次粘贴之后，下一个的选区起始位置会后移动，因此计算以前增加了多少长度  计算：+ 以前每次最终字符长度 - 以前每次原选中的长度
					added_plus +=len(finalStr_list[p]) - regionStr_len_list[p]

				pos_x_final +=added_plus
				pos_y_final=pos_x_final+len(finalStr)

				if regi.empty() and tempCursorFlagOffset>-1: #@ 无选中字符 素材有 ^!
					pos_x_final +=tempCursorFlagOffset_withtab
					pos_y_final=pos_x_final+regionStr_len_list[i] 

				tempRegins_final.append(str(pos_x_final)+"-"+str(pos_y_final))

			
			#@ 清空选区，逐个添加选区，并粘贴
			self.view.sel().clear()
			for i in range(reslen):
				#@ print("------------------------")
				posXY=tempRegins[i].split('-')
				pos_x_new=int(posXY[0])
				pos_y_new=int(posXY[1])
				len_plus=0
				for p in range(i):
					#@ 每次粘贴之后，下一个的选区起始位置会后移动，因此计算以前增加了多少长度 计算：+ 上一个最终字符长度 - 上一个原选中的长度
					len_plus +=len(finalStr_list[p])-regionStr_len_list[p] 
				#print(pos_x_new,pos_y_new)
				#print(len_plus)
				pos_x_new +=len_plus
				pos_y_new +=len_plus			
				#print(pos_x_new,pos_y_new)

				regi_new=sublime.Region(pos_x_new,pos_y_new)
				self.view.sel().add(regi_new)

				sublime.set_clipboard(finalStr_list[i])
				self.view.run_command("paste") #@ 粘贴
				self.view.sel().clear() #@ 每次都清掉选区


			#@ 最后，使光标选区定位正确
			for i in range(reslen):
				#@ print("------------------------")
				posXY=tempRegins_final[i].split('-')
				pos_x_new=int(posXY[0])
				pos_y_new=int(posXY[1])
				regi_new=sublime.Region(pos_x_new,pos_y_new)
				self.view.sel().add(regi_new)

			self.view.run_command("left_delete")
			self.view.run_command("undo")

			sublime.set_clipboard(clipboard_oldstr) #@原剪贴板的字符

			#@ 记录
			#@ 不要使用insert 命令插入字符, 其会添加一些前缀tab, 这不是我们所预期的。
			#@ self.view.run_command("insert", {"characters": str}) 

		except Exception as e:
			print(e)