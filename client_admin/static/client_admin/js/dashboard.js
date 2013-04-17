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

    $(".activity-types a").click(function(e){
        $(".activity-types a").removeClass('active');
        $(this).addClass('active');
        var filter = $(this).attr('data-filter');
        var items = $(this).parent().siblings();
        items.each(function(i){
            var visible = (filter == 'mine' && $(this).hasClass('mine') )
                ||  (filter == 'others' && !$(this).hasClass('mine') )
                ||  (filter == 'all' && i < 10);
            $(this).toggle(visible);
        });
        e.preventDefault();
    });
};
