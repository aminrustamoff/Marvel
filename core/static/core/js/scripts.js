// MAIN SECTION SCRIPTS

const resizer_main = document.querySelector('.resizer');
const leftPanel = document.querySelector('.split-left');

resizer_main.addEventListener('mousedown', (e) => {
    resizer_main.classList.add('active');

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', () => {
        resizer_main.classList.remove('active');
        document.removeEventListener('mousemove', onMouseMove);
    });
});

function onMouseMove(e) {
    const container = document.querySelector('.split-container');
    const containerRect = container.getBoundingClientRect();
    const newLeftWidth = e.clientX - containerRect.left;
    leftPanel.style.flex = 'none';
    leftPanel.style.width = newLeftWidth + 'px';
}

function toggleAccordion(button) {
    const body = button.nextElementSibling;
    const arrow = button.querySelector('.accordion-arrow');

    body.classList.toggle('open');
    arrow.classList.toggle('open');
}


// LISTENING PAGE SCRIPTS

 const audio = document.getElementById('test-audio');

// Plays on the very first click anywhere on the page
document.addEventListener('click', function() {
    audio.play();
}, { once: true }); // '{ once: true }' ensures it only runs once


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

