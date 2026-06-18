/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        void: "#0A0C10",
        panel: "#14171D",
        raised: "#1B1F27",
        line: "#262B33",
        ink: "#E8EAED",
        dim: "#8B92A0",
        key: "#4FD1C5",
        shard: "#F0A857",
        danger: "#E2574C",
      },
      fontFamily: {
        display: ['"Space Mono"', "monospace"],
        body: ['"IBM Plex Sans"', "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
    },
  },
  plugins: [],
};
