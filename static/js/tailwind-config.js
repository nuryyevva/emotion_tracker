// Tailwind Configuration
tailwind.config = {
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            colors: {
                brand: {
                    bg: '#F9FAFB',
                    sage: '#A7B5A7',
                    sageDark: '#7A8C7A',
                    sand: '#EDE6DD',
                    sky: '#E3EDF5',
                    heading: '#1F2937',
                    muted: '#6B7280'
                }
            },
            borderRadius: {
                'xl': '1rem',
                '2xl': '1.5rem',
                '3xl': '2rem',
                'full': '9999px'
            },
            boxShadow: {
                'soft': '0 10px 40px -10px rgba(0,0,0,0.08)',
                'card': '0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02)',
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }
        }
    }
};
