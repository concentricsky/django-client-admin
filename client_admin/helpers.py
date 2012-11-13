import math
import jingo
import jinja2
import string
from client_admin.menu import items, Menu
from client_admin.menu.models import Bookmark
from client_admin.dashboard.dashboards import Dashboard
from client_admin.dashboard.models import DashboardPreferences
from django.utils.importlib import import_module
from django.conf import settings
from django import template
from django.db.models import Model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse


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
    model_name = obj._meta.module_name
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
    menu = Menu()
    menu.init_with_context(context)
    has_bookmark_item = False
    bookmark = None
    if len([c for c in menu.children if isinstance(c, items.Bookmarks)]) > 0:
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
    return [ dashboard, preferences, math.ceil(float(len(dashboard.children))/float(dashboard.columns)), len([m for m in dashboard.children \
                                if not m.enabled]) > 0]


@jingo.register.inclusion_tag('client_admin/frontend/menu.html')
@jinja2.contextfunction
def frontend_admin_menu(jinja_context):
    """
    Adds an admin menu to a frontend template
    """
    # make a mutable context
    context = {}
    context.update(jinja_context)

    # add an edit link for detail pages
    obj = context.get('object', None)
    if obj: 
        app_label = obj._meta.app_label
        model_name = obj._meta.module_name
        context['admin_change_link'] = reverse('admin:%s_%s_change' % (app_label, model_name), args=(obj.id,))

    # add a changelist link for list pages and detail pages
    obj_list = context.get('object_list', None)
    if obj_list:
        obj = obj_list[0]
    if obj:        
        app_label = obj._meta.app_label
        model_name = obj._meta.module_name
        context['admin_add_link'] = reverse('admin:%s_%s_add' % (app_label, model_name))
        context['admin_changelist_link'] = reverse('admin:%s_%s_changelist' % (app_label, model_name))
        context['admin_changelist_link_name'] = string.capwords(obj._meta.verbose_name)
        context['admin_changelist_link_name_plural'] = string.capwords(obj._meta.verbose_name_plural)

    return context
