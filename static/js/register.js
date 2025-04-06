document.getElementById("registerForm").addEventListener("submit", function (e) {
    e.preventDefault();

    // Gather form data
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const dob = document.getElementById("dob").value;
    const password = document.getElementById("password").value;
    const bio_id = document.getElementById("bio_id").value;

    // Send data to the backend API
    fetch('/register_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, dob, password, bio_id }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                alert(data.message);
                window.location.href = '/login'; // Redirect to login page
            }
        })
        .catch((error) => console.error('Error:', error));
});
