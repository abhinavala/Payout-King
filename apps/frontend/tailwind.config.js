/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        safe: '#10b981', // green-500
        caution: '#f59e0b', // amber-500
        critical: '#ef4444', // red-500
        violated: '#dc2626', // red-600
      },
    },
  },
  plugins: [],
}

