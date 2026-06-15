document.addEventListener('DOMContentLoaded', function() {

    const emailInput = document.querySelector('input[name="email"]');
    if (emailInput) emailInput.focus();

    const togglePassword = document.getElementById('toggleLoginPassword');
    const passwordInput = document.getElementById('loginPassword');

    // ✅ SAFE CHECK (IMPORTANT)
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {

            // toggle type
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';

            // toggle icon
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }

});