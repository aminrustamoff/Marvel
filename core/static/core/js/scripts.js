const resizer = document.querySelector('.resizer');
const leftPanel = document.querySelector('.split-left');

resizer.addEventListener('mousedown', (e) => {
    resizer.classList.add('active');

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', () => {
        resizer.classList.remove('active');
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