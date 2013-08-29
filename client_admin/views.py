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

from functools import wraps

try:
    import json
except ImportError:
    import simplejson as json

from django.contrib import admin
from django.contrib.admin.widgets import url_params_from_lookup_dict
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.utils.text import capfirst

try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    from django.contrib.csrf.middleware import csrf_exempt

from forms import DashboardPreferencesForm, BookmarkForm
from models import DashboardPreferences, Bookmark


# Decorator
def admin_login_required(view_func):

    @wraps(view_func)
    def _checklogin(request, *args, **kwargs):
        from django.contrib import admin
        return admin.site.admin_view(view_func)(request, *args, **kwargs)
    return _checklogin


def get_obj(content_type_id, object_id):
    obj_dict = {
        'content_type_id': content_type_id,
        'object_id': object_id,
    }

    content_type = ContentType.objects.get(pk=content_type_id)

    obj_dict["content_type_text"] = unicode(content_type)

    try:
        obj = content_type.get_object_for_this_type(pk=object_id)
        obj_dict["object_text"] = unicode(obj)
        try:
            obj_dict["object_url"] = obj.get_absolute_url()
        except AttributeError:
            obj_dict["object_url"] = ""
    except:
        obj_dict["object_text"] = ""

    return obj_dict


@admin_login_required
def generic_lookup(request):
    if request.method == 'GET':
        objects = []
        if 'content_type' in request.GET and 'object_id' in request.GET:
            obj = get_obj(request.GET['content_type'], request.GET['object_id'])
            objects.append(obj)

        response = HttpResponse(mimetype='application/json')
        json.dump(objects, response, ensure_ascii=False)
        return response
    else:
        return HttpResponseNotAllowed(['GET'])


@admin_login_required
def get_generic_rel_list(request, blacklist=(), whitelist=(), url_params={}):
    if request.method == 'GET':
        obj_dict = {}
        for c in ContentType.objects.all().order_by('id'):
            val = u'%s/%s' % (c.app_label, c.model)

            params = url_params.get('%s.%s' % (c.app_label, c.model), {})
            params = url_params_from_lookup_dict(params)
            if 'whitelist' in request.GET:
                whitelist = request.GET['whitelist']
            if 'blacklist' in request.GET:
                blacklist = request.GET['blacklist']
            if whitelist:
                if val in whitelist:
                    obj_dict[c.id] = (val, params)
            else:
                if val not in blacklist:
                    obj_dict[c.id] = (val, params)

        response = HttpResponse(mimetype='application/json')
        json.dump(obj_dict, response, ensure_ascii=False)
        return response
    else:
        return HttpResponseNotAllowed(['GET'])


@admin_login_required
def dashboard(request):
    """
    Displays the main dashboard page, which shows a sitemap
    matching the main site menu and lists all of the installed
    apps that have been registered in this site.
    """
    context = {}
    app_dict = {}
    user = request.user
    for model, model_admin in admin.site._registry.items():
        app_label = model._meta.app_label
        has_module_perms = user.has_module_perms(app_label)

        if has_module_perms:
            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'admin_url': mark_safe('%s/%s/' % (app_label, model.__name__.lower())),
                    'perms': perms,
                }
                if app_label in app_dict:
                    app_dict[app_label]['models'].append(model_dict)
                else:
                    app_dict[app_label] = {
                        'name': app_label.title(),
                        'app_url': app_label + '/',
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }
    # Sort the apps alphabetically.
    app_list = app_dict.values()
    app_list.sort(key=lambda x: x['name'])

    # Sort the models alphabetically within each app.
    for app in app_list:
        app['models'].sort(key=lambda x: x['name'])

    context = {
        'title': _('Dashboard'),
        'app_list': app_list,
    }
    return TemplateResponse(request, 'client_admin/dashboard/dashboard.html', context=context)


