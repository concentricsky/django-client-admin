# # Client Admin admin classes
from client_admin.views import generic_lookup, get_generic_rel_list

from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin import widgets, helpers
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.util import unquote
from django.contrib.contenttypes import generic
from django.db import transaction
from django.forms import models
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from functools import update_wrapper, partial

csrf_protect_m = method_decorator(csrf_protect)

JS_PATH = getattr(settings, 'GENERICADMIN_JS', 'client_admin/js/') 



class BaseRecursiveInline(object):
    inlines = []

    def get_inline_instances(self, request):
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

class StackedRecursiveInline(BaseRecursiveInline, admin.StackedInline):
    template = 'admin/edit_inline/stacked_recursive.html'

class TabularRecursiveInline(BaseRecursiveInline, admin.TabularInline):
    template = 'admin/edit_inline/tabular_recursive.html'

class RecursiveInlinesModelAdmin(admin.ModelAdmin):
    
    class Media:
        pass

    def __init__(self, model, admin_site):
        media = list(getattr(self.Media, 'js', ()))
        media.append(static('client_admin/js/recursiveinlines.js'))
        self.Media.js = tuple(media)
        super(RecursiveInlinesModelAdmin, self).__init__(model, admin_site)

    def save_formset(self, request, form, formset, change):
        super(RecursiveInlinesModelAdmin, self).save_formset(request, form, formset, change=change)
        for form in formset.forms:
            for recursive_formset in getattr(form, 'recursive_formsets', []):
                self.save_formset(request, form, recursive_formset, change=change)

    def add_recursive_inline_formsets(self, request, inline, formset):
        for form in formset.forms:
            recursive_formsets = []
            for recursive_inline in inline.get_inline_instances(request):
                FormSet = recursive_inline.get_formset(request, form.instance)
                prefix = "%s-%s" % (form.prefix, FormSet.get_default_prefix())
                if request.method == 'POST':
                    if form.instance.pk:
                        recursive_formset = FormSet(request.POST, request.FILES, instance=form.instance, prefix=prefix, queryset=recursive_inline.queryset(request))
                else:
                    recursive_formset = FormSet(instance=form.instance, prefix=prefix, queryset=recursive_inline.queryset(request))
                recursive_formsets.append(recursive_formset)
                if hasattr(recursive_inline, 'inlines'):
                    self.add_recursive_inline_formsets(request, recursive_inline, recursive_formset)
            form.recursive_formsets = recursive_formsets

    def wrap_recursive_inline_formsets(self, request, inline, formset):
        media = None
        def get_media(extra_media):
            if media:
                return media + extra_media
            else:
                return extra_media

        for form in formset.forms:
            wrapped_recursive_formsets = []
            for recursive_inline, recursive_formset in zip(inline.get_inline_instances(request), form.recursive_formsets):
                if form.instance.pk:
                    instance = form.instance
                else:
                    instance = None

                fieldsets = list(recursive_inline.get_fieldsets(request))
                readonly = list(recursive_inline.get_readonly_fields(request))
                prepopulated = dict(recursive_inline.get_prepopulated_fields(request))
                if hasattr(recursive_inline, 'inlines'):
                    media = get_media(self.wrap_recursive_inline_formsets(request, recursive_inline, recursive_formset))
                wrapped_recursive_formset = helpers.InlineAdminFormSet(recursive_inline, recursive_formset, fieldsets, prepopulated, readonly, model_admin=self)
                wrapped_recursive_formsets.append(wrapped_recursive_formset)
                media = get_media(wrapped_recursive_formset.media)
            form.recursive_formsets = wrapped_recursive_formsets

        return media

    def all_valid(self, formsets):
        if not all_valid(formsets):
            return False
        for formset in formsets:
            if formset.is_bound:
                for form in formset:
                    if hasattr(form, 'recursive_formsets'):
                        if not self.all_valid(form.recursive_formsets):
                            return False
                        # gross gross gross
                        if not form.cleaned_data:
                            form._errors['__all__'] = form.error_class(["Parent object must be created when creating nested inlines."])
                            return False
        return True

    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context={}):
        "The 'add' admin view for this model."
        #copied from django/contrib/admin/options.py:924 because THAT'S WHAT YOU HAVE TO DO TO CHANGE THREE GODDAMN LINES
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
                                  prefix=prefix, queryset=inline.queryset(request))
                formsets.append(formset)
                if inline.inlines:
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
                except models.FieldDoesNotExist:
                    continue
                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")
            form = ModelForm(initial=initial)
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=self.model(), prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)
                if inline.inlines:
                    self.add_recursive_inline_formsets(request, inline, formset)

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
            self.get_prepopulated_fields(request),
            self.get_readonly_fields(request),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request))
            readonly = list(inline.get_readonly_fields(request))
            prepopulated = dict(inline.get_prepopulated_fields(request))
            if hasattr(inline, 'inlines'):
                media = media + self.wrap_recursive_inline_formsets(request, inline, formset)
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': False,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url, add=True)

    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, form_url='', extra_context=None):
        "The 'change' admin view for this model."
        # also copied from django/contrib/admin/options.py
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and "_saveasnew" in request.POST:
            return self.add_view(request, form_url=reverse('admin:%s_%s_add' %
                                    (opts.app_label, opts.module_name),
                                    current_app=self.admin_site.name))

        ModelForm = self.get_form(request, obj)
        formsets = []
        inline_instances = self.get_inline_instances(request)
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
                                  queryset=inline.queryset(request))

                formsets.append(formset)
                if hasattr(inline, 'inlines'):
                    self.add_recursive_inline_formsets(request, inline, formset)

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
                                  queryset=inline.queryset(request))
                formsets.append(formset)
                if hasattr(inline, 'inlines'):
                    self.add_recursive_inline_formsets(request, inline, formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
            self.get_prepopulated_fields(request, obj),
            self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            if hasattr(inline, 'inlines'):
                media = media + self.wrap_recursive_inline_formsets(request, inline, formset)
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj, form_url=form_url)


class ReverseInlinesModelAdmin(admin.ModelAdmin):
    
    def get_inline_instances(self, request):
        inline_instances = super(ReverseInlinesModelAdmin, self).get_inline_instances(request)
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


# ## BaseGenericModelAdmin
class BaseGenericModelAdmin(object):

    class Media:
        js = ()

    content_type_lookups = {}
    
    def __init__(self, model, admin_site):
        media = list(getattr(self.Media, 'js', ()))
        media.append(JS_PATH + 'genericadmin.js')
        self.Media.js = tuple(media)
        super(BaseGenericModelAdmin, self).__init__(model, admin_site)

    def get_urls(self):
        base_urls = super(BaseGenericModelAdmin, self).get_urls()
        opts = self.get_generic_relation_options()
        custom_urls = patterns('',
            url(r'^obj/$', self.admin_site.admin_view(generic_lookup), name='admin_genericadmin_obj_lookup'),
            url(r'^get-generic-rel-list/$', self.admin_site.admin_view(get_generic_rel_list), kwargs=opts, 
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


class GenericAdminModelAdmin(BaseGenericModelAdmin, admin.ModelAdmin):
    # Model admin for generic relations.
    pass


class GenericTabularInline(BaseGenericModelAdmin, generic.GenericTabularInline):
    # Model admin for generic tabular inlines.
    pass


class GenericStackedInline(BaseGenericModelAdmin, generic.GenericStackedInline):
    # Model admin for generic stacked inlines.
    pass


class ReverseInlinesModelAdmin(admin.ModelAdmin):
    
    def get_inline_instances(self, request):
        inline_instances = super(ReverseInlinesModelAdmin, self).get_inline_instances(request)
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
