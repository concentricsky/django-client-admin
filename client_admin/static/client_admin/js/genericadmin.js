/*
    genericadmin - Weston Nielson (wnielson@gmail.com)

    updated by Jan Schrewe (jschrewe@googlemail.com)

    updated by Troy Melhase (troy.melhase@gmail.com)

 */
 (function($) {
    var GenericAdmin = {
        url_array: null,
        obj_url: "../obj/",
        admin_media_url: window.__admin_media_prefix__,
        generics_list_url: '../get-generic-rel-list/',
        loadUrlArray: function() {
            var that = this;
            $.ajax({
                url: this.generics_list_url,
                dataType: 'json',
                success: function(data) {
                    that.url_array = data;
                },
                async: false
            });
        },
        prepareSelect: function(elem) {
            var that = this;
            var opt_keys = [];
            var opt_dict = {};
            var contentTypeSelect;

            // should return 3 items: ["id_ingredientlist_set", "2",
            // "content_type"]
            // FIX:  a better way to specify this for generic inlines
            var context = $(elem).parents('fieldset');
            contentTypeSelect = $("[id$='content_type']", context).first();

            // contentTypeSelect = $('#id_content_type').first();
            var vars = $(this.object_input).attr("id").split('-');
            if (vars.length !== 1) {
                //contentTypeSelect = $('#' + vars[0] + '-' + vars[1] + '-content_type').first();
                contentTypeSelect = $('#' + $(this.object_input).attr("id").replace('-object_id', '-content_type'))
            }
            // polish the look of the select
            $(contentTypeSelect).find('option').each(function() {
                var key;

                if (this.value) {
                    if (that.url_array[this.value]) {
                        key = that.url_array[this.value][0].split('/')[0];
                        // create an array with unique elements
                        if ($.inArray(key, opt_keys) < 0) {
                            opt_keys.push(key);
                            // if it's the first time in array
                            // it's the first time in dict
                            opt_dict[key] = [$(this).clone()];
                        } else {
                            opt_dict[key].push($(this).clone());
                        }
                    }
                    $(this).remove();
                }
            });

            opt_keys = opt_keys.sort();

            var opt_group_css = 'style="font-style:normal; font-weight:bold; color:#999; padding-left: 2px;"';
            $.each(opt_keys, function(index, key) {
                var opt_group = $('<optgroup label="' + key + '" ' + opt_group_css + '></optgroup>');
                $.each(opt_dict[key], function(index, value) {
                    opt_group.append(value).css({
                        'color': '#000'
                    });
                });
                $(contentTypeSelect).append(opt_group);
            });
            return contentTypeSelect;
        },

        getLookupUrlParams: function(cID) {
            var q = this.url_array[cID][1] || {};
            var str = [];
            for(var p in q)
                str.push(encodeURIComponent(p) + "=" + encodeURIComponent(q[p]));
            x = str.join("&");
            url = x ? ("?" + x) : "";
            return url
        },
        getLookupUrl: function(cID) {
            return '../../../' + this.url_array[cID][0] + '/' + this.getLookupUrlParams(cID);
        },
        hideLookupLink: function() {
            $('#lookup_' + this.object_input.id).unbind().remove();
            $('#unicode_' + this.object_input.id).remove();
        },
        showLookupLink: function() {
            var that = this;
            var url = this.getLookupUrl(this.cID);
            var id = 'lookup_' + this.object_input.id;
            var link_text = 'Choose an item';
            if (this.object_input.value) {link_text = 'Change';}
            var link = '<a class="related-lookup" id="' + id + '" href="' + url + '">'+link_text+'</a>';
            // link = link + '<button id="lookup_button_' + this.object_input.id + '" style="cursor: pointer; margin-right: 10px; float:left;">'+link_text+'</button></a>';
            link = link + '<strong id="unicode_' + this.object_input.id + '" style="line-height: 2.4em;"></strong>';
            // insert link html after input element
            $(this.object_input).after(link);

            return id;
        },
        pollInputChange: function(window) {
            var that = this;
            var interval_id = setInterval(function() {
                if (window.closed == true) {
                    clearInterval(interval_id);
                    that.updateObjectData()();
                    return true;
                }
            },
            150);
        },
        popRelatedObjectLookup: function(link) {
            var name = link.id.replace(/^lookup_/, '');
            var href;
            var win;

            name = id_to_windowname(name);

            if (link.href.search(/\?/) >= 0) {
                href = link.href + '&_popup=1';
            } else {
                href = link.href + '?_popup=1';
            }
            win = window.open(href, name, 'height=500,width=1000,resizable=yes,scrollbars=yes');

            // wait for popup to be closed and load object data
            this.pollInputChange(win);

            win.focus();
            return false;
        },
        updateObjectDataCallback: function(){
            $('#lookup_button_' + this.object_input.id).text('Change');
        },
        updateObjectData: function() {
            var that = this;

            return function() {
                // if (!that.object_input.value) { return } 
                // bail if no input
                $('#unicode_' + that.object_input.id).text('').text('loading...');
                $.ajax({
                    url: that.obj_url,
                    dataType: 'json',
                    data: {
                        object_id: that.object_input.value,
                        content_type: that.cID
                    },
                    success: function(data) {
                        var item = data[0];
                        if (item && item.content_type_text && item.object_text) {
                            $('#unicode_'+that.object_input.id).text(item.object_text);
                            // run a callback to do other stuff like prepopulating url fields
                            // can't be done with normal django admin prepopulate
                            if (that.updateObjectDataCallback) {
                                that.updateObjectDataCallback(item);
                            }
                        }
                    }
                });
            };
        },

        updateObjectLookup: function(elem){
            var that = this;
            var link_id;
            that.hideLookupLink();
            // Set our objectId when the content_type is changed
            if (elem.value) {
                that.cID = elem.value;
                link_id = that.showLookupLink();
                $('#' + link_id).click(function(e) {
                    that.popRelatedObjectLookup(this);
                    return false;
                });
            }
        },

        installAdmin: function(elem) {
            var that = this;
            // initialize the url array
            that.loadUrlArray();
            // store the base element
            that.object_input = elem;
            // find the select we need to change
            that.object_select = that.prepareSelect(elem);

            // install event handler for select change
            $(that.object_select).change(function() {
                // Clear the ID if the type changes
                $(that.object_input).val('');
                that.hideLookupLink();
                // Update the lookup url
                that.updateObjectLookup(this);

            });

            // Initialize object_data
            if ($(this.object_select).val()) {
                if ($(this.object_input).val()) {
                    // If both type and id exist, look up the obj and update the obj data
                    that.updateObjectLookup($(that.object_select)[0]);
                    this.updateObjectData()();
                } else {
                    // run a full change event on object_select
                    $(this.object_select).trigger('change');
                }
            }

            // Bind to the onblur of the object_id input.
            $(this.object_input).blur(this.updateObjectData());
            $(this.object_input).hide();
        },
    };

    install_on_add = function(i, e) {
        inputs = i.find("input[id$='object_id']")
        //$.extend({}, GenericAdmin).installAdmin(this_input);
        inputs.each(function(i, e) {
            $.extend({}, GenericAdmin).installAdmin(this);
        });
    };

    $(document).ready(function() {
        $("li:not(.empty-form) input[id$='object_id']").each(function(i, e) {
            $.extend({}, GenericAdmin).installAdmin(this);
        });
        $("tr:not(.empty-form) input[id$='object_id']").each(function(i, e) {
            $.extend({}, GenericAdmin).installAdmin(this);
        });
    });
} (django.jQuery));
