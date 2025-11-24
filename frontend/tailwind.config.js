/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'deep-indigo': '#1E2A4A',
        'soft-ice': '#F0F4F8',
        'sea-mint': '#66CCB6',
        'soft-coral': '#FF8866',
        'text-primary': '#FFFFFF',
        'text-secondary': '#A8B3C4',
      },
      fontFamily: {
        sans: ['Inter', 'Manrope', 'system-ui', 'sans-serif'],
        mono: ['ui-monospace', 'monospace'],
      },
      borderRadius: {
        'xl': '16px',
        '2xl': '24px',
      },
      backdropBlur: {
        'glass': '12px',
      },
    },
  },
  plugins: [],
}
