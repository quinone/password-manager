// MyJavaScript.js

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

    document.getElementById('generate_button').addEventListener('click', function() {
        // Show the copy button when the generate button is clicked
        document.getElementById('copy_button').style.display = 'inline';
    });

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

    startLogoutTimer(); // Start timer when the page loads

    // Reset timer on user interaction
    document.addEventListener('mousemove', resetLogoutTimer);
    document.addEventListener('keydown', resetLogoutTimer);
    // Add more events as needed (e.g., click, touch)

    document.getElementById("newItemButton").addEventListener("click", function() {
        window.location.href = "/new_item";
    });

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

    // Fetch folders data from the server
    fetch('/get_folders1')
        .then(response => response.json())
        .then(data => {
            const folderSelect = document.getElementById('folder_id');
            data.forEach(folder => {
                const option = document.createElement('option');
                option.value = folder.folder_id; // Assuming folder_id is the correct property name in your data
                option.textContent = folder.folder_name;
                folderSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching folders:', error));
});

document.getElementById("preferencesForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent the form from submitting

    // Fetch values from input fields
    var vaultTimeout = document.getElementById("vaultTimeout").value;
    var themeId = document.getElementById("themeId").value;

    // Prepare data to send to the server
    var data = {
        vaultTimeout: vaultTimeout,
        themeId: themeId
    };

    // Make a POST request to save the preferences
    fetch('/save_preferences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            console.log('Preferences saved successfully.');
            // Optionally, you can update the UI to reflect the changes
            // For example, change the theme immediately after saving
            var themeCSS = themeId === "dark" ? "dark-theme.css" : "light-theme.css";
            document.getElementById("themeCSS").setAttribute("href", themeCSS);
        } else {
            console.error('Failed to save preferences.');
        }
    })
    .catch(error => console.error('Error saving preferences:', error));
});

