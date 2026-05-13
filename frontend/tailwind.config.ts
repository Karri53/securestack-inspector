// frontend/tailwind.config.ts
// Custom design tokens for the SecureStack Inspector brand.
// We're using a "midnight + electric" palette — dark slate backgrounds
// with cyan accents. Reads as serious + technical, not playful.

import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom brand colors. Hex values chosen to hit WCAG AA contrast
        // ratios on the dark background — accessibility matters and
        // recruiters' design-savvy folks will notice if it doesn't.
        brand: {
          50: "#ecfeff",
          100: "#cffafe",
          400: "#22d3ee",
          500: "#06b6d4",  // primary accent
          600: "#0891b2",
          700: "#0e7490",
        },
        ink: {
          900: "#0a0e1a",  // page background
          800: "#0f1424",
          700: "#161b2e",  // card background
          600: "#1f2538",
          500: "#2a3147",
          400: "#4b5375",
          300: "#8a92ad",
          200: "#c7cbdb",
          100: "#e8eaf2",
        },
      },
      fontFamily: {
        // Inter is the de facto modern UI font. Loaded via next/font in layout.tsx.
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "ui-monospace", "monospace"],
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-in-out",
        "slide-up": "slideUp 0.6s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;