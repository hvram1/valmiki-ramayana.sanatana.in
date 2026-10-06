"""Build the site's data from the text, the alignment and shloka_setu.

    python3 scripts/prepare_data.py --kandas 1

Reads (paths are flags; the defaults are the sibling checkouts):
  ../valmiki-ramayana/xml/K0n.xml              the text
  ../audio-ingest/build/aligned/vr-k.s.json    verse and word times
  ../sharadapeetham/shloka_setu                the content address
  archive.org metadata for the recording       file name of each sarga's mp3

Writes, all committed so the site builds anywhere without the siblings:
  src/data/kandas.json         kāṇḍa and sarga names, verse counts
  src/data/k<k>/<sss>.json     one sarga: verses, tokens, word times, audio
  src/data/cid.json            content id -> [k, s, v] places it occurs
  public/search/k<k>.json      search rows: [k, s, v, text, roman]
"""
import argparse
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
PROJECTS = os.path.dirname(SITE)

IA_ITEM = 'Ramayana-recitation-Sriram-harisItArAmamUrti-Ghanapaati-v2'
IA_META = 'https://archive.org/metadata/' + IA_ITEM
IA_DOWNLOAD = 'https://archive.org/download/' + IA_ITEM + '/'

PUNCT = re.compile(r'^[|।॥0-9०-९,\-–—]+$')


def content_id(text):
    """shloka_setu's verse id."""
    from shloka_setu.translit import keys
    from shloka_setu.index import unit_id
    strict, _ = keys(text)
    return unit_id('V', strict)


def numeral(s):
    return int(s.translate(str.maketrans('०१२३४५६७८९', '0123456789')))


def tokens(text, words, first):
    """Split a verse into display tokens, each tied to the aligned word it
    is (index into the sarga's word list) or None for punctuation and the
    edition's marks ('-', 'यद्वा' dashes, '4,5'). Returns (tokens, unmatched)."""
    out, j = [], first
    for tok in text.split():
        if j < len(words) and tok == words[j]['w']:
            out.append([tok, j])
            j += 1
        else:
            out.append([tok, None])
    return out, j


def load_text(xml_dir, k):
    root = ET.parse(os.path.join(xml_dir, 'K%02d.xml' % k)).getroot()
    kanda = root.find('.//kanda')
    sargas = []
    for sarga in kanda.findall('sarga'):
        s = int(sarga.get('id').split('_S')[1])
        verses = []
        for sh in sarga.findall('shloka'):
            sid = sh.get('shl_id')
            st = sh.find('shloka_text')
            # A speaker line (<uvacha>तम् उवाच</uvacha>) opens 33 verses. It is
            # chanted, so it is shown and lit, but it is not the verse:
            # shloka_setu keeps uvacha apart, and the content id leaves it out.
            uv = st.find('uvacha')
            uvacha = ' '.join(uv.text.split()) if uv is not None else None
            text = ' '.join(''.join(st.itertext()).split())
            m = re.search(r'॥\s*([०-९0-9]+)\s*॥\s*$', text)
            body = text[:m.start()].strip() if m else text
            verses.append({'sid': sid, 'n': int(sid.split('_V')[1]),
                           'text': body, 'uvacha': uvacha})
        col = sarga.find('colophon')
        sargas.append({'s': s, 'name': sarga.get('name'), 'verses': verses,
                       'colophon': (col.text or '').strip() if col is not None else None})
    return kanda.get('name'), sargas


