// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: { 
    extend: {
      animation: {
        'bounce': 'bounce 1.4s infinite both',
      }
    } 
  },
  plugins: [],
}
