import sublime
import sublime_plugin

def select(view, region):
  sel_set = view.sel()
  sel_set.clear()
  sel_set.add(region)
  view.show(region, True)

def onDone_find_definition_input(search_string):
  v = sublime.active_window().active_view()
  results = v.find_all(search_string)
  for r in results:
    if v.syntax_name(r.begin()).startswith("entity.name.function"):
      print ':', v,r
      select(v, r)
      pass

class FindDefinitionCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = sublime.active_window().active_view()
    default_text = ""
    if len(view.sel()) == 1:
      default_text = view.substr(view.word(view.sel()[0]))
    panel_view = sublime.active_window().show_input_panel("Definition of:",default_text,onDone_find_definition_input,0,0)
