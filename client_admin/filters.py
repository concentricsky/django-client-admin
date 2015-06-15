# Copyright 2013 Concentric Sky, Inc.
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

from django.contrib.admin import RelatedFieldListFilter, ChoicesFieldListFilter
from django.contrib.admin.util import get_model_from_relation
from django.utils.encoding import smart_text

from client_admin.utils import get_admin_change_url



class LookupFilter(RelatedFieldListFilter):
    template = "admin/lookup_filter.html"

    def __init__(self, field, request, params, model, model_admin, field_path):
        """cut/pasted from RelatedFieldListFilter parent constructor, with db hit removed"""
        other_model = get_model_from_relation(field)
        if hasattr(field, 'rel'):
            rel_name = field.rel.get_related_field().name
        else:
            rel_name = other_model._meta.pk.name
        self.lookup_kwarg = '%s__%s__exact' % (field_path, rel_name)
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull, None)

        # this is the one change from the parent constructor. 
        # instead of getting all choices from the table, only pick one if theres already one set so we can display it
        self.lookup_choices = [(-1,""),(-2,"")]  # needs at least TWO or admin wont show it if empty.
        if self.lookup_val:
            try:
                obj = field.rel.to.objects.get(pk=self.lookup_val)
                val = obj.__unicode__()
            except field.rel.to.DoesNotExist:
                val = ""
                pass
            self.lookup_choices.append((self.lookup_val,val))

        # note we are deliberately calling our parent's parent constructor
        super(RelatedFieldListFilter, self).__init__(field, request, params, model, model_admin, field_path)

        if hasattr(field, 'verbose_name'):
            self.lookup_title = field.verbose_name
        else:
            self.lookup_title = other_model._meta.verbose_name
        self.title = self.lookup_title


    def choices(self, cl):
        yield {
            'lookup_url': "%s?t=id" % get_admin_change_url(self.field.rel.to),
            'query_string': cl.get_query_string({self.lookup_kwarg: "PLACEHOLDER"}),
            'filter_name': self.field.rel.to._meta.model_name,
        }
        for pk_val, val in self.lookup_choices:
            if self.lookup_val == smart_text(pk_val):
                yield {
                    'selected': self.lookup_val == smart_text(pk_val),
                    'query_string': cl.get_query_string({
                        self.lookup_kwarg: pk_val,
                    }, [self.lookup_kwarg_isnull]),
                    'display': val,
                }
        if self.lookup_val:
            yield {
                'selected': not self.lookup_val,
                'query_string': '?',
                'display': 'Remove filter',
            }



class SelectFilter(ChoicesFieldListFilter):
    template = "admin/select_filter.html"
