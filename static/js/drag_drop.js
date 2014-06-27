function handleDragStart(e) {
    console.log("drag_start");
  this.style.opacity = '0.4';  // this / e.target is the source node.
}

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

  // Don't do anything if dropping the same slot we're dragging.
  if (dragSrcEl != this) {
    // Set the source slot's HTML to the HTML of the slot we dropped on.
    dragSrcEl.innerHTML = this.innerHTML;
    this.innerHTML = e.dataTransfer.getData('text/html');
  }

  return false;
}
var slots = document.querySelectorAll('#slots .slot');
console.log($("div"));
[].forEach.call(slots, function(slot) {
  slot.addEventListener('dragstart', handleDragStart, false);
  slot.addEventListener('dragenter', handleDragEnter, false)
  slot.addEventListener('dragover', handleDragOver, false);
  slot.addEventListener('dragleave', handleDragLeave, false);
  slot.addEventListener('drop', handleDrop, false);
  slot.addEventListener('dragend', handleDragEnd, false);
});

