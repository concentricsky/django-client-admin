What's in the works?
=====================

Structure
---------------

- Responsive templates
- All views re-written as class-based
- Abstracting list views as reusable ModelTables

Features
---------------

- Create a Jinja2 helper that would print the admin menu bar on front-end templates. This would most likely be inserted dynamically and position absolutely to maintain the existing front-end structure.
- Create Jinja2 helpers that insert links to corresponding admin pages for content displayed in front-end templates. Again, these would most likely be inserted dynamically and position absolutely to maintain the existing front-end structure.
- Provide a modal interface to edit WYSIWYG fields (currently CKEditor) directly from the front end.
- Support including foreign keys and many-to-many relationships as inlines on a change form. This would mean the original field would be excluded in the main form, and the inverse inlines would be saved first, with their resulting PKs saved as the value for the corresponding relationship on the main form.
- Support for nested inlines using AJAX submissions of inline forms instead of nested formsets.


.. toctree::
  :maxdepth: 2
