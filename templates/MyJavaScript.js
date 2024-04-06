document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('login-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        var recaptchaResponse = grecaptcha.getResponse(); // Get the reCAPTCHA response

        // Check if the reCAPTCHA checkbox has been checked
        if (recaptchaResponse === '') {
            // If the checkbox has not been checked, display an error message
            document.getElementById('recaptcha-error').style.display = 'inline';
        } else {
            // If the checkbox has been checked, submit the form
            this.submit();
        }
    });
});


document.getElementById('generate_button').addEventListener('click', function() {
    // Show the copy button when the generate button is clicked
    document.getElementById('copy_button').style.display = 'inline';
});
