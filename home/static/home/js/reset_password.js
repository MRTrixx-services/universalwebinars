document.addEventListener('DOMContentLoaded', function() {
  // Password toggle for new password
  const toggleNewPassword = document.getElementById('toggleNewPassword');
  const newPasswordInput = document.getElementById('newPassword');
  
  toggleNewPassword.addEventListener('click', function() {
    const type = newPasswordInput.type === 'password' ? 'text' : 'password';
    newPasswordInput.type = type;
    this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
  });

  // Password toggle for confirm password
  const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
  const confirmPasswordInput = document.getElementById('confirmPassword');
  
  toggleConfirmPassword.addEventListener('click', function() {
    const type = confirmPasswordInput.type === 'password' ? 'text' : 'password';
    confirmPasswordInput.type = type;
    this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
  });

  // Password match validation
  const form = document.querySelector('.login-form');
  form.addEventListener('submit', function(e) {
    if (newPasswordInput.value !== confirmPasswordInput.value) {
      e.preventDefault();
      alert('Passwords do not match!');
      confirmPasswordInput.focus();
    }
  });
});