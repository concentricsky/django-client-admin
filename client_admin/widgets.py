# Copyright 2015 Concentric Sky, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django import forms
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.widgets import AdminFileWidget, ForeignKeyRawIdWidget
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.html import escape, format_html, format_html_join, smart_urlquote
from django.utils.text import Truncator
from django.utils.translation import ugettext as _


def thumbnail(image_path):
   return u'<img src="%s" class="imageupload-thumbnail">' % image_path


class ThumbnailImageWidget(AdminFileWidget):
    template_with_initial = '%(input)s%(clear_template)s'
    clear_checkbox_label = "<span>Undo</span> Delete Image"

    def render(self, name, value, attrs=None):
        output = []
        if value:
            file_path = '%s%s' % (getattr(settings, 'MEDIA_URL', '/media/'), value)
            try:
                output.append('<a target="_blank" href="%s" class="imageupload-thumbcontainer">%s</a>' %
                       (file_path, thumbnail(file_path)))
            except IOError:
                output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' %
                       ('Currently:', file_path, value, 'Change:'))
        else:
            output.append(thumbnail('%sclient_admin/images/missing_image.png' % getattr(settings, 'STATIC_URL', '/static/')))

        output.append('<div class="imageupload-widget"><p class="file-upload">%s</p></div>' % super(ThumbnailImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class AdminDateWidget(forms.DateInput):

    @property
    def media(self):
        js = ["calendar.js", "admin/DateTimeShortcuts.js"]
        return forms.Media(js=[static("admin/js/%s" % path) for path in js])

    def __init__(self, attrs=None, format=None):
        final_attrs = {'class': 'vDateField', 'size': '10'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminDateWidget, self).__init__(attrs=final_attrs, format=format)


class AdminTimeWidget(forms.TimeInput):

    @property
    def media(self):
        js = ["calendar.js", "admin/DateTimeShortcuts.js"]
        return forms.Media(js=[static("admin/js/%s" % path) for path in js])

    def __init__(self, attrs=None, format=None):
        final_attrs = {'class': 'vTimeField', 'size': '8'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTimeWidget, self).__init__(attrs=final_attrs, format=format)

class AdminSplitDateTime(forms.SplitDateTimeWidget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """
    def __init__(self, attrs=None):
        widgets = [AdminDateWidget, AdminTimeWidget]
        # Note that we're calling MultiWidget, not SplitDateTimeWidget, because
        # we want to define widgets.
        forms.MultiWidget.__init__(self, widgets, attrs)

    def format_output(self, rendered_widgets):
        return mark_safe(u'<p class="datetime">%s %s<br />%s %s</p>' % \
            (_('<span>Date:</span>'), rendered_widgets[0], _('<span>Time:</span>'), rendered_widgets[1]))


class AdminURLFieldWidget(forms.TextInput):
    def __init__(self, attrs=None):
        final_attrs = {'class': 'vURLField'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminURLFieldWidget, self).__init__(attrs=final_attrs)

    def render(self, name, value, attrs=None):
        html = super(AdminURLFieldWidget, self).render(name, value, attrs)
        if value:
            value = force_text(self._format_value(value))
            final_attrs = {'href': mark_safe(smart_urlquote(value))}
            html = format_html(
                '<p class="url"><a {0} target="_blank">Visit this site</a><br />{1}</p>',
                flatatt(final_attrs), html
            )
        return html
