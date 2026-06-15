$(document).ready(function() {

    // Select2
    $('#id_country').select2({
        placeholder: "Select your country",
        width: '100%'
    });

    // Phone input
    const input = document.querySelector("#id_phone_number");

    const iti = window.intlTelInput(input, {
        initialCountry: "us",
        separateDialCode: true,
        preferredCountries: ["us", "in", "gb"],
        utilsScript: "https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/utils.js"
    });

    // ✅ Default set US
    $('#id_country').val('US').trigger('change');
    iti.setCountry('us');

    // 🔁 Country → Phone (only dial code sync)
    $('#id_country').on('change', function() {
        const selectedCountry = $(this).val();
        if (selectedCountry) {
            iti.setCountry(selectedCountry.toLowerCase());
        }
    });

    // 🔁 Phone → Country sync (optional but good UX)
    input.addEventListener("countrychange", function() {
        const countryData = iti.getSelectedCountryData();
        $('#id_country')
            .val(countryData.iso2.toUpperCase())
            .trigger('change.select2');
    });

    // ✅ LIGHT VALIDATION
    $('#registerForm').on('submit', function(e) {
        const phone = input.value.trim();

        if (phone && !/^[0-9+\-\s().]{6,20}$/.test(phone)) {
            e.preventDefault();
            alert("Enter valid phone number");
        }
    });

    // Terms checkbox
    const termsCheckbox = document.getElementById('termsCheckbox');
    const registerBtn = document.getElementById('registerBtn');

    termsCheckbox.addEventListener('change', function() {
        registerBtn.disabled = !this.checked;
        registerBtn.style.opacity = this.checked ? '1' : '0.5';
        registerBtn.style.cursor = this.checked ? 'pointer' : 'not-allowed';
    });

    // Password toggle
    document.getElementById("togglePassword").addEventListener("click", function () {
        const field = document.getElementById("id_password");
        field.type = field.type === "password" ? "text" : "password";
        this.classList.toggle("fa-eye");
        this.classList.toggle("fa-eye-slash");
    });

    document.getElementById("toggleConfirmPassword").addEventListener("click", function () {
        const field = document.getElementById("id_confirm_password");
        field.type = field.type === "password" ? "text" : "password";
        this.classList.toggle("fa-eye");
        this.classList.toggle("fa-eye-slash");
    });

});