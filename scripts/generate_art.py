"""Generate the placeholder illustrations with Gemini.

    ../dharmasastra-gcp/myenv/bin/python scripts/generate_art.py OUT_DIR [slot ...] [-n N]
    ../dharmasastra-gcp/myenv/bin/python scripts/generate_art.py --install OUT_DIR slot=variant ...

The first form writes OUT_DIR/<slot>_v<i>.png, N variants per slot (default 2),
for the named slots or all of them. The second copies the chosen variants into
public/images/art/generated/ under the names the site expects, as JPEG (icons
as PNG with the white made transparent), so they can be compared with the
Wikimedia Commons set by flipping `art.set` in site.config.json.

It calls the Gemini REST API rather than the SDK: the SDK in that environment
(google-genai 1.32) cannot ask for an aspect ratio or a size. Same key file as
../harmonic/gen_panchamukhi.py. These are placeholders until an artist is
commissioned; the prompts below are also the brief for that artist.
"""
import argparse
import base64
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
KEY_FILE = os.path.join(os.path.dirname(SITE), 'dharmasastra-gcp', 'apikey')
MODEL = 'gemini-3-pro-image'
URL = 'https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent' % MODEL

# The page is #FDFAF3; an image whose ground is that colour melts into it.
STYLE = """\
Flat illustration in the manner of a contemporary Indian picture book, drawing
on Rajput and Pahari miniature painting: clean dark-brown outlines, flat colour
fills with only light shading, no gradients, no photorealism, no 3D. Palette:
saffron, turmeric yellow, vermilion, indigo, leaf green and warm browns. The
background is one flat, even cream colour, exactly #FDFAF3, with generous empty
space, and no paper texture, vignette, border or frame.
Figures in the dress of the epic period: princes in dhotī and uttarīya with
crowns, necklaces and earrings; ascetics in bark garments with matted hair tied
in a knot on the head. Rāma's skin is dark blue-grey (śyāma), as the miniatures
paint him; Lakṣmaṇa's is fair; Sītā is fair. Hanumān is a strong, dignified monkey
hero with a monkey's face, a long tail and reddish-ochre fur, wearing a small
crown, earrings and a short dhotī, as the miniatures paint him; he is never blue. Faces gentle and
dignified, in profile or three-quarter view as in miniatures.
Do not draw any writing: no words, names, labels, letters or numerals in any
script, and no signature; do not label rivers, cities or people. Any book or
palm leaf shows only faint wavy lines."""

EXILE = """\
In exile Rāma and Lakṣmaṇa wear knee-length ochre-brown bark garments, no crowns,
with their hair matted and tied up in a knot; Sītā wears a simple yellow sari
with little jewellery."""

ICON_STYLE = """\
A single-colour line drawing in dark slate (#2f3e46) on a plain pure white
background, uniform medium line weight, no fill, no shading and no colour, like
an engraver's sketch, centred with a wide empty margin. Indian subject, drawn
in the spirit of Rajput miniature line work. Do not draw any writing: no words,
letters or numerals in any script."""

