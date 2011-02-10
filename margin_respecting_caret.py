import sublime, sublime_plugin

VERTICAL_GAP = 8
HORIZONTAL_GAP = 20

def num_visible_rows_in_view(view):
  vr = view.visible_region()
  first_visible_row = view.rowcol(vr.begin())[0]
  last_visible_row = view.rowcol(vr.end())[0]
  return last_visible_row - first_visible_row + 1

class MarginRespectingCaret(sublime_plugin.EventListener):
  def on_selection_modified(self, view):
    first_caret_row = float("inf")
    last_caret_row = -1
    leftmost_caret_rowcol = float("inf"), float("inf")
    rightmost_caret_rowcol = -1, -1
    for region in view.sel():
      begin_row,begin_col = view.rowcol(region.begin())
      end_row,end_col = view.rowcol(region.end())
      if end_row > last_caret_row:
        last_caret_row = end_row
      if begin_row < first_caret_row:
        first_caret_row = begin_row
      if end_col > rightmost_caret_rowcol[1]:
        rightmost_caret_rowcol = end_row, end_col
      if begin_col < leftmost_caret_rowcol[1]:
        leftmost_caret_rowcol = begin_row, begin_col
    
    num_visible_rows = num_visible_rows_in_view(view)
    num_rows_in_buffer = view.rowcol(view.size())[0]

    first_desired_row = first_caret_row
    last_desired_row = last_caret_row
    num_necessary_rows = last_caret_row - first_caret_row + 1
    if num_visible_rows < num_necessary_rows:
      return; #whatever ST does already is fine with me
    num_necessary_cols = rightmost_caret_rowcol[1] - leftmost_caret_rowcol[1] + 1
    # if num_necessary_cols >= num
    
    gap = min(VERTICAL_GAP, (num_visible_rows - num_necessary_rows) / 2)
    last_desired_row = last_caret_row + gap
    if last_desired_row > num_rows_in_buffer:
      last_desired_row = num_rows_in_buffer
    first_desired_row = first_caret_row - gap
    if first_desired_row < 0:
      first_desired_row = 0
    
    num_desired_rows = last_desired_row - first_desired_row + 1
    if num_desired_rows > num_visible_rows:
      raise AssertionError("How could this happen?")
    
    bottom_desired_pos = view.text_point(last_desired_row, 0)
    top_desired_pos = view.text_point(first_desired_row, 0)
    left_desired_pos = max(view.text_point(*leftmost_caret_rowcol) - HORIZONTAL_GAP,view.line(view.text_point(*leftmost_caret_rowcol)).begin())
    right_desired_pos = min(view.text_point(*rightmost_caret_rowcol) + HORIZONTAL_GAP,view.line(view.text_point(*rightmost_caret_rowcol)).end())
    
    #position vertically
    view.show(sublime.Region(top_desired_pos, bottom_desired_pos), False)
    #position horizontally
    view.show(sublime.Region(left_desired_pos, right_desired_pos), False)
    view.add_regions("Caret", [sublime.Region(*([top_desired_pos]*2)),
                              sublime.Region(*([bottom_desired_pos]*2)),
                              sublime.Region(*([left_desired_pos]*2)),
                              sublime.Region(*([right_desired_pos]*2))],
                              "comment", sublime.DRAW_EMPTY)


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


import datetime

class InsertTimestampCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    #generate the timestamp
    timestamp_str = datetime.datetime.now().isoformat(' ')

    #for region in the selection
    #(i.e. if you have multiple regions selected,
    # insert the timestamp in all of them)
    for r in self.view.sel():
      #put in the timestamp
      #(if text is selected, it'll be
      # replaced in an intuitive fashion)
      self.view.erase(edit, r)
      self.view.insert(edit, r.begin(), timestamp_str)
