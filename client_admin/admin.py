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
from client_admin.widgets import ThumbnailImageWidget, AdminURLFieldWidget

import re

from django.conf import settings
from django.db.models import ImageField, URLField
from django.forms import Form
from django.forms.fields import CharField
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

csrf_protect_m = method_decorator(csrf_protect)


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


class DeprecationExceptionMixin(object):
    raise DeprecationWarning('Deprecated as of v2.X')


class RecursiveInlinesModelAdmin(DeprecationExceptionMixin):
    pass


class GenericModelAdminMixin(DeprecationExceptionMixin):
    pass


class GenericStackedInline(DeprecationExceptionMixin):
    pass


class GenericGroupedInline(DeprecationExceptionMixin):
    pass


class GenericTabularInline(DeprecationExceptionMixin):
    pass


class StackedInline(DeprecationExceptionMixin):
    pass


class TabularInline(DeprecationExceptionMixin):
    pass


class GroupedInline(DeprecationExceptionMixin):
    pass


class ClientModelAdmin(DeprecationExceptionMixin):
    pass


class GenericAdminModelAdmin(DeprecationExceptionMixin):
    pass


class BaseGenericModelAdmin(DeprecationExceptionMixin):
    pass
