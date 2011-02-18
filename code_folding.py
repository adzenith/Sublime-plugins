import sublime
import sublime_plugin
import re

skip_next_modified_check = False

def show_view_as_clean(view):
  global skip_next_modified_check
  view.set_scratch(True)
  skip_next_modified_check = True

class CleanlinessListener(sublime_plugin.EventListener):
  def on_modified(self,view):
    global skip_next_modified_check
    if skip_next_modified_check:
      skip_next_modified_check = False
      return
    view.set_scratch(False)

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
        fold_region(self.view, edit, s)

class UnfoldCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    unfold(self.view, edit, self.view.sel())

class FoldListener(sublime_plugin.EventListener):
  key_regions = []
  numbers = []
  visible_region = None
  def on_pre_save(self, view):
    self.key_regions, self.numbers = find_key_regions(view)
    self.visible_region = view.visible_region()
    try:
      edit = view.begin_edit()
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
