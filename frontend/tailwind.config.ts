/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          base: "#F6F8F4",
          surface: "#FFFFFF",
          subtle: "#EEF3EC",
        },
        border: {
          DEFAULT: "#DCE5DC",
          focus: "#059669",
        },
        text: {
          primary: "#14231A",
          secondary: "#4A5F52",
          muted: "#7A8E80",
        },
        primary: {
          DEFAULT: "#047857",
          hover: "#065F46",
          soft: "#D1FAE5",
          dark: "#064E3B",
        },
        harvest: {
          DEFAULT: "#D97706",
          soft: "#FEF3C7",
          dark: "#B45309",
        },
        earth: {
          DEFAULT: "#C2763F",
          soft: "#F6E7DA",
          dark: "#9A5B2F",
        },
        // FRESH TEAL / AQUA FOR WATER - NEVER CORPORATE BLUE!
        water: {
          DEFAULT: "#0D9488",
          soft: "#CCFBF1",
          dark: "#115E59",
        },
        risk: {
          DEFAULT: "#E11D48",
          soft: "#FFE4E6",
          dark: "#BE123C",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px rgba(20,35,26,0.06), 0 6px 18px rgba(20,35,26,0.04)',
        'card-hover': '0 4px 6px rgba(20,35,26,0.08), 0 12px 28px rgba(20,35,26,0.08)',
        'glow-primary': '0 0 20px rgba(4,120,87,0.2)',
      }
    },
  },
  plugins: [],
}
