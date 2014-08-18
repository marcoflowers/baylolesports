function convert_date(date) {
    return new Date(date);
}

$(function () {
    console.log($('.filters').is(':hidden'));
    $('.filters').hide();
    $('input[type=search]').focus(function () {
        if(!$('.filters').is(':visible') && !$('.filters').is(':animated')) {
            $('.filters').slideToggle(750);
        }
    });
    $('html').click(function () {
        if($('.filters').is(':visible') && !$('.filters').is(':animated')) {
            $('.filters').slideToggle(750);
        }
    });
    $('.filter').click(function (e) {
        e.stopPropagation();
    });
    // See if this is a touch device
    if ('ontouchstart' in window)
    {
        // Set the correct body class
        $('body').removeClass('no-touch').addClass('touch');

        // Add the touch toggle to show text
        $('div.boxInner img').click(function(){
        $(this).closest('.boxInner').toggleClass('touchFocus');
        });
    }

    var last_visit = $.cookie('last_visit', convert_date);
    var last_visit = new Date(last_visit.getUTCFullYear(), last_visit.getUTCMonth(), last_visit.getUTCDate(),  last_visit.getUTCHours(), last_visit.getUTCMinutes(), last_visit.getUTCSeconds());
    if(typeof last_visit != 'undefined') {
        var create_dates = window.create_dates;
        for(var tournament in create_dates) { 
            var create_date = new Date(create_dates[tournament]);
            if(create_date > last_visit) {
                $('#' + tournament).prepend('<div class="ribbon-wrapper-blue"><div class="ribbon-blue">NEW</div></div>');
            }
        }
    }

    $.cookie('last_visit', new Date(), {expires: 30});

});
