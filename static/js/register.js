// Handle registration form submission
async function handleRegister(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    if (password !== confirmPassword) {
        alert('Пароли не совпадают!');
        return;
    }
    
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    try {
        // Disable button during request
        submitButton.disabled = true;
        submitButton.textContent = 'Регистрация...';
        
        // Call register API
        await window.API.auth.register(email, password);
        
        // Redirect to dashboard on success
        window.location.href = '../dashboard.html';
    } catch (error) {
        console.error('Registration failed:', error);
        alert('Ошибка регистрации: ' + error.message);
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    }
}
