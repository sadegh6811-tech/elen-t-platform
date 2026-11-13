import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        elen: {
          deep: "#0A1F3F",
          blue: "#1E4D8C",
          sky: "#3B9EFF",
          gold: "#FFB800",
          light: "#E8F4FF",
          sky_light: "#87CEEB",
          ocean: "#0077BE",
          ocean_light: "#4FA8D8",
          forest: "#2E7D32",
          leaf: "#4CAF50",
          meadow: "#81C784",
        },
      },
      fontFamily: {
        sans: ["Inter", "Vazirmatn", "sans-serif"],
        display: ["Inter Display", "Vazirmatn", "sans-serif"],
      },
      backgroundImage: {
        "elen-gradient":
          "linear-gradient(135deg, #E8F4FF 0%, #87CEEB 30%, #0077BE 60%, #2E7D32 100%)",
        "elen-hero":
          "linear-gradient(180deg, #E8F4FF 0%, #87CEEB 50%, #4FA8D8 100%)",
        "elen-gold": "linear-gradient(135deg, #FFB800 0%, #FBBF24 100%)",
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-in-out",
        "slide-up": "slideUp 0.5s ease-out",
        glow: "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        glow: {
          "0%": { boxShadow: "0 0 20px rgba(255, 184, 0, 0.3)" },
          "100%": { boxShadow: "0 0 40px rgba(255, 184, 0, 0.6)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
