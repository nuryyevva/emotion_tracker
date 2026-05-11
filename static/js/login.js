// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    try {
        // Disable button during request
        submitButton.disabled = true;
        submitButton.textContent = 'Вход...';
        
        // Call login API
        await window.API.auth.login(email, password);
        
        // Redirect to dashboard on success
        window.location.href = '../dashboard.html';
    } catch (error) {
        console.error('Login failed:', error);
        alert('Ошибка входа: ' + error.message);
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    }
}
