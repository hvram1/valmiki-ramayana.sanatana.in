# valmiki-ramayana.sanatana.in

The Vālmīki Rāmāyaṇa as a static site: the Sanskrit text, two addresses for
every verse, and the recitation of Sriram Harisitaramamurti Ghanapāṭhī with
each word lit as it is chanted. Astro, built from files, served by GitHub Pages.

## Addresses

- `/1/1/1/` — kāṇḍa / sarga / verse, the readable address.
- `/v/<id>/` — the content address: `shloka_setu`'s hash of the verse text
  (`blake2b('V' + strict key)`, 6 bytes). It survives renumbering. One place →
  the verse page, canonical to its readable address; the same text in several
  places → a list of them.

## Where it is served

Configuration, not code. `site.config.json` holds the name and the defaults
(`https://hvram1.github.io` + `/valmiki-ramayana.sanatana.in`); the environment
overrides them:

    SITE_URL=https://valmiki-ramayana.sanatana.in BASE_PATH=/ npm run build

In CI, set the repository variables `SITE_URL` and `BASE_PATH` (Settings →
Variables) to move it; leave them unset for GitHub Pages under the repo name.
For the custom domain also add `public/CNAME` containing the domain.

## Data

`npm run data -- --kandas 1-6` (Python 3) reads the sibling checkouts —
`../valmiki-ramayana/xml`, `../audio-ingest/build/aligned`,
`../sharadapeetham` — and archive.org's file list, and writes `src/data/` and
`public/search/`. The output is committed, so the site builds anywhere. It
prints `PROBLEM` lines and exits non-zero if a verse or word fails to line up.

The audio is not hosted here: each sarga streams from the archive.org item
`Ramayana-recitation-Sriram-harisItArAmamUrti-Ghanapaati-v2`, and the player
seeks within it by the aligned times.

## Develop

    npm install
    npm run dev       # http://localhost:4321/valmiki-ramayana.sanatana.in/
    npm run build && npm run preview
