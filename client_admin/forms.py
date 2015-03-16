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

import urllib

from django import forms

from client_admin.models import DashboardPreferences, Bookmark


class DashboardPreferencesForm(forms.ModelForm):
    """
    This form allows the user to edit dashboard preferences. It doesn't show
    the user field. It expects the user to be passed in from the view.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.dashboard_id = kwargs.pop('dashboard_id', None)
        super(DashboardPreferencesForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        preferences = super(DashboardPreferencesForm, self).save(
            commit=False,
            *args,
            **kwargs
        )
        preferences.user = self.user
        preferences.dashboard_id = self.dashboard_id
        preferences.save()
        return preferences

    class Meta:
        fields = ('data',)
        model = DashboardPreferences


class BookmarkForm(forms.ModelForm):
    """
    This form allows the user to edit bookmarks. It doesn't show the user field.
    It expects the user to be passed in from the view.
    """

    def __init__(self, user, *args, **kwargs):
        super(BookmarkForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_url(self):
        url = self.cleaned_data['url']
        return urllib.unquote(url)

    def save(self, *args, **kwargs):
        bookmark = super(BookmarkForm, self).save(commit=False, *args, **kwargs)
        bookmark.user = self.user
        bookmark.save()
        return bookmark

    class Meta:
        fields = ('url', 'title')
        model = Bookmark
