
// Execute when the DOM is fully loaded
$(document).ready(function() {

    // create bindings for each button on the "drive" page
    $('a#left').bind('mousedown', function() { $.getJSON('/left_start', function(data) { /* do nothing */}); return false; });
    $('a#left').bind('mouseup', function() { $.getJSON('/stop', function(data) { /* do nothing */}); return false; });
    $('a#left').bind('click', function(event) { event.preventDefault(); return false; });
    $('a#left').bind('touchstart', function() { $.getJSON('/left_start', function(data) { /* do nothing */}); return false; });
    $('a#left').bind('touchend', function() { $.getJSON('/stop', function(data) { /* do nothing */}); return false; });

    $('a#right').bind('mousedown', function() { $.getJSON('/right_start', function(data) { /* do nothing */}); return false; });
    $('a#right').bind('mouseup', function() { $.getJSON('/stop', function(data) { /* do nothing */}); return false; });
    $('a#right').bind('click', function(event) { event.preventDefault(); return false; });
    $('a#right').bind('touchstart', function() { $.getJSON('/right_start', function(data) { /* do nothing */}); return false; });
    $('a#right').bind('touchend', function() { $.getJSON('/stop', function(data) { /* do nothing */}); return false; });

    $('a#forward').bind('mousedown', function() { $.getJSON('/forward_start', function(data) { /* do nothing */}); return false; });
    $('a#forward').bind('mouseup', function() { $.getJSON('/stop', function(data) { /* do nothing */}); return false; });
    $('a#forward').bind('click', function(event) { event.preventDefault(); return false; });
    $('a#forward').bind('touchstart', function() { $.getJSON('/forward_start', function(data) { /* do nothing */}); return false; });
    $('a#forward').bind('touchend', function() { $.getJSON('/stop', function(data) { /* do nothing */}); return false; });

    $('a#reverse').bind('mousedown', function() { $.getJSON('/reverse_start', function(data) { /* do nothing */}); return false; });
    $('a#reverse').bind('mouseup', function() { $.getJSON('/stop', function(data) { /* do nothing */}); return false; });
    $('a#reverse').bind('click', function(event) { event.preventDefault(); return false; });
    $('a#reverse').bind('touchstart', function() { $.getJSON('/reverse_start', function(data) { /* do nothing */}); return false; });
    $('a#reverse').bind('touchend', function() { $.getJSON('/stop', function(data) { /* do nothing */}); return false; });

    $('a#shot').bind('mousedown', function() { $.getJSON('/shot_start', function(data) { /* do nothing */}); return false; });
    $('a#shot').bind('click', function(event) { event.preventDefault(); return false; });
    $('a#shot').bind('touchstart', function() { $.getJSON('/shot_start', function(data) { /* do nothing */}); return false; });

    $('a#pic').bind('click', function(event) {  event.preventDefault();
                                                $.getJSON('/camera', function(data) { /* do nothing */});
                                                return false; });
});
