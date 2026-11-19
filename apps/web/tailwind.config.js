/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Bricolage Grotesque"', '"Figtree"', 'sans-serif'],
        sans: ['"Figtree"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        forest: {
          50: '#f0f4f0',
          100: '#e3ebe4',
          700: '#2a4d3c',
          800: '#1f3a2e',
          900: '#16291f',
        },
        sand: {
          50: '#faf7f0',
          100: '#f4eee2',
          200: '#e9dfcc',
          300: '#d9ccb2',
        },
        terra: {
          100: '#f6e3da',
          500: '#c4704f',
          600: '#b35f3f',
        },
        ink: {
          DEFAULT: '#2b2e2c',
          soft: '#5c615d',
        },
        ok: {
          DEFAULT: '#2f7d4f',
          bg: '#e2f1e7',
        },
        warn: {
          DEFAULT: '#9a6400',
          bg: '#fbefd0',
        },
        bad: {
          DEFAULT: '#b4423a',
          bg: '#f9e3e0',
        },
        clean: {
          DEFAULT: '#23707f',
          bg: '#ddeef1',
        },
        maint: {
          DEFAULT: '#4b514d',
          bg: '#e6e6e2',
        },
      },
    },
  },
  plugins: [],
}
