document.addEventListener('DOMContentLoaded', function() {
  const inputs = document.querySelectorAll('.otp-input');

  inputs[0].focus();

  inputs.forEach((input, index) => {
    input.addEventListener('input', function(e) {
      if (this.value.length === 1 && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
    });

    input.addEventListener('keydown', function(e) {
      if (e.key === 'Backspace' && !this.value && index > 0) {
        inputs[index - 1].focus();
      }
    });

    input.addEventListener('paste', function(e) {
      e.preventDefault();
      const pasteData = e.clipboardData.getData('text').slice(0, 6);
      pasteData.split('').forEach((char, i) => {
        if (inputs[i]) inputs[i].value = char;
      });
      if (pasteData.length === 6) inputs[5].focus();
    });
  });
});