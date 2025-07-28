// Main interactions
document.addEventListener('DOMContentLoaded', () => {
    console.log('Impresiom3D page loaded');

    // Fade-in effect for elements with .fade-in
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

    const form = document.getElementById('contactForm');
    if (!form) return;

    form.addEventListener('submit', event => {
        event.preventDefault();
        if (form.checkValidity()) {
            document.getElementById('formSuccess').classList.remove('hidden');
            form.reset();
        }
    });
});
