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
            items.Bookmarks(),
            items.AppList(
                _('Content'),
                exclude=('django.contrib.*',)
            ),
            items.AppList(
                _('Administration'),
                models=('django.contrib.*',)
            ),
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