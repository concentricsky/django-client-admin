(function($) {
    $('#changelist-filter .vForeignKeyRawIdAdminField').each(function(){
        watch(this, "value", function(){
            prefix_obj = $(this).siblings('#'+this.id+'_prefix')[0];
            new_url = prefix_obj.value.replace("PLACEHOLDER", this.value);
            window.location.href = window.location.href.split(/\?/)[0] + new_url;
        });
    });

    $('#changelist-filter select.href-trigger').change(function(){
        window.location.href = this.value;
    });
})(django.jQuery);

function showRelatedObjectLookupPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^lookup_/, '');
    name = id_to_windowname(name);
    var href;
    if (triggeringLink.href.search(/\?/) >= 0) {
        href = triggeringLink.href + '&pop=1';
    } else {
        href = triggeringLink.href + '?pop=1';
    }
    var win = window.open(href, name, 'height=600,width=1000,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}