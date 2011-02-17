import sublime
import sublime_plugin
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
