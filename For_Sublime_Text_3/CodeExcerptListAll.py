import sublime, sublime_plugin
import os,sys
import re
import string

from . import ExcerptTool


class CodeExcerptListAllCommand(sublime_plugin.TextCommand):

	config=None
	ET=None

	def run(self, edit):

		self.config=sublime.load_settings("CodeExcerpt.sublime-settings")

		self.ET=ExcerptTool.ETool(self.view,self.config)
		self.ET.listType="all"

		self.view.window().show_quick_panel(self.ET.excerpt_items_all,self.ET.on_select_done)



