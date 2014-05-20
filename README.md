![Concentric Sky](http://concentricsky.com/media/uploads/images/csky_logo.jpg)

# Client Admin for Django

Client Admin is an open source project developed by [Concentric Sky](https://concentricsky.com) that enhances Django Admin by providing organization tools and features that make the interface more appropriate for clients. Some of the code started as
  [Admin Tools](https://bitbucket.org/izi/django-admin-tools/overview), although the theming engine has been removed and many features have been added.


### Table of Contents
- [Version History](#version-history)
- [Documentation](#documentation)
- [Installation](#installation)
- [Getting Started](#getting-started)
  - [Default Features](#default-features)
  - [Additional Features](#additional-features)
- [License](#license)
- [About Concentric Sky](#about-concentric-sky)


## Version History
- v1.0.11 Various bug fixes and style changes
- v1.0.0 Public codebase was released


## Documentation

Detailed documentation is available on [Read The Docs](http://client-admin-for-django.readthedocs.org/en/latest/).


## Installation

    pip install git+https://github.com/concentricsky/django-client-admin.git

Include Client Admin in your settings.py. It should be listed before the django.contrib.admin module so that client_admin can override the default Django admin templates.

    INSTALLED_APPS = [
        'client_admin',

        ...

    ]

Include Client Admin urls in your urls.py at the same path as normal contrib.admin

    urlpatterns = patterns('',

        ...

        url(r'^admin/', include('client_admin.urls')),
        url(r'^admin/', include('admin.site.urls')),

        ...

    )


Client Admin depends on Jingo to process Jinja2 templates. Please follow the installation instructions according to that library (available at https://jingo.readthedocs.org/en/latest/), and be sure to include contrib.admin in the excluded apps setting:

    JINGO_EXCLUDE_APPS = ( 'admin',)


## Getting Started

Import and inherit from ClientModelAdmin and Inline classes.

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

### Default Features
- Provides a new style for the Django Admin interface.
- Provides a dashboard with draggable widgets.
- Creates a menu persistent on all admin pages.
- Provides a system of admin bookmarks that allow users to quickly star favorite pages and have them available from the menu.
- Provides a ClientModelAdmin class to inherit from that improves default widgets and settings.
- Provides an additional inline type, Grouped, that acts much like a Stacked inline but floats each field group instead of clearing them.
- Allows admin templates to extend Jinja2 templates. Assuming certain blocks are present
in your template, this means the admin interface could inherit a header and footer from the front-end templates.


### Additional Features
- Provides nested inline formsets for ModelAdmin classes.
- Adds an advanced search form to change list views.
- Provides an improved generic-foreignkey widget.
- Provides an improved Raw ID foreignkey widget that displays unicode instead of the object's pk.
- Includes revision history and deleted object recovery via django-reversion


## License

This project is licensed under the Apache License, Version 2.0. Details can be found in the LICENSE.md file.


## About Concentric Sky

_For nearly a decade, Concentric Sky has been building technology solutions that impact people everywhere. We work in the mobile, enterprise and web application spaces. Our team, based in Eugene Oregon, loves to solve complex problems. Concentric Sky believes in contributing back to our community and one of the ways we do that is by open sourcing our code on GitHub. Contact Concentric Sky at hello@concentricsky.com._
