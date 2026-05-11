// Show toast notification
function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    if (toast && toastMessage) {
        toastMessage.textContent = message;
        toast.classList.remove('translate-y-20', 'opacity-0');
        setTimeout(() => {
            toast.classList.add('translate-y-20', 'opacity-0');
        }, 2000);
    }
}

// Toggle notifications visibility
function toggleNotifications() {
    const remindersEnabled = document.getElementById('reminders-enabled');
    const notificationSettings = document.getElementById('notification-settings');

    if (remindersEnabled && notificationSettings) {
        if (remindersEnabled.checked) {
            notificationSettings.classList.remove('opacity-50', 'pointer-events-none');
        } else {
            notificationSettings.classList.add('opacity-50', 'pointer-events-none');
        }
    }
}

// Save profile settings
function saveProfile() {
    const profileData = {
        timezone: document.getElementById('timezone').value
    };

    console.log('Saving profile:', profileData);
    showToast('Профиль обновлён!');
}

// Save notification settings
function saveNotifications() {
    const notificationData = {
        reminders_enabled: document.getElementById('reminders-enabled').checked,
        notify_channel: document.getElementById('notify-channel').value,
        notify_frequency: document.getElementById('notify-frequency').value,
        notify_window_start: document.getElementById('notify-window-start').value,
        notify_window_end: document.getElementById('notify-window-end').value
    };

    console.log('Saving notifications:', notificationData);
    showToast('Настройки уведомлений сохранены!');
}

// Add hobby
function addHobby() {
    const hobbyInput = document.getElementById('new-hobby');
    const hobbyName = hobbyInput.value.trim();

    if (hobbyName) {
        const hobbiesList = document.getElementById('hobbies-list');
        const hobbyTag = document.createElement('span');
        hobbyTag.className = 'inline-flex items-center gap-2 px-4 py-2 bg-brand-sky/50 text-brand-sageDark rounded-full text-sm fade-in-up';
        hobbyTag.innerHTML = `
            ${hobbyName}
            <button onclick="removeHobby(this)" class="hover:text-red-500 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        `;
        hobbiesList.appendChild(hobbyTag);
        hobbyInput.value = '';

        console.log('Adding hobby:', hobbyName);
        showToast('Хобби добавлено!');
    }
}

// Remove hobby
function removeHobby(button) {
    const hobbyTag = button.closest('span');
    const hobbyName = hobbyTag.childNodes[0].textContent.trim();

    console.log('Removing hobby:', hobbyName);
    hobbyTag.remove();
    showToast('Хобби удалено!');
}

// Add coping method
function addCopingMethod() {
    const methodInput = document.getElementById('new-coping-method');
    const methodName = methodInput.value.trim();

    if (methodName) {
        const methodsList = document.getElementById('coping-methods-list');
        const methodTag = document.createElement('span');
        methodTag.className = 'inline-flex items-center gap-2 px-4 py-2 bg-purple-50 text-purple-700 rounded-full text-sm fade-in-up';
        methodTag.innerHTML = `
            ${methodName}
            <button onclick="removeCopingMethod(this)" class="hover:text-red-500 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        `;
        methodsList.appendChild(methodTag);
        methodInput.value = '';

        console.log('Adding coping method:', methodName);
        showToast('Способ добавлен!');
    }
}

// Remove coping method
function removeCopingMethod(button) {
    const methodTag = button.closest('span');
    const methodName = methodTag.childNodes[0].textContent.trim();

    console.log('Removing coping method:', methodName);
    methodTag.remove();
    showToast('Способ удалён!');
}

// Delete account
function deleteAccount() {
    if (confirm('Вы уверены, что хотите удалить аккаунт? Это действие необратимо.')) {
        console.log('Deleting account...');
        // In real implementation, this would call the API
        window.location.href = 'login.html';
    }
}

// Logout function
function logout() {
    window.location.href = 'login.html';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Settings page loaded');
    toggleNotifications();
});
