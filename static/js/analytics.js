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

/**
 * Mood Tracker Chart Module
 * Файл: chart.js
 */
const MoodChart = {
    /**
     * 🔁 ЗАМЕНИТЕ ЭТУ ФУНКЦИЮ НА ЗАПРОС К ВАШЕМУ API
     */
    async fetchData() {
        // Пример API:
        // const response = await fetch('/api/mood-data?days=30');
        // return await response.json();
        
        return this.getMockData();
    },
    
    /**
     * Генерация мок-данных с реальными датами
     */
    getMockData() {
        const data = {
            dates: [],
            mood: [],
            anxiety: [],
            fatigue: []
        };
        
        // Генерируем даты: последние 30 дней от сегодня
        const today = new Date(); // 28 апреля 2026
        for (let i = 29; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            data.dates.push(date);
        }
        
        // Генерируем значения
        for (let i = 0; i < 30; i++) {
            const t = i / 5;
            data.mood.push(Math.max(0, Math.min(10, 6.5 + 1.5 * Math.sin(t) + (Math.random() - 0.5))));
            data.anxiety.push(Math.max(0, Math.min(10, 5.0 - 1.2 * Math.sin(t + 1) + (Math.random() - 0.5))));
            data.fatigue.push(Math.max(0, Math.min(10, 5.5 + 1.0 * Math.sin(t + 2) + (Math.random() - 0.5))));
        }
        
        return data;
    },
    
    /**
     * Форматирование даты: "28 апр"
     */
    formatDate(date) {
        const day = date.getDate();
        const month = date.toLocaleString('ru', { month: 'short' });
        return `${day} ${month}`;
    },
    
    /**
     * Отрисовка графика
     */
    render(data) {
        const svg = document.getElementById('line-chart');
        if (!svg) return;
        
        // Настройки
        const width = 1200;
        const height = 400;
        const padding = { top: 20, right: 30, bottom: 60, left: 40 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;
        
        // Очистка
        svg.innerHTML = '';
        
        // Масштабирование
        const scaleX = (i) => padding.left + (i / (data.dates.length - 1)) * chartWidth;
        const scaleY = (val) => padding.top + chartHeight - (val / 10) * chartHeight;
        
        // === СЕТКА И Y-ОСЬ (0-10 все числа) ===
        for (let val = 0; val <= 10; val++) {
            const y = scaleY(val);
            
            // Горизонтальная линия сетки
            const gridLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            gridLine.setAttribute('x1', padding.left);
            gridLine.setAttribute('y1', y);
            gridLine.setAttribute('x2', width - padding.right);
            gridLine.setAttribute('y2', y);
            gridLine.setAttribute('stroke', '#E5E7EB');
            gridLine.setAttribute('stroke-width', '1');
            gridLine.setAttribute('stroke-dasharray', val === 0 || val === 10 ? '0' : '3 3');
            svg.appendChild(gridLine);
            
            // Подпись на Y-оси
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
        
        // === X-ОСЬ (даты) ===
        // Показываем каждую 5-ю дату для читаемости
        for (let i = 0; i < data.dates.length; i += 5) {
            const x = scaleX(i);
            
            // Вертикальная линия сетки
            const vLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            vLine.setAttribute('x1', x);
            vLine.setAttribute('y1', padding.top);
            vLine.setAttribute('x2', x);
            vLine.setAttribute('y2', padding.top + chartHeight);
            vLine.setAttribute('stroke', '#F3F4F6');
            vLine.setAttribute('stroke-width', '1');
            vLine.setAttribute('stroke-dasharray', '3 3');
            svg.appendChild(vLine);
            
            // Подпись даты
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
        
        // === ОСИ ===
        // Y-ось
        const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        yAxis.setAttribute('x1', padding.left);
        yAxis.setAttribute('y1', padding.top);
        yAxis.setAttribute('x2', padding.left);
        yAxis.setAttribute('y2', padding.top + chartHeight);
        yAxis.setAttribute('stroke', '#9CA3AF');
        yAxis.setAttribute('stroke-width', '1.5');
        svg.appendChild(yAxis);
        
        // X-ось
        const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        xAxis.setAttribute('x1', padding.left);
        xAxis.setAttribute('y1', padding.top + chartHeight);
        xAxis.setAttribute('x2', width - padding.right);
        xAxis.setAttribute('y2', padding.top + chartHeight);
        xAxis.setAttribute('stroke', '#9CA3AF');
        xAxis.setAttribute('stroke-width', '1.5');
        svg.appendChild(xAxis);
        
        // === ЛИНИИ И ТОЧКИ ===
        const createPath = (values) => {
            return values.map((val, i) => 
                `${i === 0 ? 'M' : 'L'} ${scaleX(i).toFixed(1)} ${scaleY(val).toFixed(1)}`
            ).join(' ');
        };
        
        // Конфигурация серий
        const series = [
            { values: data.mood, color: '#43A047', label: 'Настроение' },
            { values: data.anxiety, color: '#FDD835', label: 'Тревожность' },
            { values: data.fatigue, color: '#3182ce', label: 'Усталость' }
        ];
        
        // Рисуем линии и точки для каждой серии
        series.forEach(seriesData => {
            // Линия
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', createPath(seriesData.values));
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke', seriesData.color);
            path.setAttribute('stroke-width', '2');
            path.setAttribute('stroke-linecap', 'round');
            path.setAttribute('stroke-linejoin', 'round');
            path.setAttribute('opacity', '0.6');
            svg.appendChild(path);
            
            // Точки (кружочки)
            seriesData.values.forEach((val, i) => {
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', scaleX(i));
                circle.setAttribute('cy', scaleY(val));
                circle.setAttribute('r', '6');
                circle.setAttribute('fill', seriesData.color);
                circle.setAttribute('stroke', '#ffffff');
                circle.setAttribute('stroke-width', '2');
                circle.setAttribute('class', 'transition-all duration-200 hover:r-6 cursor-pointer');
                
                // Тултип
                const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
                title.textContent = `${this.formatDate(data.dates[i])}: ${val.toFixed(1)}`;
                circle.appendChild(title);
                
                svg.appendChild(circle);
            });
        });
        
        // === Подпись оси X ===
        const xLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        xLabel.setAttribute('x', width / 2);
        xLabel.setAttribute('y', height - 10);
        xLabel.setAttribute('text-anchor', 'middle');
        xLabel.setAttribute('class', 'text-xs fill-gray-500 select-none');
        xLabel.setAttribute('font-family', 'Inter, sans-serif');
        xLabel.setAttribute('font-size', '12');
        xLabel.textContent = 'Дата';
        svg.appendChild(xLabel);
        
        // === Подпись оси Y ===
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
     * Инициализация
     */
    async init() {
        try {
            const data = await this.fetchData();
            this.render(data);
        } catch (error) {
            console.error('❌ Ошибка загрузки данных графика:', error);
            this.render(this.getMockData());
        }
    }
};

// Автозапуск
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => MoodChart.init());
} else {
    MoodChart.init();
}
