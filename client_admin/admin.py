# # Client Admin admin classes
from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from client_admin.views import generic_lookup, get_generic_rel_list
from django.conf import settings

JS_PATH = getattr(settings, 'GENERICADMIN_JS', 'client_admin/js/') 


from django.contrib.contenttypes import generic


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
