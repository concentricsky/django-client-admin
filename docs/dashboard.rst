Dashboard Widgets
=================

App List
---------------

The App List module shows a list of models with links to add objects or show the change-list view for the model. The list can be limited to either show or exclude certain apps or models. By default, two instances of App Lists are included on the dashboard, one showing all models that aren't part of the django.contrib app and one showing only those from django.contrib.

Link List
---------------

The Link List module displays a list of hrefs that can either be external urls or internal urls using the reverse() function.

Memcached Status
-------------------

If memcached is being used on the server, then this module displays detailed statistics from each memcached instance.

Recent Activity
------------------

The Recent Activity module lists all LogEntry objects, grouped by which user generated them. Normally, the LogEntry objects are only created from admin activity, but this can also be used to display activity generated from the front-end of the site if those views create LogEntry objects using the log_action() function.

Sitemap
---------------

The sitemap module allows listing models in a hierarchy similar to a front-end site menu. This allows admin users to find content in the same logical place that a front-end user would see. By default, Client Admin will build the hierarchy based on a menu from Sky CMS, currently a private library. This code will eventually be pulled out of Client Admin and only included in Sky CMS.


Recursive Inlines

Basic Django admin allows for a model to be edited inline with a related model, but it is limited to one level of nesting. Client Admin provides several classes that allow inlines to be nested recursively.

Example:


    class ChapterInline(admin.TabularInline):
        model = Chapter

    class BookInline(client_admin.StackedInline):
        model = Book
        inlines = [ChapterInline]

    class AuthorAdmin(client_admin.RecursiveInlinesModelAdmin):
        model = Author
        inlines = [BookInline, AwardInline]

By default `RecursiveInlinesModelAdmin` is inherited by `ClientModelAdmin`. This example is only to demonstrate how to use the class on its own. Normally, only `ClientModelAdmin` and the inline classes from Client Admin would be used.


.. toctree::
  :maxdepth: 2
