"""
Admin ui common utilities.
"""
import types
from fnmatch import fnmatch

from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.importlib import import_module
import warnings

def uniquify(value, seen_values):
    """ Adds value to seen_values set and ensures it is unique """
    id = 1
    new_value = value
    while new_value in seen_values:
        new_value = "%s%s" % (value, id)
        id += 1
    seen_values.add(new_value)
    return new_value

def get_admin_object_change_url(obj):
    info = obj._meta.app_label, obj._meta.module_name
    return reverse('admin:%s_%s_change' % info, args=(obj.id,))


def get_admin_app_list_url(model):
    return reverse('admin:app_list', args=(model._meta.app_label,))

def get_admin_change_url(model):
    return reverse('admin:%s_%s_changelist' % (model._meta.app_label,
                                            model.__name__.lower()))

def get_admin_add_url(model):
    return reverse('admin:%s_%s_add' % (model._meta.app_label,
                                     model.__name__.lower()))


def get_avail_models(request):
    """ Returns (model, perm,) for all models user can possibly see """
    items = []

    for model, model_admin in admin.site._registry.items():
        perms = model_admin.get_model_perms(request)
        if True not in perms.values():
            continue
        items.append((model, perms,))
    return items

def filter_models(request, models, exclude):
    """
    Returns (model, perm,) for all models that match models/exclude patterns
    and are visible by current user.
    """
    items = get_avail_models(request)
    included = []
    full_name = lambda model: '%s.%s' % (model.__module__, model.__name__)

    # I beleive that that implemented
    # O(len(patterns)*len(matched_patterns)*len(all_models))
    # algorythm is fine for model lists because they are small and admin
    # performance is not a bottleneck. If it is not the case then the code
    # should be optimized.

    if len(models) == 0:
        included = items
    else:
        for pattern in models:
            for item in items:
                model, perms = item
                if fnmatch(full_name(model), pattern) and item not in included:
                    included.append(item)

    result = included[:]
    for pattern in exclude:
        for item in included:
            model, perms = item
            if fnmatch(full_name(model), pattern):
                result.remove(item)
    return result


class AppListElementMixin(object):
    """
    Mixin class used by both the AppListDashboardModule and the
    AppListMenuItem (to honor the DRY concept).
    """

    def _visible_models(self, request):
        included = self.models[:]
        excluded = self.exclude[:]
        return filter_models(request, included, excluded)


def get_media_url():
    """
    Returns the django client admin media URL.
    """
    media_url = getattr(settings, 'CLIENT_ADMIN_MEDIA_URL', None)
    if media_url is None:
        media_url = getattr(settings, 'STATIC_URL', None)
    if media_url is None:
        media_url = getattr(settings, 'MEDIA_URL')
    return media_url.rstrip('/')
