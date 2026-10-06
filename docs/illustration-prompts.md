# Illustration prompts

The prompts now live in `scripts/generate_art.py`, which sends them to Gemini
and installs the chosen results; see the README, "Illustrations: two sets, one
switch". What changed after the first trial, and why:

- Hanumān came out blue: the style now says reddish-ochre fur, crown and
  ornaments, "never blue".
- The model labelled the river "Sarayū" though told not to: places are now
  described, not named, and the style forbids labels of any kind.
- The map was a modern outline of India: it is now a faint sketch of rivers,
  forests and hills with no coastline or borders.
- The exiles wore palace clothes: bark garments and matted hair are spelled
  out wherever they are in exile.
- The ground was a yellower cream than the page: the style asks for #FDFAF3.
- The SDK in `dharmasastra-gcp/myenv` cannot ask for a size or aspect ratio,
  so the script calls the REST API, which can (2K, 21:9 for the banner).

Rejected variants worth remembering: one Bāla Kāṇḍa card put Hanumān in
Janaka's court; one Ayodhyā card left out Lakṣmaṇa. Check each image against
the story before installing it.

The earlier draft of these prompts follows, for reference.


Prompts for placeholder illustrations, to be made with Gemini (or any image
model) and replaced later by a commissioned artist. Every illustration has a
slot in `site.config.json` (`portal`), so a new image is a new file plus a
credit line; no page code changes.

Until then the slots hold public-domain paintings from Wikimedia Commons
(Mewar, Pahari, Mughal). The gallery used to choose them is at
https://claude.ai/artifact/1RkYLLpdQ6QT2ERjpmYrR4.

## How to use these

1. Paste the **style** paragraph first, then the slot's prompt, in the same
   message. Keep the style paragraph identical for every image so the set
   looks like one hand.
2. Ask for the stated aspect ratio. Generate several and keep the best.
3. **No lettering.** Image models garble Devanagari. Every title, verse and
   label on the page is set by the site; ask again if any text appears.
4. Save to the file named under each slot (JPEG, quality ~80; the banner
   about 2400 px wide, cards about 1200 px) and set its credit in
   `site.config.json` → `portal.credits`, e.g.
   `{"title": "Hanumān and the mountain", "artist": "Generated with Gemini (placeholder)", "license": "", "source": ""}`.

The Mahābhārata portal's banner (sanatana.in/mahabharata) is the model: flat,
outlined figures over a faint map, warm colour, a lot of cream ground.

## Style (paste before every prompt)

> Flat illustration in the manner of a contemporary Indian picture book, drawing
> on Rajput and Pahari miniature painting: clean dark-brown outlines, flat
> colour fills with only light shading, no gradients, no photorealism, no 3D.
> Palette: saffron, turmeric yellow, vermilion, indigo, leaf green and warm
> browns on a plain cream ground, with generous empty cream space. Figures in
> traditional Indian dress and ornament of the epic period: dhotī and uttarīya,
> crowns and earrings for princes, matted hair and bark garments for ascetics
> and for Rāma, Sītā and Lakṣmaṇa in exile. Rāma's skin is dark blue-grey
> (śyāma), as the miniatures paint him; Lakṣmaṇa's is fair. Faces gentle and
> dignified, in profile or three-quarter view as in miniatures. Absolutely no text, letters,
> numbers, captions or signatures anywhere in the image.

## Banner: `public/images/portal/banner.jpg`

Aspect ratio 21:9 (or 2:1). The site sets the title and the maṅgala verse above
the image, so keep the top edge calm.

> A wide panorama across a faint, pale-brown hand-drawn map of ancient India,
> from the river Sarayū in the north to the island of Laṅkā in the south, its
> rivers and hills drawn in thin brown lines with no labels. At the far left,
> the city of Ayodhyā with a gateway, white palaces and saffron pennants. Left of
> centre, Rāma and Lakṣmaṇa walk south with bows on their shoulders, Sītā between
> them, in forest dress. In the centre, Hanumān flies across the sky carrying a
> mountain covered in glowing herbs on his upraised palm. At the far right, the
> golden city of Laṅkā on its island, rising from blue water. Bottom right
> corner: the sage Vālmīki, white-bearded, seated under a tree writing on palm
> leaves, a pair of krauñca birds on a branch above him. Leave the upper middle
> third of the image as plain cream sky.

