Advanced Search
=================

If search fields are provided to a ClientModelAdmin class, they will automatically be included in an advanced search form that gets appended to the change list template but hidden by default. A link will be added just below the normal search form in the sidebar to expand the advanced search form. All search fields will be listed, including properties of foreignkey and many-to-many fields. The form field labels are automatically generated for related fields as `<model> <field>` but can be overridden using a property on the admin class of `advanced_search_titles`.

Example:

.. code-block:: python

    class AwardInline(admin.StackedInline):
        model = Award

    class BookInline(StackedInline):
        model = Book

    class AuthorAdmin(client_admin.RecursiveInlinesModelAdmin):
        model = Author
        search_fields = ('name', 'book_set__title', 'award_set__name')
        advanced_search_titles = {
            'book_set__title': 'Titles',
            'award_set__name': 'Awards'
        }


.. toctree::
  :maxdepth: 2
