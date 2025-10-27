/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        // Custom dark theme colors
        'dark-bg': '#1a1a1a',
        'dark-surface': '#2d2d2d',
        'dark-elevated': '#3d3d3d',
        'accent-primary': '#5865f2',
        'accent-hover': '#4752c4',
      },
      spacing: {
        '18': '4.5rem', // Custom width for narrow sidebar
      },
    },
  },
  plugins: [],
}
