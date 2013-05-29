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
Module where client admin dashboard classes are defined.
"""

from django.template.defaultfilters import slugify
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from client_admin import modules
from client_admin.utils import uniquify


class Dashboard(object):
    """
    Base class for dashboards.
    The Dashboard class is a simple python list that has three additional
    properties:

    ``title``
        The dashboard title, by default, it is displayed above the dashboard
        in a ``h2`` tag. Default value: 'Dashboard'.

    ``template``
        The template to use to render the dashboard.
        Default value: 'client_admin/dashboard/dashboard.html'

    ``columns``
        An integer that represents the number of columns for the dashboard.
        Default value: 2.
    """

    title = _('Dashboard')
    template = 'client_admin/dashboard/dashboard.html'
    columns = 2
    children = None

    class Media:
        css = ()
        js = ['admin/js/jquery.min.js', 'admin/js/jquery.init.js', 'admin/js/inlines.min.js']

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self.__class__, key):
                setattr(self, key, kwargs[key])
        self.children = self.children or []

    def init_with_context(self, context):
        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('django.contrib.*',),
            enabled=False,
        ))
        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('Administration'),
            models=('django.contrib.*',),
            enabled=False,
        ))
        # TODO: aslo append a link to google analytics if an ID is in settings
        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            _('Quick links'),
            layout='inline',
            #draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                [_('Return to site'), '/'],
                [_('Change password'),
                 reverse('admin:password_change')],
                [_('Log out'), reverse('admin:logout')],
            ]
        ))
        # append a recent actions module
        #self.children.append(modules.RecentActions(_('My Actions'), 5))
        # append an all actions module
        self.children.append(modules.AllRecentActions(
            _('Recent Activity') 
            , 10
            , css_classes=('activity',)
        ))

        self.children.append(modules.MemcachedStatus())


    def get_id(self):
        """
        Internal method used to distinguish different dashboards in js code.
        """
        return 'dashboard'

    def _prepare_children(self):
        """ Enumerates children without explicit id """
        seen = set()
        for id, module in enumerate(self.children):
            module.id = uniquify(module.id or str(id+1), seen)
            module._prepare_children()
    
    def init_children_with_context(self, context):
        for module in self.children:
            module.init_with_context(context)

