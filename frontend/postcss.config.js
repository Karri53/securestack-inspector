// frontend/postcss.config.js
// PostCSS pipeline. Next.js reads this automatically.
// tailwindcss processes our @tailwind directives in globals.css and
// generates utility classes by scanning the files listed in tailwind.config.ts.
// autoprefixer adds vendor prefixes (-webkit-, -moz-) so older browsers don't break.

module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
