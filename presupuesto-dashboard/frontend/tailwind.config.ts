import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        tide: "#194d87",
        mist: "#eff4fb",
        success: "#1f9d62",
        warning: "#d1a31c",
        danger: "#d64545",
      },
      fontFamily: {
        sans: ["IBM Plex Sans", "Segoe UI", "sans-serif"],
      },
      boxShadow: {
        panel: "0 18px 40px rgba(15, 23, 42, 0.08)",
      },
      backgroundImage: {
        halo: "radial-gradient(circle at top left, rgba(25,77,135,0.18), transparent 34%), radial-gradient(circle at bottom right, rgba(209,163,28,0.14), transparent 28%)",
      },
    },
  },
  plugins: [],
} satisfies Config;
