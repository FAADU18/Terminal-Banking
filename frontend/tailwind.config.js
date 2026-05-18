/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Poppins", "Segoe UI", "sans-serif"],
        body: ["Manrope", "Segoe UI", "sans-serif"],
      },
      colors: {
        brand: {
          50: "#f0f8ff",
          100: "#d9eeff",
          500: "#0f9bff",
          700: "#0466c8",
          900: "#033b70",
        },
      },
      boxShadow: {
        glass: "0 12px 30px -14px rgba(10, 48, 90, 0.45)",
      },
      backgroundImage: {
        "banking-gradient": "linear-gradient(135deg, #023e8a 0%, #0f9bff 45%, #80ed99 100%)",
      },
    },
  },
  plugins: [],
}

