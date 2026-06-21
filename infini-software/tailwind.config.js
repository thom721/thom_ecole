/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      fontFamily: {
        syne: ['"Plus Jakarta Sans"', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        bg:   '#080c10',
        s1:   '#0d1219',
        s2:   '#111820',
        s3:   '#161e28',
        bd:   '#1e2a38',
        bd2:  '#253040',
        mut:  '#64748b',
        sub:  '#374151',
        cyan: { DEFAULT: '#06b6d4', dark: '#0891b2' },
        gold: { DEFAULT: '#f59e0b', dark: '#d97706' },
        ok:   '#10b981',
      },
      keyframes: {
        slideUp:   { from:{opacity:'0',transform:'translateY(60px)'}, to:{opacity:'1',transform:'translateY(0)'} },
        slideDown: { from:{opacity:'1',transform:'translateY(0)'},    to:{opacity:'0',transform:'translateY(-30px)'} },
        bounceY:   { '0%,100%':{transform:'translateY(0)'},'50%':{transform:'translateY(7px)'} },
      },
      animation: {
        'slide-up':   'slideUp .55s cubic-bezier(.16,1,.3,1) forwards',
        'slide-down': 'slideDown .35s cubic-bezier(.4,0,1,1) forwards',
        'bounce-y':   'bounceY 1.8s ease-in-out infinite',
      }
    }
  },
  plugins: []
}
