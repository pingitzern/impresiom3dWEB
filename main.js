// Simple placeholder script
document.addEventListener('DOMContentLoaded', () => {
    console.log('Impresiom3D page loaded');

    const form = document.querySelector('form');
    if (!form) {
        return;
    }

    const showMessage = (message) => {
        // Using alert for simplicity as there is no designated container
        alert(message);
    };

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const name = form.querySelector('[name="name"]');
        const email = form.querySelector('[name="email"]');
        const phone = form.querySelector('[name="phone"]');
        const messageField = form.querySelector('[name="message"]');

        const allFilled = name && email && phone && messageField &&
            name.value.trim() && email.value.trim() && phone.value.trim() && messageField.value.trim();

        if (!allFilled) {
            showMessage('Please fill in all required fields.');
            return;
        }

        showMessage('Form submitted successfully!');
        form.reset();
    });
});
