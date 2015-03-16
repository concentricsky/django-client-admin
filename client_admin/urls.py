# Copyright 2015 Concentric Sky, Inc.
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

    url(r'^$', client_admin_views.dashboard, name='client_admin_dashboard'),
)
