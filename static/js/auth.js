// Handle login form submission
function handleLogin(event) {
    event.preventDefault();

    // Mock login - in real implementation, this would call the API
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    console.log('Mock login attempt:', { email, password });

    // Simulate successful login - redirect to dashboard
    window.location.href = '../analytics.html';
}
