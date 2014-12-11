# Copyright 2013 Concentric Sky, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# # Client Admin admin classes
from client_admin.views import generic_lookup, get_generic_rel_list
from client_admin.widgets import ThumbnailImageWidget, AdminURLFieldWidget, UnicodeForeignKeyRawIdWidget

import re

from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.options import get_ul_class, IS_POPUP_VAR
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.util import unquote
from django.contrib.admin.widgets import AdminRadioSelect
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import ImageField, ManyToManyField, FieldDoesNotExist, URLField
from django.forms import Form
from django.forms.fields import CharField
from django.forms.formsets import all_valid
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

csrf_protect_m = method_decorator(csrf_protect)

JS_PATH = getattr(settings, 'GENERICADMIN_JS', 'client_admin/js/')


class EmptyVersionAdmin(object):
    pass

try:
    import reversion
    VersionAdmin = reversion.VersionAdmin
except:
    VersionAdmin = EmptyVersionAdmin


## Recursive Inlines!
## inspired in part by https://code.djangoproject.com/ticket/9025
class BaseRecursiveInlineMixin(object):
    inlines = []
    extra = 0

    def get_inline_instances(self, request, obj=None):
        for inline_class in self.inlines:
            inline = inline_class(self.model, self.admin_site)
            if request:
                if not (inline.has_add_permission(request) or
                        inline.has_change_permission(request) or
                        inline.has_delete_permission(request)):
                    continue
                if not inline.has_add_permission(request):
                    inline.max_num = 0
            yield inline


