from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('client_admin.dashboard.views',
    url(r'^set_preferences/(?P<dashboard_id>.+)/$', 'set_preferences', name='client-admin-dashboard-set-preferences'),
)
