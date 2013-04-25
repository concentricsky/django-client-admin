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

    $(document).ready(function () {
        // This is a hack, as it assumes that any GET args with icontains come
        // from an advanced search. This is true for now, but maybe not later.
        // Instead, possibly should iterate over form and check for values.
        // Or, add a hidden field to the form that marks the form as 'adv'
        if (window.location.search.indexOf("icontains") == -1){
            $('#changelist-advanced-search').hide();
        } else {
            $('#toolbar').hide();
        }
    });
})(django.jQuery);

slide_speed = 200;

var show_advanced_search = function (){
    $('#changelist-advanced-search').slideDown(slide_speed);
    $('#toolbar').slideUp(slide_speed);
};

var hide_advanced_search = function (){
    $('#changelist-advanced-search').slideUp(slide_speed);
    $('#toolbar').slideDown(slide_speed);
};

function submitFunc() {
    var adv_form = document.getElementById('changelist-advanced-search');
    var form_length = adv_form.length;
    for (var i=0; i<form_length; i++){
        var field = adv_form[i];
        if (field.value==="") {
            field.disabled='disabled';
        }
    }
}