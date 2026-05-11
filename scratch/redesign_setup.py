import os

frontend_dir = r"d:\work\antigravity\ChasePay_v04\frontend"

# --- Tailwind Config ---
tailwind_config = """tailwind.config = {
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
}"""

with open(os.path.join(frontend_dir, "js", "tailwind-config.js"), "w", encoding="utf-8") as f:
    f.write(tailwind_config)

# --- Update auth.js ---
auth_js_path = os.path.join(frontend_dir, "js", "auth.js")
with open(auth_js_path, "r", encoding="utf-8") as f:
    auth_js = f.read()

auth_js = auth_js.replace(
    "const isLoginPage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/';",
    "const publicPages = ['index.html', 'login.html', '/'];\n    const isLoginPage = publicPages.some(page => window.location.pathname.endsWith(page));"
)
auth_js = auth_js.replace("window.location.href = 'index.html';", "window.location.href = 'login.html';")

with open(auth_js_path, "w", encoding="utf-8") as f:
    f.write(auth_js)

print("Setup tailwind config and updated auth.js")
