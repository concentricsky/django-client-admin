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
from django.utils.encoding import smart_text

from client_admin.utils import get_admin_change_url


class LookupFilter(RelatedFieldListFilter):
    template = "admin/lookup_filter.html"

    def choices(self, cl):
        yield {
            'lookup_url': "%s?t=id" % get_admin_change_url(self.field.rel.to),
            'query_string': cl.get_query_string({self.lookup_kwarg: "PLACEHOLDER"}),
            'filter_name': self.field.rel.to._meta.module_name,
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
