import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#08111f',
        panel: '#0f1b30',
        accent: '#5ad7ff',
      },
    },
  },
  plugins: [],
};

export default config;
