tailwind.config = {
  theme: {
    extend: {
      colors: {
        pink: "#FA50B5",
        red: "#EA3737",
        orange: "#FF6100",
        amber: "#FFB200",
        yellow: "#FFDB08",
        green: "#00BE43",
        blue: "#0482FF",
        purple: "#AC39F2",
        bg: "#F2F2EE",
        card: "#FFFFFF",
        border: "#D7D7D0",
        text: "#111111",
        muted: "#5B5B5B",
        dark: "#121212"
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['"Space Grotesk"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
      borderRadius: {
        xl: "28px",
        "2xl": "36px",
        "3xl": "40px"
      },
      boxShadow: {
        soft: "0 10px 30px rgba(0,0,0,0.06)",
        hover: "0 20px 50px rgba(0,0,0,0.12)"
      }
    }
  }
}