// Handle registration form submission
function handleRegister(event) {
    event.preventDefault();

    // Mock registration - in real implementation, this would call the API
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (password !== confirmPassword) {
        alert('Пароли не совпадают!');
        return;
    }

    console.log('Mock registration attempt:', { email, password });

    // Simulate successful registration - redirect to dashboard
    window.location.href = '../analytics.html';
}
