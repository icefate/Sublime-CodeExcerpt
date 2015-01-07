# coding=gbk
import sublime, sublime_plugin
import os,sys
import re
import string

#@ ���ļ�ANSI
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
			self.view.window().show_quick_panel(self.excerpt_items,self.on_select_done)
		else:
			#@ �����chm�ļ� ���������д�
			import subprocess
			subprocess.Popen(["start /max ",file_selected["fullfilename"].encode(sys.getfilesystemencoding())],shell=True) #@ �������е������������shell=True

	#@ ����ѡ����ʼ��ǰ������	
	def getPreTab(self,point):
		regionSelectedFirstLine=self.view.line(point)
		#print self.view.substr(regionSelectedFirstLine)
 		m = re.match("^(\t|\s)+", self.view.substr(regionSelectedFirstLine))
		retStr=""
		if m!=None:
			retStr=m.group(0)
		return retStr

	#@ ���б���ѡ���ز�Ƭ�� ִ��
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
					if not re.search("^#T=",line) and i<len(lines)-1: #@  �ز��ļ����һ���ǣ�#  ������
						templateStr += line
					else:
						templateStr += re.sub(".*","",line) #@ ��һ�� \n
						break

		tStr=re.sub("^#T=.*\n","",templateStr) 
		if tStr=="\n":  #@ ����һ�е����, ���� CSS2.ctl �����ʽ
			templateStr=re.sub("^(#T=)|\n|\r","",templateStr) 
		else:
			templateStr=tStr

		templateStr=re.sub("(\n|\r)$","",templateStr) #@ ��ĩβ���з�
		templateStr= templateStr.replace("^#T=","#T=") #@ ����Ƭ������������ #T= ,EditplusΪ�˱������ʽ��ͻ,���Զ���^����ǰ�� 
		pat=re.compile(r"^\^#",re.MULTILINE) #@ ^#��ͷ 
		templateStr= re.sub(pat,"#",templateStr)  
		templateStr= templateStr.replace("^^","^")  #@ ^^ ��ͷ

		tempCursorFlagOffset=string.find(templateStr,"^!") #@ �����õĹ��λ��


		res=self.view.sel()
		newRegins=[] #@ ��ѡ����¼

		for regi in res:
			pos_x=regi.a
			pos_y=regi.b
			if regi.empty(): #@ ��ѡ���ַ�
				newPointPos=-1
				if tempCursorFlagOffset>=0: 
					newPointPos=pos_x+tempCursorFlagOffset

				pretabstr=self.getPreTab(pos_x)
				pat=re.compile(r"\n",re.MULTILINE)

				if newPointPos==-1: #@ ��^! ��ǵ�
					finalStr= re.sub(pat,"\n"+pretabstr,templateStr)
					self.view.replace(self.currentEditObj,regi,finalStr)
					ncp=pos_x+len(finalStr)
					newRegins.append(sublime.Region(ncp,ncp))
				else: # @ ��^! ��ǵ�
					finalStr=re.sub(pat,"\n"+pretabstr,templateStr.replace("^!",""))  #@ ȥ�� ^! ���ڳ��˵�һ�����ÿһ��ǰ������
					self.view.replace(self.currentEditObj,regi,finalStr)

					#@ templateStr ��ʼ �� ^! ����м��л��еģ����λ����Ҫ��: ����*len(pretabstr)
 					ncount=len(re.split("\n",templateStr[0:tempCursorFlagOffset]))-1;
 					#print ncount
					newPointPos=newPointPos+ncount*len(pretabstr) #@ ���λ��
					newRegins.append(sublime.Region(newPointPos,newPointPos))
			else: #@ ��ѡ����
				'''
				PS:
					�� ^!  ��ǵ� : ɾ��ԭѡ��, �������Ƭ��
					�� ^!  ��ǵ� : ����ɾ��ԭѡ���ַ���, Ӧ����ȡ������¼���ڲ������Ƭ�Ϻ� , ��^! ��Ǵ�����ԭѡ���ַ���
				'''
				pos_min=regi.begin()

				if tempCursorFlagOffset<0: #@ �� ^!  ��ǵ�
					self.view.replace(self.currentEditObj, regi, templateStr)
					ncp=pos_min+len(templateStr)
					newRegins.append(sublime.Region(ncp,ncp))
				else: #@ �� ^!  ��ǵ�

					newPointPos=pos_min+tempCursorFlagOffset
					regionStr=self.view.substr(regi)

					pretabstr=self.getPreTab(pos_min) 
					pat=re.compile(r"\n", re.MULTILINE)
					finalStr=re.sub(pat,"\n"+pretabstr,templateStr) #@ ���˵�һ����,ÿһ��ǰ������

					#@ ѡ����ǰ׺���� ����
					regionStr_noPreTab=re.sub("^(\t|\s)+","",regionStr)
					regionStrPreTab_len=len(regionStr)-len(regionStr_noPreTab)
					regionStrPreTab=regionStr[0:regionStrPreTab_len]
 
					finalStr=regionStrPreTab+finalStr #@ �����ַ�ǰ ���� ѡ����ǰ׺����
					finalStr=finalStr.replace("^!",regionStr_noPreTab) #@ �滻��ǰ׺������ѡ��

					self.view.replace(self.currentEditObj, regi, finalStr)

					newPointStart=pos_min
					newPointEnd=newPointStart+len(finalStr)
					newRegins.append(sublime.Region(newPointStart,newPointEnd)) 

		#@ �������ѡ�� �����������µ�ѡ��
		
		self.view.sel().clear()
		for regi in newRegins:
			self.view.sel().add(regi)
		
		#@ ��������Թ��bug , ִ��ɾ��/ ����,ʹ��궨λ��ȷ
		'''	
			����������������д��루ɾ��/ ����������ʹ�ø���ʱ(���������PHP����) ����ֹ�궨λʧ����Bug �����ǲ�ѡ�����ʱ��ʹ�� Plain Text ���������������⡣��
			Bug�ĳ��֣�
				�ڷǷ�ѡ�ַ�������²���������^!��ǵ��ز�,����궨λȷʵ���Ѿ���λ�� ^! ��Ǵ�����������˸��ʾ����ĩβ 
			ԭ��
				������show_quick_panel�������б�ͨ���û���������б�����ַ�,�ͻᵼ��������⡣ ��ֱ���ڴ�������ú���on_select_done�������� 

			���, ������棬ִ��ɾ�� / ���� �������������ʾ...
		'''
		self.view.window().run_command("left_delete")
		self.view.window().run_command("undo")