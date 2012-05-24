var init_dashboard = function(id, columns, preferences, url) {
    jQuery('#'+id).dashboard({
        'columns': columns,
        'load_preferences_function': function(options) {
            return preferences;
        },
        'save_preferences_function': function(options, preferences) {
            jQuery.post(url, { data: JSON.stringify(preferences) });
        }
    });
    jQuery(".group-tabs").tabs();
    jQuery(".group-accordion").accordion({header: '.group-accordion-header'});
    
    $ = jQuery;

    $(".activity-types a").click(function(){
        $(".activity-types a").removeClass('active');
        $(this).addClass('active')
        filter = $(this).attr('data-filter');
        items = $(this).parent().siblings()
        items.each(function(){
            $(this).show();
            if (filter == 'others' && $(this).hasClass('mine') ){
                    $(this).hide();
            } else if (filter == 'mine' && !$(this).hasClass('mine') ){
                    $(this).hide();
            } 
        });

    })
};
