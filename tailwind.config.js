/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "chess-green": "#305730",
        "chess-brown": "#8c6f3e",
      },
    },
  },
  plugins: [],
};
