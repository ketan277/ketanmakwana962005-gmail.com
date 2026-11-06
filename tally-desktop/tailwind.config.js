/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tally: {
          dark: '#0e2632',
          header: '#132e39',
          border: '#376274',
          substrip: '#9cc3d5',
          bg: '#9fb3bd',
          panel: '#ffffff',
          blueHeader: '#1d5598',
          yellowActive: '#fab529',
          yellowHover: '#fde088',
          selectedRow: '#fab529',
          textDark: '#1a1a1a',
          footer: '#d6e2e9'
        }
      }
    },
  },
  plugins: [],
}
