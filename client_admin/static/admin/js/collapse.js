(function($) {
    $.fn.clickToggle = function(func1, func2) {
        var funcs = [func1, func2];
        this.data('toggleclicked', 0);
        this.click(function() {
            var data = $(this).data();
            var tc = data.toggleclicked;
            $.proxy(funcs[tc], this)();
            data.toggleclicked = (tc + 1) % 2;
        });
        return this;
    };

	$(document).ready(function() {
		// Add anchor tag for Show/Hide link
		$("fieldset.collapse").each(function(i, elem) {
			// Don't hide if fields in this fieldset have errors
			if ($(elem).find("div.errors").length == 0) {
				var collapse_toggle = $('<a/>', {
					href: 'javascript:void(0)',
					class: 'collapse-toggle'
				}).html(gettext("Show"));
				$(elem).addClass("collapsed").find("h2").first().append(collapse_toggle);

				collapse_toggle.clickToggle(
					function() { // Show
						$(this).text(gettext("Hide")).closest("fieldset").removeClass("collapsed").trigger("show.fieldset", [$(this).attr("id")]);
						return false;
					},
					function() { // Hide
						$(this).text(gettext("Show")).closest("fieldset").addClass("collapsed").trigger("hide.fieldset", [$(this).attr("id")]);
						return false;
					}
				);
			}
		});
	});
})(django.jQuery);