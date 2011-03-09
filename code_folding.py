"""
Add these commands to your user keymap file:
	{ "keys": ["super+k"], "command": "fold"},
	{ "keys": ["shift+super+k"], "command": "unfold"}

HOW TO USE
Select some text, hit super+k, and it'll get folded into a fold indicator
like this one: [--[#]--] . It works with multiple selections too.
Put your cursor in a fold indicator (or select a bunch of them at once!) and
hit shift+super+k to unfold them.

WARNING
The form of the fold indicator is important -- you can feel free to move it
around, make multiple copies, etc., but if you change it at all it won't unfold
correctly. If you make a mistake, just change it back and it'll work.
"""


import sublime
import sublime_plugin
import re

def show_view_as_clean(view):
	if view.is_scratch():
		return
	global skip_next_modified_check
	view.set_scratch(True)
	view.settings().set("cleanliness",True)

class CleanlinessListener(sublime_plugin.EventListener):
	def on_modified(self,view):
		global skip_next_modified_check
		if view.settings().get("cleanliness") == True:
			view.settings().set("cleanliness",False)
			return
		elif view.settings().get("cleanliness") == False:
			view.set_scratch(False)
		#else cleanliness is None:
		#  pass

folds = []

def find_key_regions(view):
	numbers = []
	key_regions = view.find_all(r"\[--\[(\d+)\]--\]", 0, "$1", numbers)
	numbers = [int(n) for n in numbers]
	return key_regions, numbers

def unfold(view,edit,regions):
	dirty = view.is_dirty()
	#find the relevant fold key
	key_regions, numbers = find_key_regions(view)
	for k,n in reversed(zip(key_regions, numbers)):
		for r in regions:
			if r.intersects(k):
				#expand it
				if n >= len(folds):
					raise ValueError("Unknown fold number")
				view.replace(edit, k, folds[n])
	if not dirty:
		show_view_as_clean(view)

def fold_region(view,edit,region,num=None):
	dirty = view.is_dirty()
	if num == None:
		folds.append(view.substr(region))
		num = len(folds) - 1
	view.replace(edit,region,"[--[{0}]--]".format(num))
	if not dirty:
		show_view_as_clean(view)

class FoldCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if len(s):
				#check if we've already folded this string before
				substring = self.view.substr(s)
				try:
					n = folds.index(substring)
				except:
					n = None
				fold_region(self.view, edit, s, n)

class UnfoldCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		unfold(self.view, edit, self.view.sel())

class FoldListener(sublime_plugin.EventListener):
	key_regions = []
	numbers = []
	visible_region = None
	def on_pre_save(self, view):
		self.visible_region = view.visible_region()
		self.key_regions = []
		self.numbers = []
		try:
			edit = view.begin_edit()
			while True:
				kr, n = find_key_regions(view)
				if not len(kr):
					break
				self.key_regions = kr + self.key_regions
				self.numbers = n + self.numbers
				unfold(view, edit, [sublime.Region(0,len(view))])
		finally:
			view.end_edit(edit)
	
	def on_post_save(self, view):
		try:
			edit = view.begin_edit()
			for r,n in zip(self.key_regions, self.numbers):
				region_to_fold = sublime.Region(r.begin(),r.begin()+len(folds[n]))
				fold_region(view, edit, region_to_fold, n)
		finally:
			view.end_edit(edit)
			view.show(self.visible_region, False)
			show_view_as_clean(view)
