import { defineConfig } from 'astro/config';
import fs from 'node:fs';

// Where the site lives is configuration, not code. site.config.json holds the
// defaults (GitHub Pages under the repo name); SITE_URL and BASE_PATH override
// them, so the custom domain is SITE_URL=https://valmiki-ramayana.sanatana.in
// BASE_PATH=/ with no change to the source.
const cfg = JSON.parse(fs.readFileSync(new URL('./site.config.json', import.meta.url)));

export default defineConfig({
  output: 'static',
  site: process.env.SITE_URL || cfg.site,
  base: process.env.BASE_PATH || cfg.base,
  trailingSlash: 'ignore',
  devToolbar: { enabled: false },
});
