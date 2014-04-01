Installation
=================

    pip install git+https://github.com/concentricsky/django-client-admin.git

Include Client Admin in your settings.py. It should be listed before the django.contrib.admin module so that client_admin can override the default Django admin templates.

.. code-block:: python

    INSTALLED_APPS = [
        'client_admin',

        ...

    ]

Include Client Admin urls in your urls.py at the same path as normal contrib.admin

.. code-block:: python

    urlpatterns = patterns('',

        ...

        url(r'^admin/', include('client_admin.urls')),
        url(r'^admin/', include('admin.site.urls')),

        ...

    )

Import and inherit from ClientModelAdmin and Inline classes.

.. code-block:: python

    from client_admin.admin import ClientModelAdmin, GroupedInline, TabularInline, StackedInline


    class BindingInline(GroupedInline):
        model = Binding


    class RetailerInline(TabularInline):
        model = Retailer


    class AuthorInline(StackedInline):
        model = Author


    class BookAdmin(ClientModelAdmin):
        inlines = [PhoneNumberInline, RetailerInline, MailingAddressInline]

    ...


Customization
---------------

Branding Client Admin for each project can be done by providing a replacement header menu logo. In the project's static folder, create a client_admin/images/h1_logo_bg.png that is 40px tall and no more than 400px wide.



Best Practices
----------------

- Create a 'staff' user that belongs to a 'staff' group with limited permissions.
    - The staff group should have access to:
        - Editing and creating all site-specific structured content
        - Deleting any structured content that is used as an inline
    - The staff group should _not_ have access to:
        - Deleting any structured content that would cascade delete. Instead, have them use an 'is_active' flag to remove content from the front end.
        - Administration apps like Auth and Sites



.. toctree::
  :maxdepth: 2