class RecursiveInlinesModelAdmin(admin.ModelAdmin):
    grouped_fields = []

    def __init__(self, model, admin_site):
        media = list(getattr(self.Media, 'js', ()))
        media.append(static('client_admin/js/recursiveinlines.js'))
        self.Media.js = tuple(media)
        super(RecursiveInlinesModelAdmin, self).__init__(model, admin_site)

    def save_formset(self, request, form, formset, change):
        for form in formset.forms:
            for recursive_formset in getattr(form, 'recursive_formsets', []):
                self.save_formset(request, form, recursive_formset, change=change)
        super(RecursiveInlinesModelAdmin, self).save_formset(request, form, formset, change=change)

    def add_recursive_inline_formsets(self, request, inline, formset, obj=None):
        for form in formset.forms:
            recursive_formsets = []
            if form.instance.pk:
                if hasattr(inline, 'get_inline_instances'):
                    for recursive_inline in inline.get_inline_instances(request, obj):
                        FormSet = recursive_inline.get_formset(request, form.instance)
                        prefix = "%s-%s" % (form.prefix, FormSet.get_default_prefix())
                        if request.method == 'POST':
                            recursive_formset = FormSet(request.POST, request.FILES, instance=form.instance, prefix=prefix, queryset=recursive_inline.queryset(request))
                        else:
                            recursive_formset = FormSet(instance=form.instance, prefix=prefix, queryset=recursive_inline.queryset(request))
                        recursive_formsets.append(recursive_formset)
                        if hasattr(recursive_inline, 'inlines'):
                            self.add_recursive_inline_formsets(request, recursive_inline, recursive_formset)
            form.recursive_formsets = recursive_formsets

    def wrap_recursive_inline_formsets(self, request, inline, formset, obj=None):
        media = None

        def get_media(extra_media):
            if media:
                return media + extra_media
            else:
                return extra_media

        for form in formset.forms:
            wrapped_recursive_formsets = []
            if hasattr(form, 'recursive_formsets') and hasattr(inline, 'get_inline_instances'):
                for recursive_inline, recursive_formset in zip(inline.get_inline_instances(request, obj), form.recursive_formsets):
                    fieldsets = list(recursive_inline.get_fieldsets(request))
                    readonly = list(recursive_inline.get_readonly_fields(request))
                    prepopulated = dict(recursive_inline.get_prepopulated_fields(request))
                    wrapped_recursive_formset = helpers.InlineAdminFormSet(recursive_inline, recursive_formset, fieldsets, prepopulated, readonly, model_admin=self)
                    wrapped_recursive_formsets.append(wrapped_recursive_formset)
                    media = get_media(wrapped_recursive_formset.media)
                    if hasattr(recursive_inline, 'inlines'):
                        media = media + get_media(self.wrap_recursive_inline_formsets(request, recursive_inline, recursive_formset))
            form.recursive_formsets = wrapped_recursive_formsets

        return media

    def all_valid(self, formsets):
        if not all_valid(formsets):
            return False
        for formset in formsets:
            if formset.is_bound:
                for form in formset:
                    if hasattr(form, 'recursive_formsets') and form.recursive_formsets:
                        if not self.all_valid(form.recursive_formsets):
                            return False
                        # gross gross gross
                        if not form.cleaned_data:
                            form._errors['__all__'] = form.error_class(["Parent object must be created when creating nested inlines."])
                            return False
        return True

    @csrf_protect_m
    @transaction.atomic
    def add_view(self, request, form_url='', extra_context={}):
        "The 'add' admin view for this model."
        #copied from django/contrib/admin/options.py:924 at version 1.4.0
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = self.get_form(request)
        formsets = []
        inline_instances = self.get_inline_instances(request)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():
                new_object = self.save_form(request, form, change=False)
                form_validated = True
            else:
                form_validated = False
                new_object = self.model()
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new="_saveasnew" in request.POST,
                                  prefix=prefix, queryset=inline.get_queryset(request))
                formsets.append(formset)
                if hasattr(inline, 'inlines') and inline.inlines:
                    self.add_recursive_inline_formsets(request, inline, formset)
            if self.all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, False)
                self.save_related(request, form, formsets, False)
                self.log_addition(request, new_object)
                return self.response_add(request, new_object)
        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())
            for k in initial:
                try:
                    f = opts.get_field(k)
                except FieldDoesNotExist:
                    continue
                if isinstance(f, ManyToManyField):
                    initial[k] = initial[k].split(",")
            form = ModelForm(initial=initial)
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=self.model(), prefix=prefix,
                                  queryset=inline.get_queryset(request))
                formsets.append(formset)
                if hasattr(inline, 'inlines') and hasattr(self, 'add_recursive_inline_formsets'):
                    self.add_recursive_inline_formsets(request, inline, formset)

        adminForm = helpers.AdminForm(form, list(
            self.get_fieldsets(request)),
            self.get_prepopulated_fields(request),
            self.get_readonly_fields(request),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request))
            readonly = list(inline.get_readonly_fields(request))
            prepopulated = dict(inline.get_prepopulated_fields(request))
            inline_admin_formset = helpers.InlineAdminFormSet(
                inline, formset, fieldsets, prepopulated,
                readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media
            if hasattr(inline, 'inlines'):
                media = media + self.wrap_recursive_inline_formsets(request, inline, formset)

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': IS_POPUP_VAR in request.REQUEST,
            'show_delete': False,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
            'preserved_filters': self.get_preserved_filters(request),

        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url, add=True)

    @csrf_protect_m
    @transaction.atomic
    def change_view(self, request, object_id, form_url='', extra_context=None):
        "The 'change' admin view for this model."
        # copied from django/contrib/admin/options.py at version 1.4.0
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and "_saveasnew" in request.POST:
            return self.add_view(request, form_url=reverse(
                'admin:%s_%s_add' % (opts.app_label, opts.model_name),
                current_app=self.admin_site.name))

        ModelForm = self.get_form(request, obj)
        formsets = []
        inline_instances = self.get_inline_instances(request, obj)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, new_object), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix,
                                  queryset=inline.get_queryset(request))
                formsets.append(formset)
                if hasattr(inline, 'inlines') and inline.inlines:
                    self.add_recursive_inline_formsets(request, inline, formset, obj)

            if self.all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, True)
                self.save_related(request, form, formsets, True)
                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)

        else:
            form = ModelForm(instance=obj)
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, obj), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix,
                                  queryset=inline.get_queryset(request))
                formsets.append(formset)
                if hasattr(inline, 'inlines') and hasattr(self, 'add_recursive_inline_formsets'):
                    self.add_recursive_inline_formsets(request, inline, formset)

        adminForm = helpers.AdminForm(
            form, self.get_fieldsets(request, obj),
            self.get_prepopulated_fields(request, obj),
            self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(
                inline, formset, fieldsets, prepopulated,
                readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media
            if hasattr(inline, 'inlines'):
                media = media + self.wrap_recursive_inline_formsets(request, inline, formset, obj)

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': IS_POPUP_VAR in request.REQUEST,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
            'preserved_filters': self.get_preserved_filters(request),

        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj, form_url=form_url)


class ReverseInlinesModelAdminMixin(object):

    def get_inline_instances(self, request, obj=None):
        inline_instances = super(ReverseInlinesModelAdminMixin, self).get_inline_instances(request, obj)
        if hasattr(self, 'inverse_inlines'):
            for inline_class in self.inverse_inlines:
                inline = inline_class(self.model, self.admin_site)
                if request:
                    if not (inline.has_add_permission(request) or
                            inline.has_change_permission(request) or
                            inline.has_delete_permission(request)):
                        continue
                    if not inline.has_add_permission(request):
                        inline.max_num = 0
                inline_instances.append(inline)
        return inline_instances


# ## GenericModelAdminMixin
class GenericModelAdminMixin(object):

    class Media:
        js = ()

    content_type_lookups = {}

    def __init__(self, model, admin_site):
        media = list(getattr(self.Media, 'js', ()))
        media.append(JS_PATH + 'genericadmin.js')
        self.Media.js = tuple(media)
        super(GenericModelAdminMixin, self).__init__(model, admin_site)

    def get_urls(self):
        base_urls = super(GenericModelAdminMixin, self).get_urls()
        opts = self.get_generic_relation_options()
        custom_urls = patterns(
            '',
            url(r'^obj/$', self.admin_site.admin_view(generic_lookup), name='admin_genericadmin_obj_lookup'),
            url(
                r'^get-generic-rel-list/$',
                self.admin_site.admin_view(get_generic_rel_list),
                kwargs=opts,
                name='admin_genericadmin_rel_list'),
        )
        return custom_urls + base_urls

    # Return a dictionary of keywords that are fed to the get_generic_rel_list view
    def get_generic_relation_options(self):
        return {'url_params': self.content_type_lookups,
                'blacklist': self.get_blacklisted_relations(),
                'whitelist': self.get_whitelisted_relations()}

    def get_blacklisted_relations(self):
        try:
            return self.content_type_blacklist
        except (AttributeError, ):
            return ()

    def get_whitelisted_relations(self):
        try:
            return self.content_type_whitelist
        except (AttributeError, ):
            return ()


class AdvancedSearchForm(Form):
    def __init__(self, *args, **kwargs):
        admin_class = kwargs.pop('admin_class')
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
        for item in admin_class.search_fields:

            # Check for this field in the advanced search titles dict on the admin class
            property_verbose_name = getattr(admin_class, 'advanced_search_titles', {}).get(item)
            if property_verbose_name:
                verbose_name = property_verbose_name
            else:
                # See if this field is a regular field or a related field property
                item_parts = item.split('__')
                if len(item_parts) > 1:
                    # This assumes it was only two parts, else this should be recursive

                    # Get the field and fk info from get_field_by_name()
                    field, model, direct, m2m = admin_class.model._meta.get_field_by_name(item_parts[0])
                    if direct or m2m:
                        # This is a related property of a fk or m2m, so the field_class is the field.model
                        field_class = field.related.parent_model
                    else:
                        # This is a reverse m2m _set, so the field class is that related class
                        field_class = getattr(admin_class.model, item_parts[0]).related.model

                    field, model, direct, m2m = field_class._meta.get_field_by_name(item_parts[1])
                    verbose_name = "%s %s" % (field_class._meta.verbose_name.title(), field.verbose_name.title())
                else:
                    # This was just a regular field
                    field_class = admin_class.model
                    field_name = item
                    field, model, direct, m2m = field_class._meta.get_field_by_name(field_name)
                    verbose_name = field.verbose_name.title()

            self.fields['%s__icontains' % item] = CharField(label=verbose_name)


class AdvancedSearchMixin(object):
    advanced_search_titles = {}

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        new_context = {'advanced_search_form': AdvancedSearchForm(admin_class=self, initial=request.GET)}
        new_context.update(extra_context or {})
        return super(AdvancedSearchMixin, self).changelist_view(request, extra_context=new_context)

    def lookup_allowed(self, lookup, value):
        if re.sub('\__icontains$', '', lookup) in self.search_fields:
            return True
        else:
            return super(AdvancedSearchMixin, self).lookup_allowed(lookup, value)


class URLFieldMixin(object):
    formfield_overrides = {
        URLField: {'widget': AdminURLFieldWidget},
    }


class ImageWidgetMixin(object):
    # Override image widget
    formfield_overrides = {
        ImageField: {'widget': ThumbnailImageWidget},
    }


class UnicodeForeignKeyRawIdWidgetMixin(object):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        db = kwargs.get('using')
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = UnicodeForeignKeyRawIdWidget(db_field.rel, self.admin_site, using=db)
        elif db_field.name in self.radio_fields:
            kwargs['widget'] = AdminRadioSelect(attrs={
                'class': get_ul_class(self.radio_fields[db_field.name]),
            })
            kwargs['empty_label'] = db_field.blank and _('None') or None
        return db_field.formfield(**kwargs)


class BaseClientAdminMixin(UnicodeForeignKeyRawIdWidgetMixin, GenericModelAdminMixin, AdvancedSearchMixin, ImageWidgetMixin, URLFieldMixin):
    formfield_overrides = dict(ImageWidgetMixin.formfield_overrides.items() + URLFieldMixin.formfield_overrides.items())


class StackedInlineMixin(object):
    collapse = False

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super(StackedInlineMixin, self).get_formset(request, obj, **kwargs)
        FormSet.collapse = self.collapse
        return FormSet


class GenericStackedInline(StackedInlineMixin, BaseClientAdminMixin, GenericModelAdminMixin, generic.GenericStackedInline):
    pass


class GenericGroupedInline(StackedInlineMixin, BaseClientAdminMixin, GenericModelAdminMixin, generic.GenericStackedInline):
    # Model admin for generic stacked inlines.
    template = 'admin/edit_inline/grouped.html'


class StackedInline(StackedInlineMixin, BaseRecursiveInlineMixin, BaseClientAdminMixin, GenericModelAdminMixin, admin.StackedInline):
    pass


class TabularInline(BaseRecursiveInlineMixin, BaseClientAdminMixin, GenericModelAdminMixin, admin.TabularInline):
    pass


class GenericTabularInline(BaseRecursiveInlineMixin, BaseClientAdminMixin, GenericModelAdminMixin, generic.GenericTabularInline):
    # Model admin for generic tabular inlines.
    pass


class GroupedInline(StackedInline):
    template = 'admin/edit_inline/grouped.html'


class ClientModelAdmin(VersionAdmin, ReverseInlinesModelAdminMixin, BaseClientAdminMixin, RecursiveInlinesModelAdmin):
    pass

# deprecated
class GenericAdminModelAdmin(ClientModelAdmin):
    #raise DeprecationWarning('Use ClientModelAdmin instead')
    pass

# deprecated
class BaseGenericModelAdmin(GenericModelAdminMixin):
    pass
