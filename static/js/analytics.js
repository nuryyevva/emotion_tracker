// Mock data for analytics (used as fallback)
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

    // In real implementation, this would fetch from API
    console.log('Fetching analytics data...');
    
    setTimeout(() => {
        if (loadingToast) {
            loadingToast.classList.add('translate-y-20', 'opacity-0');
        }
    }, 1500);
}

// Logout function
function logout() {
    window.API.auth.logout();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Analytics page loaded');
});

/**
 * Mood Tracker Chart Module
 */
const MoodChart = {
    /**
     * Fetch data from API
     */
    async fetchData() {
        try {
            // Call the emotions history API
            const response = await window.API.emotions.getHistory({ limit: 30 });
            
            // Transform API response to chart data format
            const data = {
                dates: [],
                mood: [],
                anxiety: [],
                fatigue: []
            };
            
            if (response && response.items) {
                response.items.forEach(item => {
                    data.dates.push(new Date(item.record_date));
                    data.mood.push(item.mood);
                    data.anxiety.push(item.anxiety);
                    data.fatigue.push(item.fatigue);
                });
            }
            
            return data;
        } catch (error) {
            console.error('Failed to fetch analytics data:', error);
            // Return mock data as fallback
            return this.getMockData();
        }
    },
    
    /**
     * Generate mock data
     */
    getMockData() {
        const data = {
            dates: [],
            mood: [],
            anxiety: [],
            fatigue: []
        };
        
        // Generate dates: last 30 days from today
        const today = new Date();
        for (let i = 29; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            data.dates.push(date);
        }
        
        // Generate values
        for (let i = 0; i < 30; i++) {
            const t = i / 5;
            data.mood.push(Math.max(0, Math.min(10, 6.5 + 1.5 * Math.sin(t) + (Math.random() - 0.5))));
            data.anxiety.push(Math.max(0, Math.min(10, 5.0 - 1.2 * Math.sin(t + 1) + (Math.random() - 0.5))));
            data.fatigue.push(Math.max(0, Math.min(10, 5.5 + 1.0 * Math.sin(t + 2) + (Math.random() - 0.5))));
        }
        
        return data;
    },
    
    /**
     * Format date: "28 апр"
     */
    formatDate(date) {
        const day = date.getDate();
        const month = date.toLocaleString('ru', { month: 'short' });
        return `${day} ${month}`;
    },
    
    /**
     * Render the chart
     */
    render(data) {
        const svg = document.getElementById('line-chart');
        if (!svg) return;
        
        // Settings
        const width = 1200;
        const height = 400;
        const padding = { top: 20, right: 30, bottom: 60, left: 40 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;
        
        // Clear SVG
        svg.innerHTML = '';
        
        // Scaling
        const scaleX = (i) => padding.left + (i / (data.dates.length - 1)) * chartWidth;
        const scaleY = (val) => padding.top + chartHeight - (val / 10) * chartHeight;
        
        // Grid and Y-axis (0-10 all numbers)
        for (let val = 0; val <= 10; val++) {
            const y = scaleY(val);
            
            // Horizontal grid line
            const gridLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            gridLine.setAttribute('x1', padding.left);
            gridLine.setAttribute('y1', y);
            gridLine.setAttribute('x2', width - padding.right);
            gridLine.setAttribute('y2', y);
            gridLine.setAttribute('stroke', '#E5E7EB');
            gridLine.setAttribute('stroke-width', '1');
            gridLine.setAttribute('stroke-dasharray', val === 0 || val === 10 ? '0' : '3 3');
            svg.appendChild(gridLine);
            
            // Y-axis label
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', padding.left - 10);
            text.setAttribute('y', y + 4);
            text.setAttribute('text-anchor', 'end');
            text.setAttribute('class', 'text-xs fill-gray-400 select-none');
            text.setAttribute('font-family', 'Inter, sans-serif');
            text.setAttribute('font-size', '11');
            text.textContent = val;
            svg.appendChild(text);
        }
        
        // X-axis (dates)
        for (let i = 0; i < data.dates.length; i += 5) {
            const x = scaleX(i);
            
            // Vertical grid line
            const vLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            vLine.setAttribute('x1', x);
            vLine.setAttribute('y1', padding.top);
            vLine.setAttribute('x2', x);
            vLine.setAttribute('y2', padding.top + chartHeight);
            vLine.setAttribute('stroke', '#F3F4F6');
            vLine.setAttribute('stroke-width', '1');
            vLine.setAttribute('stroke-dasharray', '3 3');
            svg.appendChild(vLine);
            
            // Date label
            const dateText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            dateText.setAttribute('x', x);
            dateText.setAttribute('y', height - 35);
            dateText.setAttribute('text-anchor', 'middle');
            dateText.setAttribute('class', 'text-xs fill-gray-400 select-none');
            dateText.setAttribute('font-family', 'Inter, sans-serif');
            dateText.setAttribute('font-size', '10');
            dateText.textContent = this.formatDate(data.dates[i]);
            svg.appendChild(dateText);
        }
        
        // Axes
        const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        yAxis.setAttribute('x1', padding.left);
        yAxis.setAttribute('y1', padding.top);
        yAxis.setAttribute('x2', padding.left);
        yAxis.setAttribute('y2', padding.top + chartHeight);
        yAxis.setAttribute('stroke', '#9CA3AF');
        yAxis.setAttribute('stroke-width', '1.5');
        svg.appendChild(yAxis);
        
        const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        xAxis.setAttribute('x1', padding.left);
        xAxis.setAttribute('y1', padding.top + chartHeight);
        xAxis.setAttribute('x2', width - padding.right);
        xAxis.setAttribute('y2', padding.top + chartHeight);
        xAxis.setAttribute('stroke', '#9CA3AF');
        xAxis.setAttribute('stroke-width', '1.5');
        svg.appendChild(xAxis);
        
        // Lines and points
        const createPath = (values) => {
            return values.map((val, i) => 
                `${i === 0 ? 'M' : 'L'} ${scaleX(i).toFixed(1)} ${scaleY(val).toFixed(1)}`
            ).join(' ');
        };
        
        // Series configuration
        const series = [
            { values: data.mood, color: '#43A047', label: 'Настроение' },
            { values: data.anxiety, color: '#FDD835', label: 'Тревожность' },
            { values: data.fatigue, color: '#3182ce', label: 'Усталость' }
        ];
        
        // Draw lines and points for each series
        series.forEach(seriesData => {
            // Line
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', createPath(seriesData.values));
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke', seriesData.color);
            path.setAttribute('stroke-width', '2');
            path.setAttribute('stroke-linecap', 'round');
            path.setAttribute('stroke-linejoin', 'round');
            path.setAttribute('opacity', '0.6');
            svg.appendChild(path);
            
            // Points (circles)
            seriesData.values.forEach((val, i) => {
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', scaleX(i));
                circle.setAttribute('cy', scaleY(val));
                circle.setAttribute('r', '6');
                circle.setAttribute('fill', seriesData.color);
                circle.setAttribute('stroke', '#ffffff');
                circle.setAttribute('stroke-width', '2');
                circle.setAttribute('class', 'transition-all duration-200 hover:r-6 cursor-pointer');
                
                // Tooltip
                const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
                title.textContent = `${this.formatDate(data.dates[i])}: ${val.toFixed(1)}`;
                circle.appendChild(title);
                
                svg.appendChild(circle);
            });
        });
        
        // X-axis label
        const xLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        xLabel.setAttribute('x', width / 2);
        xLabel.setAttribute('y', height - 10);
        xLabel.setAttribute('text-anchor', 'middle');
        xLabel.setAttribute('class', 'text-xs fill-gray-500 select-none');
        xLabel.setAttribute('font-family', 'Inter, sans-serif');
        xLabel.setAttribute('font-size', '12');
        xLabel.textContent = 'Дата';
        svg.appendChild(xLabel);
        
        // Y-axis label
        const yLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        yLabel.setAttribute('x', 15);
        yLabel.setAttribute('y', height / 2);
        yLabel.setAttribute('text-anchor', 'middle');
        yLabel.setAttribute('class', 'text-xs fill-gray-500 select-none');
        yLabel.setAttribute('font-family', 'Inter, sans-serif');
        yLabel.setAttribute('font-size', '12');
        yLabel.setAttribute('transform', `rotate(-90, 15, ${height / 2})`);
        yLabel.textContent = 'Значение';
        svg.appendChild(yLabel);
    },
    
    /**
     * Initialize
     */
    async init() {
        try {
            const data = await this.fetchData();
            this.render(data);
        } catch (error) {
            console.error('❌ Error loading chart data:', error);
            this.render(this.getMockData());
        }
    }
};

// Auto-start
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => MoodChart.init());
} else {
    MoodChart.init();
}
