try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url
from client_admin import views as client_admin_views

urls = []


urlpatterns = patterns(
    '',
    url(r'^menu/add_bookmark/$', client_admin_views.add_bookmark, name='client-admin-menu-add-bookmark'),
    url(r'^menu/edit_bookmark/(?P<id>.+)/$', client_admin_views.edit_bookmark, name='client-admin-menu-edit-bookmark'),
    url(r'^menu/remove_bookmark/(?P<id>.+)/$', client_admin_views.remove_bookmark, name='client-admin-menu-remove-bookmark'),

    url(r'^dashboard/set_preferences/(?P<dashboard_id>.+)/$', client_admin_views.set_preferences, name='client-admin-dashboard-set-preferences'),

    url(r'^obj/$', client_admin_views.generic_lookup, name='admin_genericadmin_obj_lookup'),
    #url(r'^get-generic-rel-list/$', client_admin_views.get_generic_rel_list, name='admin_genericadmin_rel_list'),

    url(r'^$', client_admin_views.dashboard, name='client_admin_dashboard'),
)
