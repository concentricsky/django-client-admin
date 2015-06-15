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

import math
import jingo
import jinja2
from client_admin.items import Bookmarks
from client_admin.models import DashboardPreferences, Bookmark
from client_admin.menus import Menu
from client_admin.dashboards import Dashboard
from django.utils.importlib import import_module
from django.conf import settings
from django import template
from django.db.models import Model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.cache import get_cache

if get_cache.__module__.startswith('debug_toolbar'):
    try:
        from debug_toolbar.panels.cache import get_cache
    except ImportError:
        # for debugtoolbar < 1.0
        try:
            from debug_toolbar.panels.cache import base_get_cache as get_cache
        except:
            pass


def check_permission(request, mode_name, app_label, model_name):
    '''
    Check for proper permissions. mode_name may be either add, change or delete.
    '''
    p = '%s.%s_%s' % (app_label, mode_name, model_name)
    return request.user.is_active and request.user.has_perm(p)


@jingo.register.function
@jinja2.contextfunction
def edit_link(context, obj, label='Edit'):

    # Check if `model_object` is a model-instance
    if not isinstance(obj, Model):
        raise template.TemplateSyntaxError, "'%s' argument must be a model-instance" % obj

    app_label = obj._meta.app_label
    model_name = obj._meta.model_name
    edit_link = reverse('admin:%s_%s_change' % (app_label, model_name), args=(obj.id,))

    if check_permission(request=context['request'], mode_name='change', app_label=app_label, model_name=model_name):
        return '<a href="%s" target="_blank">%s</a>' % (edit_link, label)
    return None


@jingo.register.function
def get_generic_relation_list(request):
    """
    Returns a list of installed applications and models for which the current user
    has at least one permission.

    Syntax::
        {{ get_generic_relation_list }}
    """
    return_string = "var MODEL_URL_ARRAY = {"
    for c in ContentType.objects.all().order_by('id'):
        return_string = "%s%d: '%s.%s'," % (return_string, c.id, c.app_label, c.model)
    return_string = "%s}" % return_string[:-1]
    return return_string


# # get\_menu(context)

# To use:
#
#       {% set menu, has_bookmark_item, bookmark = get_menu() %}
#
# This helper receives context from a Jinja2 template and returns:
@jingo.register.function
@jinja2.contextfunction
def get_menu(context):
    if not context['request'].user.is_staff:
        return [None, None, None]

    # - an instance of the menu
    menu_cls = getattr(settings, 'CLIENT_ADMIN_MENU', None)
    if menu_cls:
        try:
            mod, inst = menu_cls.rsplit('.', 1)
            mod = import_module(mod)
            menu = getattr(mod, inst)()
        except:
            menu = Menu()
    else:
        menu = Menu()

    menu.init_with_context(context)
    has_bookmark_item = False
    bookmark = None
    if len([c for c in menu.children if isinstance(c, Bookmarks)]) > 0:
        # - if the user has any bookmarks
        has_bookmark_item = True
        url = context['request'].get_full_path()
        try:
            # - this user's bookmark of this page
            bookmark = Bookmark.objects.filter(user=context['request'].user, url=url)[0]
        except:
            pass
    return [menu, has_bookmark_item, bookmark]


# # get\_current\_dashboard(context)

# To use:
#
#       {% set dashboard, dashboard_preferences, split_at, has_disabled_modules = get_current_dashboard() %}
#
# This helper receives context from a Jinja2 template and returns:

@jingo.register.function
@jinja2.contextfunction
def get_current_dashboard(context):
    """
    Adds the Dashboard context to a template
    """
    if not context['request'].user.is_staff:
        return [None, None, None, None]
    # - an instance of the dashboard

    dashboard_cls = getattr(settings, 'CLIENT_ADMIN_DASHBOARD', None)
    if dashboard_cls:
        try:
            mod, inst = dashboard_cls.rsplit('.', 1)
            mod = import_module(mod)
            dashboard = getattr(mod, inst)()
        except:
            dashboard = Dashboard()
    else:
        dashboard = Dashboard()

    dashboard.init_with_context(context)
    dashboard._prepare_children()
    dashboard.init_children_with_context(context)
    try:
        # - the user's dashboard preferences
        preferences = DashboardPreferences.objects.get(
            user=context['request'].user,
            dashboard_id=dashboard.get_id()
        ).data
    except DashboardPreferences.DoesNotExist:
        preferences = '{}'
        DashboardPreferences(
            user=context['request'].user,
            dashboard_id=dashboard.get_id(),
            data=preferences
        ).save()
    # - where the modules should be split for a two-column view
    # - which modules have been disabled
    return [
        dashboard,
        preferences,
        math.ceil(float(len(dashboard.children))/float(dashboard.columns)),
        len([m for m in dashboard.children if not m.enabled]) > 0
    ]


@jingo.register.filter
def prettyname(name):
    return ' '.join([word.capitalize() for word in name.split('_')])


@jingo.register.filter
def prettyvalue(value, key):
    return PrettyValue().format(key, value)


class PrettyValue(object):
    """
    Helper class that reformats the value. Looks for a method named
    ``format_<key>_value`` and returns that value. Returns the value
    as is, if no format method is found.
    """

    def format(self, key, value):
        try:
            func = getattr(self, 'format_%s_value' % key.lower())
            return func(value)
        except AttributeError:
            return value

    def format_limit_maxbytes_value(self, value):
        return "%s (%s)" % (value, self.human_bytes(value))

    def format_bytes_read_value(self, value):
        return "%s (%s)" % (value, self.human_bytes(value))

    def format_bytes_written_value(self, value):
        return "%s (%s)" % (value, self.human_bytes(value))

    def format_uptime_value(self, value):
        return self.fract_timestamp(int(value))

    def format_time_value(self, value):
        from datetime import datetime
        return datetime.fromtimestamp(int(value)).strftime('%x %X')

    def fract_timestamp(self, s):
        years, s = divmod(s, 31556952)
        min, s = divmod(s, 60)
        h, min = divmod(min, 60)
        d, h = divmod(h, 24)
        return '%sy, %sd, %sh, %sm, %ss' % (years, d, h, min, s)

    def human_bytes(self, bytes):
        bytes = float(bytes)
        if bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2fGB' % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2fMB' % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = '%.2fKB' % kilobytes
        else:
            size = '%.2fB' % bytes
        return size


@jingo.register.function
def widthratio(value, max_value, max_width):
    try:
        value = float(value)
        max_value = float(max_value)
        ratio = (value / max_value) * max_width
    except ZeroDivisionError:
        return '0'
    except (ValueError, TypeError):
        return ''
    return str(int(round(ratio)))
