from django.db import models
from django.contrib.auth import get_user_model


class Bookmark(models.Model):
    """
    This model represents a user created bookmark.
    """
    user = models.ForeignKey(get_user_model())
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s - %s" % (self.title, self.url)

    class Meta:
        db_table = 'client_admin_menu_bookmark'
        ordering = ('id',)


class DashboardPreferences(models.Model):
    """
    This model represents the dashboard preferences for a user.
    """
    user = models.ForeignKey(get_user_model())
    data = models.TextField()
    dashboard_id = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s dashboard preferences" % self.user.username

    class Meta:
        db_table = 'client_admin_dashboard_preferences'
        ordering = ('user',)
