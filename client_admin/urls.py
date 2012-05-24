from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from client_admin import views as client_admin_views

urls = []

urlpatterns = patterns('',
    url(r'^menu/', include('client_admin.menu.urls')),
    url(r'^dashboard/', include('client_admin.dashboard.urls')),

    url(r'^obj/$', client_admin_views.generic_lookup, name='admin_genericadmin_obj_lookup'),
    #url(r'^get-generic-rel-list/$', client_admin_views.get_generic_rel_list, name='admin_genericadmin_rel_list'),

    url(r'^$', client_admin_views.dashboard, name='client_admin_dashboard'),
)