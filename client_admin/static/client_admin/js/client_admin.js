(function($) {
    $('#changelist-filter .vForeignKeyRawIdAdminField').each(function(){
        watch(this, "value", function(){
            prefix_obj = $(this).siblings('#'+this.id+'_prefix')[0];
            window.location.href = window.location.href.split(/\?/)[0] + prefix_obj.value + this.value;
        });
    });
})(django.jQuery);