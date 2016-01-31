from __future__ import unicode_literals
from django import forms
try:
    from django.forms.utils import flatatt
except ImportError:
    from django.forms.util import flatatt

from django.utils.safestring import mark_safe
from django.utils.html import escape

class AceOverlayWidget(forms.Textarea):
    def __init__(self, mode=None, theme=None, wordwrap=False, width="500px", height="300px", showprintmargin=True, *args, **kwargs):
        self.mode = mode
        self.theme = theme
        self.wordwrap = wordwrap
        self.width = width
        self.height = height
        self.showprintmargin = showprintmargin
        super(AceOverlayWidget, self).__init__(*args, **kwargs)

    @property
    def media(self):
        js = [
            "ace_overlay/ace/ace.js",
            "ace_overlay/widget.js",
            ]
        if self.mode:
            js.append("ace_overlay/ace/mode-%s.js" % self.mode)
        if self.theme:
            js.append("ace_overlay/ace/theme-%s.js" % self.theme)
        css = {
            "screen": ["ace_overlay/widget.css"],
            }
        return forms.Media(js=js, css=css)

    def render(self, name, value, attrs=None):
        attrs = attrs or {}

        ace_attrs = {
            "class": "django-ace-widget loading",
            "style": "width:%s; height:%s" % (self.width, self.height)
        }
        if self.mode:
            ace_attrs["data-mode"] = self.mode
        if self.theme:
            ace_attrs["data-theme"] = self.theme
        if self.wordwrap:
            ace_attrs["data-wordwrap"] = "true"
        ace_attrs["data-showprintmargin"] = "true" if self.showprintmargin else "false"

        textarea = super(AceOverlayWidget, self).render(name, value, attrs)


        html = '<div%s><div></div></div>%s' % (flatatt(ace_attrs), textarea)


        # add toolbar
        # html = '<div class="django-ace-editor"><div style="width: %s" class="django-ace-toolbar"><a href="./" class="django-ace-max_min"></a></div>%s</div>' % (self.width, html)

        html = "<div class='ace-overlay'>\
            <div class='readonly-container'>\
                <div class='input-container'>%s</div>\
                <div class='code-container'>%s</div>\
                <a href='#' class='edit'></a>\
            </div>\
            <div class='overlay-container'>\
                <a href='#' class='backdrop' title='Cancel'></a>\
                <div class='overlay'>\
                    <div class='header'>\
                        <div class='title'>Editing...</div>\
                        <div class='buttons'><a href='#' class='cancel'>Cancel</a><a href='#' class='save'>Close</a></div>\
                    </div>\
                    <div class='editor-container'>\
                        <div%s></div>\
                    </div>\
                </div>\
            </div>\
        </div>"%(textarea, escape(value), flatatt(ace_attrs))

        return mark_safe(html)
