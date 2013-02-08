from django.db import models
from django.conf import settings

class DashboardPreferences(models.Model):
    """
    This model represents the dashboard preferences for a user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    data = models.TextField()
    dashboard_id = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s dashboard preferences" % self.user.username

    class Meta:
        db_table = 'client_admin_dashboard_preferences'
        ordering = ('user',)