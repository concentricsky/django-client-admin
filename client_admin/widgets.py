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

from client_admin.templatetags.generic import get_admin_object_change_url


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


class UnicodeForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    """
    A Widget for displaying ForeignKeys in the "raw_id" interface rather than
    in a <select> box, but displaying the unicode of the object instead of the id.
    """
    def __init__(self, rel, admin_site, attrs=None, using=None):
        self.rel = rel
        self.admin_site = admin_site
        self.db = using
        super(ForeignKeyRawIdWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        rel_to = self.rel.to
        if attrs is None:
            attrs = {}
        extra = []
        if rel_to in self.admin_site._registry:
            # The related object is registered with the same AdminSite
            related_url = reverse('admin:%s_%s_changelist' %
                                    (rel_to._meta.app_label,
                                    rel_to._meta.module_name),
                                    current_app=self.admin_site.name)

            params = self.url_parameters()
            if params:
                url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in params.items()])
            else:
                url = ''
            if "class" not in attrs:
                attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript code looks for this hook.
            # TODO: "lookup_id_" is hard-coded here. This should instead use
            # the correct API to determine the ID dynamically.
            extra.append('<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);">%s</a>'
                            % (related_url, url, name, 'Find'))
        output = [self.label_for_value(value, name), super(ForeignKeyRawIdWidget, self).render(name, value, attrs)] + extra
        return mark_safe(''.join(output))

    def label_for_value(self, value, name):
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to._default_manager.using(self.db).get(**{key: value})
            return '<a href="%s" target="_blank" class="related_link" id="unicode_id_%s">%s</a>' % (get_admin_object_change_url(obj), name, escape(Truncator(obj).words(14, truncate='...')))
        except (ValueError, self.rel.to.DoesNotExist):
            return '<a target="_blank" id="unicode_id_%s"></a>' % name
