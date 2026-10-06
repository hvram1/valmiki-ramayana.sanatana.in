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

Tilaka's commentary has a slot on every verse page and is empty until
`../valmiki-ramayana/tilaka/K0n.json` exists (`[{"text": verse, "tilaka":
commentary}]`, paragraphs split by a blank line). It is joined by content id,
never by number, as that edition numbers verses its own way; the data step
counts and lists the verses that do not join.

The audio is not hosted here: each sarga streams from the archive.org item
`Ramayana-recitation-Sriram-harisItArAmamUrti-Ghanapaati-v2`, and the player
seeks within it by the aligned times.

## Develop

    npm install
    npm run dev       # http://localhost:4321/valmiki-ramayana.sanatana.in/
    npm run build && npm run preview

## Illustrations: two sets, one switch

`art.set` in `site.config.json` chooses the illustrations, and `ART_SET` in the
environment overrides it for one build:

    ART_SET=generated npm run build     # Gemini placeholders
    ART_SET=commons npm run build       # public-domain paintings (default)

Each set lives in `public/images/art/<set>/` (banner, introduction, emblem,
six kāṇḍa cards, six feature icons) and has its own entries and credits under
`art.sets` in the config; the credits page follows the set.

- **commons**: paintings from Wikimedia Commons, public domain or CC0, chosen
  from the gallery at https://claude.ai/artifact/1RkYLLpdQ6QT2ERjpmYrR4.
- **generated**: placeholders made with Gemini until an artist is commissioned.
  The prompts are in `scripts/generate_art.py` and double as the artist's
  brief. To make more variants and install the ones you choose:

      ../dharmasastra-gcp/myenv/bin/python scripts/generate_art.py art-variants/generated banner kanda-3 -n 3
      ../dharmasastra-gcp/myenv/bin/python scripts/generate_art.py --install art-variants/generated banner=3 kanda-3=2

  `art-variants/` holds every variant made so far and is not committed.
