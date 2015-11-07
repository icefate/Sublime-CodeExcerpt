# coding=gbk
import sublime, sublime_plugin
import os,sys
import re
import string

#@ ���ļ�ANSI

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
		
		if item.find("[ CHM ]") ==0:
			#@ �����chm�ļ� ���������д�
			import subprocess
			chmfile=self.CHM_PATH+"\\"+re.sub("^\[\sCHM\s\]\s-\s","",item)+".chm"
			print(chmfile)
			subprocess.Popen(["start /max ",chmfile.encode(sys.getfilesystemencoding())],shell=True) #@ �������е������������shell=True
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

					'''
						�ֱ�ȡ������ǰ����
						1. pretabstr               ѡ���������е�ȫ������ 
						2. regionStrPreTab    ѡ����Χ�� ��һ����tab ��ո�ͷ�����е� ��ѡ�е�����
						������ ������� Ҳ���ܲ���ȣ�ȡ����ѡȡ�����

						������Ȼ����BUG��Ӱ�첻��
					'''
					pretabstr=self.getPreTab(pos_min) 
					pat=re.compile(r"\n", re.MULTILINE)
					finalStr=re.sub(pat,"\n"+pretabstr,templateStr) #@ ���˵�һ����,ÿһ��ǰ�� ���������

					regionStr_noPreTab=re.sub("^(\t|\s)+","",regionStr) 
					regionStrPreTab_len=len(regionStr)-len(regionStr_noPreTab)
					regionStrPreTab=regionStr[0:regionStrPreTab_len] #@ �õ����ǵ�һ���� tab �� �ո� ��ͷ�����е�����
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