// Script para manejar el cambio de tema
document.addEventListener('DOMContentLoaded', function() {
    // Establecer tema cuando se hace clic en un botón de tema
    const themeButtons = document.querySelectorAll('[data-set-theme]');
    themeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const theme = button.getAttribute('data-set-theme');
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        });
    });
});