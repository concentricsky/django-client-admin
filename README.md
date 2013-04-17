# Client Admin for Django

Client Admin enhances Django Admin. Much of the code started as 
[Admin Tools](https://bitbucket.org/izi/django-admin-tools/overview). The Admin Tools theming engine has been removed, and many features have been modified.


## What does it give you by default?

- Provides a new style for the Django Admin interface.

- Provides a dashboard with draggable widgets

- Creates a menu persistent on all admin pages

- Provides a system of admin bookmarks that allow users to quickly star favorite pages and have them available from the menu

- Provides a ModelAdmin class to inherit from that improves default widgets and settings

- Provides nested inline formsets for ModelAdmin classes

- Provides an additional inline type, Grouped, that acts much like a Stacked inline but floats each field group instead of clearing them.

## Additional features:

- Creates a sitemap module for the dashboard.

- Provides an improved generic-foreignkey widget.

- Provides an improved Raw ID foreignkey widget that displays unicode instead of the object's pk.

- Allows admin templates to extend Jinja2 templates. Assuming certain blocks are present 
in your template, this means the admin interface could inherit a header and footer from the front-end templates.

- Includes revision history and deleted object recovery via django-reversion


## How to install?

Client Admin 

    pip install git+https://github.com/concentricsky/django-client-admin.git#egg=client_admin

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


To access media files, you should use the staticfiles contrib application introduced in Django 1.3.


### Customizations

- Override the page logo

- Override the large logo on the login screen



## Dashboard widgets


### Sitemap

By default, Client Admin will look for a menu from Sky CMS with an id of 1.


### Recent Activity

The Recent Activity module lists all activity registered to the 

### Quick Links


## Recursive Inlines

Basic Django admin allows for a model to be edited inline with a related model, but it is limited to one level of nesting. Client Admin provides several classes that allow inlines to be nested recursively.

### Example

    class AwardInline(admin.StackedInline):
        model = Award
    
    class ChapterInline(admin.TabularInline):
        model = Chapter
    
    class BookInline(client_admin.StackedRecursiveInline):
        model = Book
        inlines = [ChapterInline]
    
    class AuthorAdmin(client_admin.RecursiveInlinesModelAdmin):
        model = Author
        inlines = [BookInline, AwardInline]


## Best Practices

- Create a 'staff' user that belongs to a 'staff' group with limited permissions. 

    - The staff group should have access to:

        - Editing and creating all site-specific structured content

        - Deleting any structured content that is used as an inline

    - The staff group should _not_ have access to:

        - Deleting any structured content that would cascade delete. Instead, have them use the 'is_active' flag to remove content from the front end.

        - Administration apps like Auth and Sites


## What's in the works?

Client Admin wants to:

- Create a Jinja2 helper that would print the admin menu bar on front-end templates. This would most likely be inserted dynamically and position absolutely to maintain the existing front-end structure.

- Create Jinja2 helpers that insert links to corresponding admin pages for content. Again, these would most likely be inserted dynamically and position absolutely to maintain the existing front-end structure.

- Provide a modal interface to edit WYSIWYG fields (currently CKEditor) directly from the front end. 

- Support including foreign keys and many-to-many relationships as inlines on a change form. This would mean the original field would be excluded in the main form, and the inverse inlines would be saved first, with their resulting PKs saved as the value for the corresponding relationship on the main form.

- Support for nested inlines using AJAX submissions of inline forms instead of nested formsets.
