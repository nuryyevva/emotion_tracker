// Mock data for analytics
const mockAnalyticsData = {
    weekday_patterns: {
        "0": { day_name: "Monday", mood: 6.2, anxiety: 5.5, fatigue: 6.0, record_count: 12 },
        "1": { day_name: "Tuesday", mood: 6.8, anxiety: 4.9, fatigue: 5.5, record_count: 13 },
        "2": { day_name: "Wednesday", mood: 6.5, anxiety: 5.2, fatigue: 5.8, record_count: 11 },
        "3": { day_name: "Thursday", mood: 6.6, anxiety: 5.0, fatigue: 5.6, record_count: 10 },
        "4": { day_name: "Friday", mood: 7.2, anxiety: 4.5, fatigue: 5.2, record_count: 14 },
        "5": { day_name: "Saturday", mood: 7.5, anxiety: 4.2, fatigue: 4.8, record_count: 9 },
        "6": { day_name: "Sunday", mood: 7.3, anxiety: 4.3, fatigue: 5.0, record_count: 8 }
    },
    insights: [
        "По вторникам тревожность в среднем ниже на 0.6 пункта",
        "В выходные усталость снижается на 1.2 пункта",
        "Вы заполняете дневник 5 дней подряд — отличный прогресс!"
    ],
    averages: {
        mood: 6.8,
        anxiety: 4.2,
        fatigue: 5.1
    }
};

// Refresh analytics functionality
function refreshAnalytics() {
    // Show loading toast
    const loadingToast = document.getElementById('loading-toast');
    if (loadingToast) {
        loadingToast.classList.remove('translate-y-20', 'opacity-0');
    }

    // Simulate API call delay
    setTimeout(() => {
        if (loadingToast) {
            loadingToast.classList.add('translate-y-20', 'opacity-0');
        }

        // In real implementation, this would fetch from API
        console.log('Fetching analytics data...');
        console.log('Mock data:', mockAnalyticsData);
    }, 1500);
}

// Logout function
function logout() {
    window.location.href = 'login.html';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Analytics page loaded');
    console.log('Mock analytics data:', mockAnalyticsData);
});
