"""
DRAW OUTLINED
  "word_highlights_draw_outlined" : true
    Add this to your user prefs to make the highlights be drawn as outlines
    instead of as filled highlights.

COLOR OPTIONS
  "word_highlights_color_scope_name" : "wordhighlight"
    Normally the color of the highlights is the same as the color of comments
    in your code. If you'd like to customize the color, add the below to your
    color scheme file and change EDF2E9 to whatever color you want, then add
    this to your user file preferences.
---ADD TEXT BELOW THIS LINE TO YOUR COLOR SCHEME FILE---
    <dict>
        <key>name</key>
        <string>WordHighlight</string>
        <key>scope</key>
        <string>wordhighlight</string>
        <key>settings</key>
        <dict>
          <key>foreground</key>
          <string>#EDF2E9</string>
       </dict>
    </dict>
---ADD TEXT ABOVE THIS LINE TO YOUR COLOR SCHEME FILE---
"""

import sublime
import sublime_plugin

DEFAULT_COLOR_SCOPE_NAME = "comment"

class WordHighlightListener(sublime_plugin.EventListener):
  def on_selection_modified(self,view):
    settings = view.settings()
    color_scope_name = settings.get('word_highlights_color_scope_name', DEFAULT_COLOR_SCOPE_NAME)
    draw_outlined = bool(settings.get('word_highlights_draw_outlined')) * sublime.DRAW_OUTLINED
    
    regions = []
    for sel in view.sel():
      if len(sel) > 2:
        regions += view.find_all(view.substr(sel), sublime.LITERAL)
    view.add_regions("WordHighlight", regions, color_scope_name, draw_outlined)