/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          DEFAULT: '#1a1b1e',
          100: '#333333',
          200: '#2c2c2c',
          300: '#262626',
          400: '#1f1f1f',
          500: '#191919'
        }
      }
    },
  },
  plugins: [],
}

