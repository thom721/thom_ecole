/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      colors: {
            gold:  { DEFAULT:'#D4A853', dark:'#B8860B', light:'#FDE68A' },
            navy:  { DEFAULT:'#0B1F3A', light:'#162d4a' },
            teal:  { DEFAULT:'#1A7A6E', light:'#0f5e54' },
            cream: '#FAF7F2',
          },
          fontFamily: {
            serif: ['Playfair Display','Georgia','serif'],
            sans:  ['DM Sans','system-ui','sans-serif'],
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
    },
 
  },
  plugins: [],
  // Important: Pour s'assurer que toutes les classes fonctionnent
  safelist: [
    {
      pattern: /^(bg|text|border)-(slate|gray|red|orange|yellow|green|blue|purple|pink)-(50|100|200|300|400|500|600|700|800|900)$/,
    },
    {
      pattern: /^(m|p|gap|space)-(0|1|2|3|4|5|6|8|10|12|16|20|24)$/,
    },
  ],
}