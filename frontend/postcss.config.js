 // postcss.config.js
import tailwindcss from '@tailwindcss/postcss'
import autoprefixer  from 'autoprefixer'

export default {
  plugins: {
    // this is the new PostCSS plugin entrypoint for Tailwind v4+
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  }
}
