//---- start drag drop ----//
function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault(); // Necessary. Allows us to drop.
    }
    e.dataTransfer.dropEffect = 'move';  // See the section on the DataTransfer object.

    return false;
}

function handleDragEnter(e) {
    // this / e.target is the current hover target.
    this.classList.add('over');
}

function handleDragLeave(e) {
    this.classList.remove('over');  // this / e.target is previous target element.
}



function handleDragEnd(e) {
    // this/e.target is the source node.
    this.style.opacity = '1.0';

    [].forEach.call(slots, function (slot) {
        slot.classList.remove('over');
    });
}


var dragSrcEl = null;

function handleDragStart(e) {
    // Target (this) element is the source node.
    this.style.opacity = '0.4';

    dragSrcEl = this;

    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}
function handleDrop(e) {
    // this/e.target is current target element.

    if (e.stopPropagation) {
        e.stopPropagation(); // Stops some browsers from redirecting.
    }
    this.classList.remove('over');

    // Don't do anything if dropping the same slot we're dragging.
    if (dragSrcEl != this) {
        // Set the source slot's HTML to the HTML of the slot we dropped on.
        dragSrcEl.innerHTML = this.innerHTML;
        this.innerHTML = e.dataTransfer.getData('text/html');
    }

    return false;
}

//---- end drag drop ----//


$(document).ready(function() {
    var slots = $("#slots .slot");
    [].forEach.call(slots, function(slot) {
        slot.addEventListener('dragstart', handleDragStart, false);
        slot.addEventListener('dragenter', handleDragEnter, false)
        slot.addEventListener('dragover', handleDragOver, false);
        slot.addEventListener('dragleave', handleDragLeave, false);
        slot.addEventListener('drop', handleDrop, false);
        slot.addEventListener('dragend', handleDragEnd, false);
    });
});



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



function save() {
    var slots = $("#tournslots .slot");
    data = {};
    [].forEach.call(slots, function(slot) {
        console.log($(slot).parents().attr("value"));
        console.log($(slot).text());
        data[$(slot).parents().attr("value")]=$(slot).text()
    });
    data["bracket"]=true
    console.log(document.URL)
    //$.post(document.URL, data, function() {
   //     console.log("Success");
   // });
    console.log(data)
    console.log(JSON.stringify(data))
    var string=""
    for (var key in data) {
        var obj = data[key];
        string=string+key+"="+obj+"&"
    }
    string=string.substring(0,string.length-1)
    console.log(string)
    $.ajax({
            url: document.URL, 
            type:'post',
            data:string,
            success:function(data){
                console.log("Success")
            }
    })
}



function save() {
    var slots = $("#slots .slot");
    data = {};
    [].forEach.call(slots, function(slot) {
        console.log($(slot).parents().attr("value"));
        console.log($(slot).text());
    });
    $.post(document.URL, data, function() {
    });
}
