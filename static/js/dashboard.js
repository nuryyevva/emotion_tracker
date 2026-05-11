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
function saveRecord() {
    // Mock save functionality
    const record = {
        mood: parseInt(document.getElementById('mood').value),
        anxiety: parseInt(document.getElementById('anxiety').value),
        fatigue: parseInt(document.getElementById('fatigue').value),
        sleep_hours: parseFloat(document.getElementById('sleep').value),
        note: document.getElementById('note').value,
        record_date: new Date().toISOString().split('T')[0]
    };

    console.log('Saving record:', record);

    // Show success toast
    const toast = document.getElementById('toast');
    if (toast) {
        toast.classList.remove('translate-y-20', 'opacity-0');
        setTimeout(() => {
            toast.classList.add('translate-y-20', 'opacity-0');
        }, 2000);
    }
}

// Logout function
function logout() {
    // Mock logout - redirect to login page
    window.location.href = 'login.html';
}

// Initialize color states on page load
document.addEventListener('DOMContentLoaded', function() {
    updateValue('mood', document.getElementById('mood').value);
    updateValue('anxiety', document.getElementById('anxiety').value);
    updateValue('fatigue', document.getElementById('fatigue').value);
    updateValue('sleep', document.getElementById('sleep').value);
});
