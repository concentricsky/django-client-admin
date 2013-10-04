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

"""
Module where client admin menu classes are defined.
"""
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from client_admin import items


class Menu(object):
    template = 'client_admin/menu/menu.html'
    children = None
    site_logo = None

    class Media:
        css = ()
        js  = ()

    def __init__(self, **kwargs):
        self.site_logo = getattr(settings, 'CLIENT_ADMIN_LOGO', None)
        for key in kwargs:
            if hasattr(self.__class__, key):
                setattr(self, key, kwargs[key])
        self.children = kwargs.get('children', [])

    def init_with_context(self, context):

        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.AppList(
                _('Content'),
                exclude=('django.contrib.*',)
            ),
            items.AppList(
                _('Administration'),
                models=('django.contrib.*',)
            ),
            items.Bookmarks(),
            items.MenuItem(
                _('Account'),
                css_classes=('user-tools',),
                children=(
                    items.MenuItem( _('Change password'), reverse('admin:password_change') )
                    , items.MenuItem( _('Log out'), reverse('admin:logout') )
                    #, items.MenuItem( _('Documentation'), reverse('admin:django-admindocs-docroot') )
                ),
            ),
        ]
        for child in self.children:
            child.init_with_context(context)
