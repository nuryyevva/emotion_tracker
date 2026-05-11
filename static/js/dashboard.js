// Update slider value display and apply color feedback
function updateValue(type, value) {
    // Update number display
    const displayId = `value-${type}`;
    const displayEl = document.getElementById(displayId);
    if (displayEl) {
        displayEl.textContent = value;

        // Optional: Add subtle animation to the number
        displayEl.classList.add('scale-110');
        setTimeout(() => displayEl.classList.remove('scale-110'), 100);
    }

    // Color feedback based on severity
    let colorClass = '';
    if (type === 'mood') {
        if(value < 4) colorClass = 'text-red-400';
        else if(value > 7) colorClass = 'text-green-500';
        else colorClass = 'text-blue-400';
    } else if (type === 'sleep') {
        if(value < 5) colorClass = 'text-orange-400';
        else if(value >= 7 && value <= 9) colorClass = 'text-green-500';
        else colorClass = 'text-blue-400';
    } else {
        // anxiety and fatigue
        if(value > 7) colorClass = 'text-red-400';
        else if(value > 4) colorClass = 'text-orange-400';
        else colorClass = 'text-green-500';
    }

    if(displayEl) displayEl.className = `text-lg font-bold ${colorClass}`;
}

// Save record functionality
async function saveRecord() {
    const record = {
        mood: parseInt(document.getElementById('mood').value),
        anxiety: parseInt(document.getElementById('anxiety').value),
        fatigue: parseInt(document.getElementById('fatigue').value),
        sleep_hours: parseFloat(document.getElementById('sleep').value),
        note: document.getElementById('note').value,
    };

    const submitButton = document.querySelector('button[onclick="saveRecord()"]');
    const originalText = submitButton.innerHTML;
    
    try {
        // Disable button during request
        submitButton.disabled = true;
        submitButton.innerHTML = '<svg class="w-5 h-5 opacity-80 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Сохранение...';
        
        // Call API to create emotion record
        await window.API.emotions.create(record);

        // Show success toast
        const toast = document.getElementById('toast');
        if (toast) {
            toast.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => {
                toast.classList.add('translate-y-20', 'opacity-0');
            }, 2000);
        }
        
        // Reset form
        document.getElementById('mood').value = 5;
        document.getElementById('anxiety').value = 3;
        document.getElementById('fatigue').value = 6;
        document.getElementById('sleep').value = 7.5;
        document.getElementById('note').value = '';
        updateValue('mood', '5');
        updateValue('anxiety', '3');
        updateValue('fatigue', '6');
        updateValue('sleep', '7.5');
        
    } catch (error) {
        console.error('Failed to save record:', error);
        alert('Ошибка сохранения: ' + error.message);
    } finally {
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    }
}

// Logout function
function logout() {
    window.API.auth.logout();
}

// Initialize color states on page load
document.addEventListener('DOMContentLoaded', function() {
    updateValue('mood', document.getElementById('mood').value);
    updateValue('anxiety', document.getElementById('anxiety').value);
    updateValue('fatigue', document.getElementById('fatigue').value);
    updateValue('sleep', document.getElementById('sleep').value);
});
