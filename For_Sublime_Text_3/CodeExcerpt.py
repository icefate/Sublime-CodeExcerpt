import sublime, sublime_plugin
import os,sys
import re
import string

from . import ExcerptTool


class CodeExcerptCommand(sublime_plugin.TextCommand):


	config=None
	ET=None

	def run(self, edit):

		self.config=sublime.load_settings("CodeExcerpt.sublime-settings")

		self.ET=ExcerptTool.ETool(self.view,self.config)

		#@ sublime.active_window().show_quick_panel(self.ET.file_items,self.on_select_file) 
		self.view.window().show_quick_panel(self.ET.file_items,self.ET.on_select_file)



