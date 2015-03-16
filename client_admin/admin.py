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

# # Client Admin admin classes
from client_admin.views import generic_lookup, get_generic_rel_list
from client_admin.widgets import ThumbnailImageWidget, AdminURLFieldWidget, UnicodeForeignKeyRawIdWidget

import re

from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.options import get_ul_class
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.util import unquote
from django.contrib.admin.widgets import AdminRadioSelect
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import ImageField, ManyToManyField, FieldDoesNotExist, URLField
from django.forms import Form
from django.forms.fields import CharField
from django.forms.formsets import all_valid
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

csrf_protect_m = method_decorator(csrf_protect)

JS_PATH = getattr(settings, 'GENERICADMIN_JS', 'client_admin/js/')


class EmptyVersionAdmin(object):
    pass

try:
    import reversion
    VersionAdmin = reversion.VersionAdmin
except:
    VersionAdmin = EmptyVersionAdmin


class AdvancedSearchForm(Form):
    def __init__(self, *args, **kwargs):
        admin_class = kwargs.pop('admin_class')
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
        for item in admin_class.search_fields:

            # Check for this field in the advanced search titles dict on the admin class
            property_verbose_name = getattr(admin_class, 'advanced_search_titles', {}).get(item)
            if property_verbose_name:
                verbose_name = property_verbose_name
            else:
                # See if this field is a regular field or a related field property
                item_parts = item.split('__')
                if len(item_parts) > 1:
                    # This assumes it was only two parts, else this should be recursive

                    # Get the field and fk info from get_field_by_name()
                    field, model, direct, m2m = admin_class.model._meta.get_field_by_name(item_parts[0])
                    if direct or m2m:
                        # This is a related property of a fk or m2m, so the field_class is the field.model
                        field_class = field.related.parent_model
                    else:
                        # This is a reverse m2m _set, so the field class is that related class
                        field_class = getattr(admin_class.model, item_parts[0]).related.model

                    field, model, direct, m2m = field_class._meta.get_field_by_name(item_parts[1])
                    verbose_name = "%s %s" % (field_class._meta.verbose_name.title(), field.verbose_name.title())
                else:
                    # This was just a regular field
                    field_class = admin_class.model
                    field_name = item
                    field, model, direct, m2m = field_class._meta.get_field_by_name(field_name)
                    verbose_name = field.verbose_name.title()

            self.fields['%s__icontains' % item] = CharField(label=verbose_name)


class AdvancedSearchMixin(object):
    advanced_search_titles = {}

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        new_context = {'advanced_search_form': AdvancedSearchForm(admin_class=self, initial=request.GET)}
        new_context.update(extra_context or {})
        return super(AdvancedSearchMixin, self).changelist_view(request, extra_context=new_context)

    def lookup_allowed(self, lookup, value):
        if re.sub('\__icontains$', '', lookup) in self.search_fields:
            return True
        else:
            return super(AdvancedSearchMixin, self).lookup_allowed(lookup, value)


class URLFieldMixin(object):
    formfield_overrides = {
        URLField: {'widget': AdminURLFieldWidget},
    }


class ImageWidgetMixin(object):
    # Override image widget
    formfield_overrides = {
        ImageField: {'widget': ThumbnailImageWidget},
    }


class UnicodeForeignKeyRawIdWidgetMixin(object):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        db = kwargs.get('using')
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = UnicodeForeignKeyRawIdWidget(db_field.rel, self.admin_site, using=db)
        elif db_field.name in self.radio_fields:
            kwargs['widget'] = AdminRadioSelect(attrs={
                'class': get_ul_class(self.radio_fields[db_field.name]),
            })
            kwargs['empty_label'] = db_field.blank and _('None') or None
        return db_field.formfield(**kwargs)

class DeprecationExceptionMixin(object):
    raise DeprecationWarning('Deprecated as of v2.X')

class BaseClientAdminMixin(UnicodeForeignKeyRawIdWidgetMixin, GenericModelAdminMixin, AdvancedSearchMixin, ImageWidgetMixin, URLFieldMixin):
    formfield_overrides = dict(ImageWidgetMixin.formfield_overrides.items() + URLFieldMixin.formfield_overrides.items())

class RecursiveInlinesModelAdmin(DeprecationExceptionMixin):
    pass

class StackedInlineMixin(object):
    collapse = False

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super(StackedInlineMixin, self).get_formset(request, obj, **kwargs)
        FormSet.collapse = self.collapse
        return FormSet
class GenericModelAdminMixin(DeprecationExceptionMixin):
    pass


class GenericStackedInline(DeprecationExceptionMixin):
    pass


class GenericGroupedInline(DeprecationExceptionMixin):
    pass


class GenericTabularInline(DeprecationExceptionMixin):
    pass


class StackedInline(StackedInlineMixin, BaseRecursiveInlineMixin, BaseClientAdminMixin, GenericModelAdminMixin, admin.StackedInline):
    pass


class TabularInline(BaseRecursiveInlineMixin, BaseClientAdminMixin, GenericModelAdminMixin, admin.TabularInline):
    pass


class GenericTabularInline(BaseRecursiveInlineMixin, BaseClientAdminMixin, GenericModelAdminMixin, generic.GenericTabularInline):
    # Model admin for generic tabular inlines.
    pass


class GroupedInline(StackedInline):
    template = 'admin/edit_inline/grouped.html'


class ClientModelAdmin(VersionAdmin, ReverseInlinesModelAdminMixin, BaseClientAdminMixin, RecursiveInlinesModelAdmin):
    pass


class BaseGenericModelAdmin(DeprecationExceptionMixin):
    pass
