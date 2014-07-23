





function post_event(ukey) {
    var date = $('div.' + ukey).text();
    var notifications = $('input.' + ukey).is('.checked');
    var data = {
        "date":date,
        "notifications":notifications,
    };
    var url = document.URL.substring(document.URL.lastIndexOf('/'));
    $.post('/tournament/schedule/' + ukey, data, function() {});
}
