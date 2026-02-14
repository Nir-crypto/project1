/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef8ff',
          100: '#d8eeff',
          200: '#afd7ff',
          300: '#7dbbff',
          400: '#4a9bff',
          500: '#1f7eff',
          600: '#1362db',
          700: '#124eb1',
          800: '#15438f',
          900: '#173d76',
        },
      },
      boxShadow: {
        card: '0 20px 60px -24px rgba(15, 23, 42, 0.35)',
      },
    },
  },
  plugins: [],
}
