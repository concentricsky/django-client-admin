Client Admin Features
=====================


Default Features
-----------------
- Provides a new style for the Django Admin interface.
- Provides a dashboard with draggable widgets.
- Creates a menu persistent on all admin pages.
- Provides a system of admin bookmarks that allow users to quickly star favorite pages and have them available from the menu.
- Provides a ClientModelAdmin class to inherit from that improves default widgets and settings.
- Provides an additional inline type, Grouped, that acts much like a Stacked inline but floats each field group instead of clearing them.
- Allows admin templates to extend Jinja2 templates. Assuming certain blocks are present in your template, this means the admin interface could inherit a header and footer from the front-end templates.


Additional Features
--------------------
- Provides nested inline formsets for ModelAdmin classes.
- Adds an advanced search form to change list views.
- Provides an improved generic-foreignkey widget.
- Provides an improved Raw ID foreignkey widget that displays unicode instead of the object's pk.
- Includes revision history and deleted object recovery via django-reversion


.. toctree::
  :maxdepth: 2

  dashboard
  advanced-search
