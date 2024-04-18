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

function displayMessages(messages, messageType) {
    // Clear existing messages
    const messageContainer = document.getElementById('message-container');
    messageContainer.innerHTML = '';

    // Create new message elements and append to the container
    messages.forEach(message => {
        const messageElement = document.createElement('p');
        messageElement.textContent = message;
        messageElement.classList.add(messageType);
        messageContainer.appendChild(messageElement);
    });
}

<script>
      // auto_logout.js

var timeout;

function startLogoutTimer() {
    timeout = setTimeout(function() {
        window.location.href = '/logout'; // Redirect to logout route on timeout
    }, 60 * 1000); // Timeout after 1 minute (in milliseconds)
}

function resetLogoutTimer() {
    clearTimeout(timeout); // Reset timer
    startLogoutTimer(); // Start timer again
}

document.addEventListener('DOMContentLoaded', function() {
    startLogoutTimer(); // Start timer when the page loads

    // Reset timer on user interaction
    document.addEventListener('mousemove', resetLogoutTimer);
    document.addEventListener('keydown', resetLogoutTimer);
    // Add more events as needed (e.g., click, touch)
});

<script>
document.getElementById("newItemButton").addEventListener("click", function() {
    window.location.href = "/new_item";
});
</script>

<script>
        // Fetch folders data from the server
        fetch('/get_folders')
            .then(response => response.json())
            .then(data => {
                const folderList = document.getElementById('folderList');
                data.forEach(folder => {
                    const row = document.createElement('tr');
                    const cell = document.createElement('td');
                    cell.textContent = folder.folder_name;
                    row.appendChild(cell);
                    folderList.appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching folders:', error));
    </script>
