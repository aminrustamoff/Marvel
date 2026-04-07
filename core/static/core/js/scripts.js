function toggleAccordion(button) {
    const body = button.nextElementSibling;
    const arrow = button.querySelector('.accordion-arrow');

    body.classList.toggle('open');
    arrow.classList.toggle('open');
}