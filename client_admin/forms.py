from django import forms
import urllib
from client_admin.models import DashboardPreferences
from client_admin.models import Bookmark


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