## Emblem: `public/images/logo.svg` (or a PNG beside it)

Square, 1:1, on a plain white background. Make it a PNG first; an artist can
redraw it as SVG later. Two directions to try:

> A round emblem: the sage Vālmīki's head and shoulders in profile, white beard,
> matted hair tied up, holding a palm-leaf manuscript, inside a turmeric-yellow
> disc. Bold outlines that stay legible at 40 pixels. Plain white background.

> A round emblem: Rāma's bow (the kodaṇḍa), strung, with a single arrow across
> it, in front of a rising sun in saffron and turmeric yellow. Bold, simple
> outlines that stay legible at 40 pixels. Plain white background.

## Introduction: `public/images/portal/intro.jpg`

Aspect ratio 4:3. Beside the opening text, which tells how the poem begins.

> The sage Nārada, with his vīṇā, visits the sage Vālmīki at his hermitage in
> the forest by the river Tamasā. Vālmīki sits on a deer skin before a thatched
> hut, hands joined, listening. Disciples sit at a little distance. Trees full
> of birds; a pair of krauñca cranes by the water.

## Kāṇḍa cards: `public/images/portal/kanda-1.jpg` … `kanda-6.jpg`

Aspect ratio 3:2 each. The card shows the image above the kāṇḍa's name, so
compose with the main action in the middle band.

1. **Bāla** (`kanda-1.jpg`)
   > In King Janaka's assembly hall, the young prince Rāma bends and breaks the
   > great bow of Śiva, which snaps in the middle with a flash. Kings and sages
   > look on in wonder; the sage Viśvāmitra stands behind him; Sītā watches from
   > a balcony holding a garland.
2. **Ayodhyā** (`kanda-2.jpg`)
   > Rāma, Sītā and Lakṣmaṇa in bark garments leave the gate of Ayodhyā in a
   > chariot driven by the charioteer Sumantra, while the people of the city
   > follow weeping with raised arms.
3. **Araṇya** (`kanda-3.jpg`)
   > Outside the leaf hut at Pañcavaṭī by the river Godāvarī, Sītā points
   > delighted at a golden deer with silver spots among the trees. Rāma reaches
   > for his bow; Lakṣmaṇa raises a hand in warning.
4. **Kiṣkindhā** (`kanda-4.jpg`)
   > On the rocky slopes of Mount Ṛṣyamūka, Hanumān kneels with joined hands
   > before Rāma and Lakṣmaṇa. Sugrīva and other vānaras watch from the rocks
   > above. Lake Pampā with lotuses below.
5. **Sundara** (`kanda-5.jpg`)
   > In the Aśoka grove of Laṅkā, small Hanumān on a branch of a śiṃśapā tree
   > offers Rāma's signet ring to Sītā, who sits beneath the tree in a plain
   > yellow garment, astonished. Rākṣasī guards asleep around her.
6. **Yuddha** (`kanda-6.jpg`)
   > Vānaras and bears build the bridge to Laṅkā across the ocean, carrying
   > rocks and whole trees; the stones float on the water. Rāma and Lakṣmaṇa
   > watch from the shore, Laṅkā's golden walls far off on the horizon.

## Feature icons: `public/images/icons/*.svg`

Square, 1:1. These are line drawings, like the Mahābhārata portal's: replace
the style paragraph with this one for the icons.

> A single-colour line drawing in dark slate (#2f3e46) on a plain white
> background, uniform medium line weight, no fill and no shading, like an
> engraver's sketch, centred with margin around it. No text.

| File | Prompt |
|---|---|
| `read.png` | An open palm-leaf manuscript bundle resting on a low wooden reading stand. |
| `listen.png` | A Vedic scholar seated cross-legged, chanting, one hand raised in a recitation gesture, faint curved sound lines rising. |
| `search.png` | Hanumān shading his eyes with one hand, gazing into the distance, searching. |
| `commentary.png` | A scholar seated at a low desk, writing on a palm leaf with a stylus, a stack of leaves beside him. |
| `characters.png` | Rāma standing, full figure, holding his bow, a quiver on his back. |
| `places.png` | A small map with a dotted path winding past hills, a river and a temple. |

Save them as PNG beside the SVGs and point `portal.icons` in
`site.config.json` at the new files.
