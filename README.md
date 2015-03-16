![Concentric Sky](http://concentricsky.com/media/uploads/images/csky_logo.jpg)

# Client Admin for Django

Client Admin is an open source project developed by [Concentric Sky](https://concentricsky.com) that enhances Django Admin by providing organization tools and features that make the interface more appropriate for clients. Some of the code started as
  [Admin Tools](https://bitbucket.org/izi/django-admin-tools/overview), although the theming engine has been removed and many features have been added.


### Table of Contents
- [Version History](#version-history)
- [Documentation](#documentation)
- [Installation](#installation)
- [Getting Started](#getting-started)
  - [Features](#default-features)
  - [Removed as of 2.0](#removed-as-of-2.0)
- [License](#license)
- [About Concentric Sky](#about-concentric-sky)


## Version History
- v2.0.0  Do one thing well; Client Admin now focuses solely on theme features. Antiquated admin enhancements, and widgets, decoupled into requirements.
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

    ...

### Features
- Provides a new style for the Django Admin interface.
- Provides a dashboard with draggable widgets.
- Creates a menu persistent on all admin pages.
- Provides a system of admin bookmarks that allow users to quickly star favorite pages and have them available from the menu.
- Allows admin templates to extend Jinja2 templates. Assuming certain blocks are present
- Adds an advanced search form to change list views.

### Removed as of 2.0
- Provides a ClientModelAdmin class to inherit from that improves default widgets and settings.
- Provides an additional inline type, Grouped, that acts much like a Stacked inline but floats each field group instead of clearing them.
in your template, this means the admin interface could inherit a header and footer from the front-end templates.
- Provides nested inline formsets for ModelAdmin classes.
- Provides an improved Raw ID foreignkey widget that displays unicode instead of the object's pk.
- Includes revision history and deleted object recovery via django-reversion


## License

This project is licensed under the Apache License, Version 2.0. Details can be found in the LICENSE.md file.


## About Concentric Sky

_For nearly a decade, Concentric Sky has been building technology solutions that impact people everywhere. We work in the mobile, enterprise and web application spaces. Our team, based in Eugene Oregon, loves to solve complex problems. Concentric Sky believes in contributing back to our community and one of the ways we do that is by open sourcing our code on GitHub. Contact Concentric Sky at hello@concentricsky.com._