# slot -> (aspect ratio, size, style, prompt)
SLOTS = {
    'banner': ('21:9', '2K', STYLE, EXILE + """

A wide website banner: a panorama of Rāma's journey from Ayodhyā to Laṅkā.
Behind everything, a very faint stylised landscape in thin pale-brown lines:
rivers, forests and mountain ranges, like an old hand-drawn sketch map, with no
recognisable modern coastline or borders and no labels.
At the far left, Rāma's home city on its river: a gateway, white palaces and
saffron pennants. Left of centre, Rāma, Sītā and Lakṣmaṇa walk
south in exile, Rāma in front with his bow, then Sītā, then Lakṣmaṇa. In the
centre, high in the sky, Hanumān flies with the mountain of healing herbs
raised on one palm, the herbs glowing softly. At the far right, the golden city
of Laṅkā on its island, surrounded by blue sea. In the bottom right corner, the
sage Vālmīki, white-bearded, in bark garments, seated under a tree writing on a
palm leaf, with a pair of krauñca cranes on a branch above him.
Keep the top third of the whole image almost empty cream, for a title."""),

    'intro': ('4:3', '2K', STYLE, """\
The sage Nārada, with a vīṇā on his shoulder, standing in the air on a small
cloud, visits the sage Vālmīki at his forest hermitage beside a quiet river.
Vālmīki, white-bearded, in bark garments, sits on a deer skin before a thatched
hut with his hands joined, listening. Two young disciples sit a little apart.
Trees full of birds; a pair of krauñca cranes stands by the water."""),

    'kanda-1': ('3:2', '2K', STYLE, """\
A king's great assembly hall. The young prince Rāma, crowned and
richly dressed, holds the great bow of Śiva and breaks it in the middle; the
two halves fly apart with a flash of light. Kings and sages along the sides
start back in wonder; the sage Viśvāmitra, white-bearded, stands behind Rāma
with Lakṣmaṇa. Sītā watches from a balcony, holding a garland of flowers."""),

    'kanda-2': ('3:2', '2K', STYLE, EXILE + """

Rāma, Sītā and Lakṣmaṇa leave the gate of Ayodhyā for the forest in a chariot
drawn by two white horses and driven by the old charioteer Sumantra. Behind
them the people of the city follow, grieving, arms raised; palaces and saffron
pennants behind."""),

    'kanda-3': ('3:2', '2K', STYLE, EXILE + """

Outside a small leaf hut in the forest, beside a river, Sītā points in
delight at a golden deer with silver spots among the trees. Rāma reaches for
his bow; Lakṣmaṇa raises one hand in warning."""),

    'kanda-4': ('3:2', '2K', STYLE, EXILE + """

On rocky mountain slopes, Hanumān kneels with joined hands before
Rāma and Lakṣmaṇa, who carry their bows. The monkey king Sugrīva and other
monkeys watch from the rocks above. Below, a lake full of lotuses."""),

    'kanda-5': ('3:2', '2K', STYLE, """\
The Aśoka grove in Laṅkā at night under a crescent moon. Sītā, in a plain
yellow sari, pale and thin, sits beneath a flowering tree, astonished. On a
branch above her, Hanumān, made small, holds out Rāma's gold signet ring to her.
Rākṣasī guards sleep at a distance among the trees."""),

    'kanda-6': ('3:2', '2K', STYLE, EXILE + """

Monkeys and bears build the bridge to Laṅkā across the ocean, carrying rocks
and whole trees; the stones float on the water. Rāma and Lakṣmaṇa stand on the
shore watching. Far off on the horizon, the golden walls of Laṅkā."""),

    'emblem': ('1:1', '1K', STYLE.replace('exactly #FDFAF3', 'pure white'), """\
A round emblem for a website, in a turmeric-yellow disc with a thin saffron
rim: the sage Vālmīki's head and shoulders in profile, white beard, matted hair
tied in a knot, holding a palm leaf. Bold, simple outlines that stay legible
when the emblem is shown 40 pixels wide. Plain white around the disc."""),

    'icon-read': ('1:1', '1K', ICON_STYLE, 'An open palm-leaf manuscript bundle resting on a low wooden reading stand.'),
    'icon-listen': ('1:1', '1K', ICON_STYLE, 'A Vedic scholar seated cross-legged, chanting, one hand raised in a gesture of recitation, a few curved sound lines rising.'),
    'icon-search': ('1:1', '1K', ICON_STYLE, 'Hanumān, the monkey, standing on a rock and shading his eyes with one hand, gazing into the distance, searching.'),
    'icon-commentary': ('1:1', '1K', ICON_STYLE, 'A scholar seated at a low desk, writing on a palm leaf with a stylus, a stack of palm leaves beside him.'),
    'icon-characters': ('1:1', '1K', ICON_STYLE, 'Rāma standing, full figure, in a crown, holding his tall bow, a quiver of arrows on his back.'),
    'icon-places': ('1:1', '1K', ICON_STYLE, 'A small sketch map: a dotted path winding past hills, a river, a forest and a temple.'),
}

