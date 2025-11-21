// Efecto de shake si el login falla
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.login-box form');
    const errorMsg = document.querySelector('.login-box .error');
    if (errorMsg) {
        form.classList.add('shake');
        setTimeout(() => form.classList.remove('shake'), 600);
    }

    // Animación de foco en inputs
    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 0 2px #f76d6d44';
        });
        input.addEventListener('blur', function() {
            this.style.boxShadow = '';
        });
    });

    // Animación de botón al hacer click
    const btn = form.querySelector('button[type="submit"]');
    btn.addEventListener('mousedown', function() {
        this.style.transform = 'scale(0.97)';
    });
    btn.addEventListener('mouseup', function() {
        this.style.transform = '';
    });
});