@login_required
@csrf_exempt
def set_preferences(request, dashboard_id):
    """
    This view serves and validates a preferences form.
    """
    try:
        preferences = DashboardPreferences.objects.get(
            user=request.user,
            dashboard_id=dashboard_id
        )
    except DashboardPreferences.DoesNotExist:
        preferences = None
    if request.method == "POST":
        form = DashboardPreferencesForm(
            user=request.user,
            dashboard_id=dashboard_id,
            data=request.POST,
            instance=preferences
        )
        if form.is_valid():
            preferences = form.save()
            if request.is_ajax():
                return HttpResponse('true')
            request.user.message_set.create(message='Preferences saved')
        elif request.is_ajax():
            return HttpResponse('false')
    else:
        form = DashboardPreferencesForm(
            user=request.user,
            dashboard_id=dashboard_id,
            instance=preferences
        )
    return TemplateResponse(request, 'client_admin/dashboard/preferences_form.html', context={
        'form': form,
    })


@login_required
@csrf_exempt
def add_bookmark(request):
    """
    This view serves and validates a bookmark form.
    If requested via ajax it also returns the drop bookmark form to replace the
    add bookmark form.
    """
    if request.method == "POST":
        form = BookmarkForm(user=request.user, data=request.POST)
        if form.is_valid():
            bookmark = form.save()
            if not request.is_ajax():
                request.user.message_set.create(message='Bookmark added')
                if request.POST.get('next'):
                    return HttpResponseRedirect(request.POST.get('next'))
                return HttpResponse('Added')
            return TemplateResponse(request, 'client_admin/menu/remove_bookmark_form.html', context={
                'bookmark': bookmark,
                'url': bookmark.url,
            })
    else:
        form = BookmarkForm(user=request.user)
    return TemplateResponse(request, 'client_admin/menu/form.html', context={
        'form': form,
        'title': 'Add Bookmark',
    })


@login_required
@csrf_exempt
def edit_bookmark(request, id):
    bookmark = get_object_or_404(Bookmark, id=id)
    if request.method == "POST":
        form = BookmarkForm(user=request.user, data=request.POST, instance=bookmark)
        if form.is_valid():
            form.save()
            if not request.is_ajax():
                request.user.message_set.create(message='Bookmark updated')
                if request.POST.get('next'):
                    return HttpResponseRedirect(request.POST.get('next'))
            return HttpResponse('Saved')
    else:
        form = BookmarkForm(user=request.user, instance=bookmark)
    return TemplateResponse(request, 'client_admin/menu/form.html', context={
        'form': form,
        'title': 'Edit Bookmark',
    })


@login_required
@csrf_exempt
def remove_bookmark(request, id):
    """
    This view deletes a bookmark.
    If requested via ajax it also returns the add bookmark form to replace the
    drop bookmark form.
    """
    bookmark = get_object_or_404(Bookmark, id=id)
    if request.method == "POST":
        bookmark.delete()
        if not request.is_ajax():
            request.user.message_set.create(message='Bookmark removed')
            if request.POST.get('next'):
                return HttpResponseRedirect(request.POST.get('next'))
            return HttpResponse('Deleted')
        return TemplateResponse(request, 'client_admin/menu/add_bookmark_form.html', context={
            'url': request.POST.get('next'),
            'title': '**title**'  # This gets replaced on the javascript side
        })
    return TemplateResponse(request, 'client_admin/menu/delete_confirm.html', context={
        'bookmark': bookmark,
        'title': 'Delete Bookmark',
    })

from django.forms.formsets import formset_factory
from django.db.models.loading import get_model
from django import forms
from django.core.urlresolvers import reverse

@login_required
def bulk_add(request, app_label, model_name):
    model_cls = get_model(app_label, model_name)
    form_cls = None
    if model_cls in admin.site._registry:
        form_cls = getattr(admin.site._registry[model_cls], 'bulk_form', None)
    if form_cls is None:
        class form_cls(forms.ModelForm):
            class Meta:
                model = model_cls
    formset_cls = formset_factory(form_cls, extra=25)
    if request.method == "POST":
        formset = formset_cls(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset:
                if form.is_valid() and form.has_changed():
                    form.save()
            return HttpResponseRedirect(reverse('admin:%s_%s_changelist' % (app_label, model_name)))
    else:
        formset = formset_cls()

    return TemplateResponse(request, 'client_admin/bulk/add.html', context={
        'formset': formset,
        'app_label': app_label,
        'model_name': model_name,
        'verbose_name_plural': model_cls._meta.verbose_name_plural.title(),
    })
    pass
