// READING PAGE SCRIPTS

const resizer = document.getElementById('resizer');
const left = document.querySelector('.split-left');
const right = document.querySelector('.split-right');

let isDragging = false;

resizer.addEventListener('mousedown', () => {
    isDragging = true;
    document.body.style.cursor = 'col-resize';
});

document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;

    let containerWidth = document.querySelector('.split-container').offsetWidth;
    let leftWidth = (e.clientX / containerWidth) * 100;

    left.style.flex = "none";
    left.style.width = leftWidth + "%";
    right.style.flex = "1";
});

document.addEventListener('mouseup', () => {
    isDragging = false;
    document.body.style.cursor = 'default';
});