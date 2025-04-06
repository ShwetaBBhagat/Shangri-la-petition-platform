document.getElementById('loginForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Determine the endpoint based on the email
    const endpoint = email === 'admin@petition.parliament.sr' ? '/admin/login' : '/login';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        const result = await response.json();

        if (response.ok) {
            // Redirect based on the user type
            if (email === 'admin@petition.parliament.sr') {
                alert(result.message);
                window.location.href = '/admin/dashboard';
            } else {
                alert(result.message);
                window.location.href = '/dashboard';
            }
        } else {
            // Show error message
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('An error occurred. Please try again.');
    }
});
