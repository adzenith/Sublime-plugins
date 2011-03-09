"""
Add the following to your user file prefs:
	"scroll_offset_vertical" : 8,
	"scroll_offset_horizontal" : 20
replacing 8 and 20 with whatever numbers you like (those are the numbers I use).


Also if you want sweet debug markers then you can add this:
	"scroll_offset_guides" : true
Note how the markers always stay on the screen. Creepy!

Known issue:
	selecting near the edge of the screen with the mouse is kind of wonky
"""



import sublime
import sublime_plugin

def num_visible_rows_in_view(view):
	vr = view.visible_region()
	first_visible_row = view.rowcol(vr.begin())[0]
	last_visible_row = view.rowcol(vr.end())[0]
	return last_visible_row - first_visible_row + 1

def find_selection_limits(view):
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
	return first_caret_row, last_caret_row, leftmost_caret_rowcol, rightmost_caret_rowcol

class ScrollOffset(sublime_plugin.EventListener):
	def on_activated(self,view):
		self.on_selection_modified(view)
	
	def on_selection_modified(self, view):
		settings = view.settings()
		vertical_offset = abs(int(settings.get("scroll_offset_vertical") or 0))
		horizontal_offset = abs(int(settings.get("scroll_offset_horizontal") or 0))
		if not any((vertical_offset, horizontal_offset)):
			return
		if len(view.sel()) == 0:
			return
		
		show_guides = bool(settings.get("scroll_offset_guides"))
		
		(first_caret_row, last_caret_row,
		leftmost_caret_rowcol, rightmost_caret_rowcol) = find_selection_limits(view)
		
		num_visible_rows = num_visible_rows_in_view(view)
		num_rows_in_buffer = view.rowcol(view.size())[0]

		first_desired_row = first_caret_row
		last_desired_row = last_caret_row
		num_necessary_rows = last_caret_row - first_caret_row + 1
		if num_visible_rows < num_necessary_rows:
			return; #whatever ST does already is fine with me
		
		num_necessary_cols = rightmost_caret_rowcol[1] - leftmost_caret_rowcol[1] + 1
		# if num_necessary_cols >= num
		# How do I find out the width of the buffer?
		
		gap = min(vertical_offset, (num_visible_rows - num_necessary_rows) / 2)
		last_desired_row = min(last_caret_row + gap, num_rows_in_buffer)
		first_desired_row = max(first_caret_row - gap, 0)
		
		num_desired_rows = last_desired_row - first_desired_row + 1
		if num_desired_rows > num_visible_rows:
			raise AssertionError("How could this happen?")
		
		bottom_desired_pos = view.text_point(last_desired_row, 0)
		top_desired_pos = view.text_point(first_desired_row, 0)
		left_desired_pos = max(view.text_point(*leftmost_caret_rowcol) - horizontal_offset,
													 view.line(view.text_point(*leftmost_caret_rowcol)).begin())
		right_desired_pos = min(view.text_point(*rightmost_caret_rowcol) + horizontal_offset,
														view.line(view.text_point(*rightmost_caret_rowcol)).end())
		
		#position vertically
		view.show(sublime.Region(top_desired_pos, bottom_desired_pos), False)
		#position horizontally
		view.show(sublime.Region(left_desired_pos, right_desired_pos), False)
		if(show_guides):
			view.add_regions("Caret", [sublime.Region(*([top_desired_pos]*2)),
																sublime.Region(*([bottom_desired_pos]*2)),
																sublime.Region(*([left_desired_pos]*2)),
																sublime.Region(*([right_desired_pos]*2))],
																"comment", sublime.DRAW_EMPTY)
