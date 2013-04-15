try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('client_admin.menu.views',
    url(r'^add_bookmark/$', 'add_bookmark', name='client-admin-menu-add-bookmark'),
    url(r'^edit_bookmark/(?P<id>.+)/$', 'edit_bookmark', name='client-admin-menu-edit-bookmark'),
    url(r'^remove_bookmark/(?P<id>.+)/$', 'remove_bookmark', name='client-admin-menu-remove-bookmark'),
)
