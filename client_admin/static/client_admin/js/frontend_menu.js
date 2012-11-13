
$(function() {
    
        $('a.clientadmin-window').click(function() {
            var href = $(this).attr('href');
            href += ((href.search(/\?/) >= 0) ? '&' : '?') + "_popup=1"
            var win = window.open(href, "clientadmin", "height=800,width=1024" );
            win.focus();
            win.onload = function() {
              win.onunload = function() {
                win.close();
                window.location = window.location;
              }
            }
            return false;
        });

})
