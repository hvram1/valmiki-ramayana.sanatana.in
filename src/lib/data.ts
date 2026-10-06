import kandasJson from '../data/kandas.json';
import cidJson from '../data/cid.json';

/** [text, index into the sarga's words] -- null for punctuation and marks */
export type Tok = [string, number | null];

export interface Verse {
  n: number;
  cid: string;
  text: string;
  toks: Tok[];
  t: number;
  e: number;
  score: number;
}

export interface Sarga {
  k: number;
  s: number;
  kanda: string;
  name: string;
  audio: string | null;
  duration: number;
  verses: Verse[];
  colophon: { text: string; t: number; e: number } | null;
  words: [number, number][];
}

export interface KandaInfo {
  k: number;
  name: string;
  sargas: { s: number; name: string; verses: number }[];
}

export const KANDAS = Object.values(kandasJson) as KandaInfo[];
export const CIDS = cidJson as Record<string, [number, number, number][]>;

const files = import.meta.glob<Sarga>('../data/k*/*.json', { eager: true, import: 'default' });

export function sarga(k: number, s: number): Sarga {
  const d = files[`../data/k${k}/${String(s).padStart(3, '0')}.json`];
  if (!d) throw new Error(`no sarga ${k}.${s}`);
  return d;
}

export function allSargas(): Sarga[] {
  return KANDAS.flatMap((K) => K.sargas.map((S) => sarga(K.k, S.s)));
}

/** The sarga before and after, across kāṇḍa boundaries. */
export function neighbours(k: number, s: number) {
  const flat = KANDAS.flatMap((K) => K.sargas.map((S) => ({ k: K.k, s: S.s, name: S.name })));
  const i = flat.findIndex((x) => x.k === k && x.s === s);
  return { prev: flat[i - 1], next: flat[i + 1] };
}
