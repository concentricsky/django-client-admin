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