def ia_files(cache):
    if os.path.exists(cache):
        meta = json.load(open(cache))
    else:
        with urllib.request.urlopen(IA_META) as r:
            meta = json.load(r)
        json.dump(meta, open(cache, 'w'))
    return {os.path.basename(f['name']): f['name']
            for f in meta['files'] if f['name'].endswith('.mp3')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kandas', default='1', help='e.g. 1 or 1-6 or 1,2')
    ap.add_argument('--xml', default=os.path.join(PROJECTS, 'valmiki-ramayana', 'xml'))
    ap.add_argument('--aligned', default=os.path.join(PROJECTS, 'audio-ingest', 'build', 'aligned'))
    ap.add_argument('--shloka-setu', default=os.path.join(PROJECTS, 'sharadapeetham'))
    args = ap.parse_args()
    sys.path.insert(0, args.shloka_setu)

    ks = set()
    for part in args.kandas.split(','):
        a, _, b = part.partition('-')
        ks.update(range(int(a), int(b or a) + 1))

    data = os.path.join(SITE, 'src', 'data')
    os.makedirs(data, exist_ok=True)
    os.makedirs(os.path.join(SITE, 'public', 'search'), exist_ok=True)
    ia = ia_files(os.path.join(SITE, 'scripts', '.ia-meta.json'))

    kandas_path = os.path.join(data, 'kandas.json')
    kandas = json.load(open(kandas_path)) if os.path.exists(kandas_path) else {}
    cid_path = os.path.join(data, 'cid.json')
    cids = json.load(open(cid_path)) if os.path.exists(cid_path) else {}
    cids = {c: [p for p in ps if p[0] not in ks] for c, ps in cids.items()}

    problems = []
    for k in sorted(ks):
        kname, sargas = load_text(args.xml, k)
        os.makedirs(os.path.join(data, 'k%d' % k), exist_ok=True)
        search = []
        listing = []
        for sg in sargas:
            s = sg['s']
            al = json.load(open(os.path.join(args.aligned, 'vr-%d.%d.json' % (k, s))))
            byid = {u['id']: u for u in al['verses']}
            words = al['words']
            audio = ia.get(os.path.basename(al['audio']))
            if not audio:
                problems.append('%d.%d: no archive.org file for %s' % (k, s, al['audio']))

            verses = []
            for v in sg['verses']:
                u = byid.get(v['sid'])
                if u is None:
                    problems.append('%s: not in the alignment' % v['sid'])
                    continue
                first = next((i for i, w in enumerate(words) if w['unit'] == u['i']), len(words))
                toks, _ = tokens(v['text'], words, first)
                n_aligned = sum(1 for w in words if w['unit'] == u['i'])
                n_tied = sum(1 for t in toks if t[1] is not None)
                if n_tied != n_aligned:
                    problems.append('%s: %d of %d words tied to the text'
                                    % (v['sid'], n_tied, n_aligned))
                verse_only = v['text']
                if v['uvacha']:
                    assert verse_only.startswith(v['uvacha']), v['sid']
                    verse_only = verse_only[len(v['uvacha']):].strip()
                cid = content_id(verse_only)
                cids.setdefault(cid, []).append([k, s, v['n']])
                roman = ' '.join(words[t[1]]['r'] for t in toks if t[1] is not None)
                verses.append({'n': v['n'], 'cid': cid, 'text': v['text'], 'toks': toks,
                               'u': len(v['uvacha'].split()) if v['uvacha'] else 0,
                               't': u['t'], 'e': u['e'], 'score': u['score']})
                search.append([k, s, v['n'], v['text'], roman])

            col = next((u for u in al['verses'] if u['kind'] == 'colophon'), None)
            out = {
                'k': k, 's': s, 'kanda': kname, 'name': sg['name'],
                'audio': IA_DOWNLOAD + audio if audio else None,
                'duration': al['duration'],
                'verses': verses,
                'colophon': {'text': col['text'], 't': col['t'], 'e': col['e']} if col else None,
                # [start, end] per aligned word, indexed by the tokens above
                'words': [[w['t'], w['e']] for w in words],
            }
            with open(os.path.join(data, 'k%d' % k, '%03d.json' % s), 'w') as f:
                json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
            listing.append({'s': s, 'name': sg['name'], 'verses': len(verses)})

        kandas[str(k)] = {'k': k, 'name': kname, 'sargas': listing}
        with open(os.path.join(SITE, 'public', 'search', 'k%d.json' % k), 'w') as f:
            json.dump(search, f, ensure_ascii=False, separators=(',', ':'))
        print('K%d %s: %d sargas, %d verses' % (k, kname, len(listing), len(search)))

    # in reading order, so a rerun writes the same file
    cids = dict(sorted(((c, sorted(ps)) for c, ps in cids.items() if ps), key=lambda kv: kv[1][0]))
    json.dump(dict(sorted(kandas.items(), key=lambda kv: int(kv[0]))),
              open(kandas_path, 'w'), ensure_ascii=False, indent=1)
    json.dump(cids, open(cid_path, 'w'), separators=(',', ':'))
    shared = sum(1 for ps in cids.values() if len(ps) > 1)
    print('%d content ids, %d shared by more than one place' % (len(cids), shared))
    for p in problems:
        print('PROBLEM', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