# slot -> file under public/images/art/generated/
FILES = {
    'banner': 'banner.jpg', 'intro': 'intro.jpg', 'emblem': 'emblem.png',
    **{'kanda-%d' % k: 'kanda-%d.jpg' % k for k in range(1, 7)},
    **{'icon-%s' % i: 'icons/%s.png' % i for i in ('read', 'listen', 'search', 'commentary', 'characters', 'places')},
}


def generate(key, slot, out):
    aspect, size, style, prompt = SLOTS[slot]
    body = {
        'contents': [{'parts': [{'text': style + '\n\n' + prompt}]}],
        'generationConfig': {'responseModalities': ['TEXT', 'IMAGE'],
                             'imageConfig': {'aspectRatio': aspect, 'imageSize': size}},
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method='POST',
                                 headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                resp = json.load(r)
            for part in resp['candidates'][0]['content']['parts']:
                if 'inlineData' in part:
                    with open(out, 'wb') as f:
                        f.write(base64.b64decode(part['inlineData']['data']))
                    return '%s: saved %s' % (slot, os.path.basename(out))
            return '%s: no image (%s)' % (slot, resp['candidates'][0].get('finishReason'))
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (400, 403):
                return '%s: refused %d %s' % (slot, e.code, msg)
            time.sleep(5 * attempt)
        except Exception as e:
            msg = str(e)[:200]
            time.sleep(5 * attempt)
    return '%s: failed (%s)' % (slot, msg)


def install(src_dir, choices):
    from PIL import Image
    dest = os.path.join(SITE, 'public', 'images', 'art', 'generated')
    for choice in choices:
        slot, _, v = choice.partition('=')
        src = os.path.join(src_dir, '%s_v%s.png' % (slot, v or '1'))
        out = os.path.join(dest, FILES[slot])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im = Image.open(src)
        if slot.startswith('icon-'):
            # Line art: one slate ink whose opacity follows the darkness of
            # the drawing, so the lines stay solid when shown at 96 px and the
            # ground is transparent on any band colour.
            im = im.convert('L')
            im.thumbnail((288, 288), Image.LANCZOS)
            ink = im.point(lambda v: max(0, min(255, int((235 - v) * 2.4))))
            im = Image.new('RGBA', im.size, (0x2f, 0x3e, 0x46, 0))
            im.putalpha(ink)
            im.save(out, optimize=True)
        elif slot == 'emblem':
            # white ground -> transparent around the disc
            from PIL import ImageChops
            im = im.convert('RGBA')
            r, g, b, a = im.split()
            paper = ImageChops.darker(r, ImageChops.darker(g, b)).point(lambda v: 0 if v > 238 else 255)
            im.putalpha(ImageChops.multiply(a, paper))
            im.thumbnail((256, 256))
            im.save(out, optimize=True)
        else:
            im = im.convert('RGB')
            im.thumbnail((2400, 2400) if slot == 'banner' else (1500, 1500))
            im.save(out, 'JPEG', quality=82, optimize=True, progressive=True)
        print('%s <- %s (%dx%d)' % (FILES[slot], os.path.basename(src), *im.size))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out_dir')
    ap.add_argument('slots', nargs='*')
    ap.add_argument('-n', type=int, default=2, help='variants per slot')
    ap.add_argument('--install', action='store_true', help='copy chosen variants (slot=variant) into the site')
    ap.add_argument('--key', default=KEY_FILE)
    args = ap.parse_args()
    if args.install:
        return install(args.out_dir, args.slots)
    key = open(args.key).read().strip()
    os.makedirs(args.out_dir, exist_ok=True)
    jobs = [(s, os.path.join(args.out_dir, '%s_v%d.png' % (s, i)))
            for s in (args.slots or SLOTS) for i in range(1, args.n + 1)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for line in pool.map(lambda j: generate(key, *j), jobs):
            print(line, flush=True)


if __name__ == '__main__':
    sys.exit(main())
