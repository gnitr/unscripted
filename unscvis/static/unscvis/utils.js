(function($) {
    $(function() {
        window.is_tab_focused = 1;
        window.unscutils = {
            /*
                Returns the height $element should have to fill the remaining
                space in the viewport.
                If noscrollbar =  1, returns height so that the whole page is
                contained within the viewport. i.e. no scrollbar
            */
            get_elastic_height: function($element, min, margin, noscrollbar) {
                var height = 0;
            
                // This is a hack for OL - we force 100% height when it is in
                // full screen mode. See zoom view of images on the faceted search.
                if ($element.find('.ol-full-screen-true').length > 0) {
                    return '100%';
                }
            
                min = min || 0;
                margin = margin || 0;
                noscrollbar = noscrollbar || 0;
            
                var current_height = $element.outerHeight();
                if (noscrollbar) {
                    // ! only works if body height is NOT 100% !
                    height = $(window).outerHeight() - $('body').outerHeight() + current_height;
                    height = (height <= min) ? min : height;
                } else {
                    var window_height = $(window).height() - margin;
                    height = window_height - $element.offset().top + $(document).scrollTop();
                    height = (height <= min) ? min : height;
                    height = (height > window_height) ? window_height : height;
                }
            
                return Math.floor(height);
            },
        
            /*
            Make $target height elastic. It will take the rest of the
            viewport space. This is automatically updated when the user
            scrolls or change the viewport size.
            $callback is called each time the height is updated.
            */
            elastic_element: function($target, callback, min, margin) {
                var on_resize = function(e) {
                    var height = unscutils.get_elastic_height($target, min, margin);
                    $target.css('height', height);
                    callback();
                };
                $(window).on('resize scroll', function(e) {on_resize(e);});
                $(document).on('webkitfullscreenchange mozfullscreenchange fullscreenchange MSFullscreenChange', function(e) {on_resize(e);});
                on_resize();
            },

            f1: $(window).on("blur focus", function(e) {
                var prevType = $(this).data("prevType");

                if (prevType != e.type) {   //  reduce double fire issues
                    switch (e.type) {
                        case "blur":
                        	window.is_tab_focused = 0;
                            // do work
                            break;
                        case "focus":
                        	window.is_tab_focused = 1;
                            // do work
                            break;
                    }
                }

                $(this).data("prevType", e.type);
            }),
            
            is_tab_visible: function() {
                if (typeof document.hidden !== 'undefined') {
                    return !document.hidden;
                }
                return (window.is_tab_focused !== 0);
            }
        }
    });
})(jQuery);
    