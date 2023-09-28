/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        "chess-font": "Helvetica,Arial,sans-serif",
      },
      colors: {
        "chess-green": "#81b64c",
        "chess-black": "#302e2b",
        "chess-brown": "#8c6f3e",
      },
    },
  },
  plugins: [],
};
