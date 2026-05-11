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
async function saveProfile() {
    const timezone = document.getElementById('timezone').value;
    
    try {
        await window.API.users.updateProfile({ timezone });
        showToast('Профиль обновлён!');
    } catch (error) {
        console.error('Failed to update profile:', error);
        alert('Ошибка обновления профиля: ' + error.message);
    }
}

// Save notification settings
async function saveNotifications() {
    const notificationData = {
        reminders_enabled: document.getElementById('reminders-enabled').checked,
        channel: document.getElementById('notify-channel').value,
        frequency: document.getElementById('notify-frequency').value,
        window_start: document.getElementById('notify-window-start').value,
        window_end: document.getElementById('notify-window-end').value,
    };
    
    try {
        await window.API.notifications.updatePreferences(notificationData);
        showToast('Настройки уведомлений сохранены!');
    } catch (error) {
        console.error('Failed to update notifications:', error);
        alert('Ошибка сохранения настроек: ' + error.message);
    }
}

// Add hobby
async function addHobby() {
    const hobbyInput = document.getElementById('new-hobby');
    const hobbyName = hobbyInput.value.trim();

    if (hobbyName) {
        try {
            await window.API.users.addHobby(hobbyName);
            
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
            showToast('Хобби добавлено!');
        } catch (error) {
            console.error('Failed to add hobby:', error);
            alert('Ошибка добавления хобби: ' + error.message);
        }
    }
}

// Remove hobby
async function removeHobby(button) {
    const hobbyTag = button.closest('span');
    const hobbyName = hobbyTag.childNodes[0].textContent.trim();

    try {
        await window.API.users.removeHobby(hobbyName);
        hobbyTag.remove();
        showToast('Хобби удалено!');
    } catch (error) {
        console.error('Failed to remove hobby:', error);
        alert('Ошибка удаления хобби: ' + error.message);
    }
}

// Add coping method
async function addCopingMethod() {
    const methodInput = document.getElementById('new-coping-method');
    const methodName = methodInput.value.trim();

    if (methodName) {
        try {
            await window.API.users.addCopingMethod(methodName);
            
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
            showToast('Способ добавлен!');
        } catch (error) {
            console.error('Failed to add coping method:', error);
            alert('Ошибка добавления способа: ' + error.message);
        }
    }
}

// Remove coping method
async function removeCopingMethod(button) {
    const methodTag = button.closest('span');
    const methodName = methodTag.childNodes[0].textContent.trim();

    try {
        await window.API.users.removeCopingMethod(methodName);
        methodTag.remove();
        showToast('Способ удалён!');
    } catch (error) {
        console.error('Failed to remove coping method:', error);
        alert('Ошибка удаления способа: ' + error.message);
    }
}

// Delete account
async function deleteAccount() {
    if (confirm('Вы уверены, что хотите удалить аккаунт? Это действие необратимо.')) {
        try {
            await window.API.users.deleteAccount();
            window.API.auth.logout();
        } catch (error) {
            console.error('Failed to delete account:', error);
            alert('Ошибка удаления аккаунта: ' + error.message);
        }
    }
}

// Logout function
function logout() {
    window.API.auth.logout();
}

// Load user data on page load
async function loadUserData() {
    try {
        // Load profile
        const profile = await window.API.users.getProfile();
        if (profile.timezone) {
            document.getElementById('timezone').value = profile.timezone;
        }
        
        // Load settings
        const settings = await window.API.users.getSettings();
        if (settings) {
            if (settings.reminders_enabled !== undefined) {
                document.getElementById('reminders-enabled').checked = settings.reminders_enabled;
            }
            if (settings.notify_channel) {
                document.getElementById('notify-channel').value = settings.notify_channel;
            }
            if (settings.notify_frequency) {
                document.getElementById('notify-frequency').value = settings.notify_frequency;
            }
            if (settings.notify_window_start) {
                document.getElementById('notify-window-start').value = settings.notify_window_start;
            }
            if (settings.notify_window_end) {
                document.getElementById('notify-window-end').value = settings.notify_window_end;
            }
        }
        
        // Load hobbies
        if (profile.hobbies) {
            const hobbiesList = document.getElementById('hobbies-list');
            hobbiesList.innerHTML = '';
            profile.hobbies.forEach(hobby => {
                const hobbyTag = document.createElement('span');
                hobbyTag.className = 'inline-flex items-center gap-2 px-4 py-2 bg-brand-sky/50 text-brand-sageDark rounded-full text-sm';
                hobbyTag.innerHTML = `
                    ${hobby}
                    <button onclick="removeHobby(this)" class="hover:text-red-500 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                `;
                hobbiesList.appendChild(hobbyTag);
            });
        }
        
        // Load coping methods
        if (profile.coping_methods) {
            const methodsList = document.getElementById('coping-methods-list');
            methodsList.innerHTML = '';
            profile.coping_methods.forEach(method => {
                const methodTag = document.createElement('span');
                methodTag.className = 'inline-flex items-center gap-2 px-4 py-2 bg-purple-50 text-purple-700 rounded-full text-sm';
                methodTag.innerHTML = `
                    ${method}
                    <button onclick="removeCopingMethod(this)" class="hover:text-red-500 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                `;
                methodsList.appendChild(methodTag);
            });
        }
        
        toggleNotifications();
    } catch (error) {
        console.error('Failed to load user data:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadUserData();
});
