import cfg from '../../site.config.json';

export const SITE = cfg;

/** A path inside the site, whatever base it is served under. */
export function href(path = ''): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  return `${base}/${path.replace(/^\//, '')}`;
}

export const verseHref = (k: number, s: number, v: number) => href(`${k}/${s}/${v}/`);
export const sargaHref = (k: number, s: number) => href(`${k}/${s}/`);
export const kandaHref = (k: number) => href(`${k}/`);
export const cidHref = (cid: string) => href(`v/${cid}/`);

const DEV = '०१२३४५६७८९';
export const deva = (n: number) => String(n).replace(/\d/g, (d) => DEV[+d]);

/** The illustrations. Every set in site.config.json is published and the
 *  visitor switches between them (see ArtImg and the switch on the home page);
 *  `art.set`, or ART_SET in the environment for one build, is the first-visit
 *  default. */
export type ArtSet = (typeof cfg.art.sets)[keyof typeof cfg.art.sets];
export type ArtName = keyof typeof cfg.art.sets;
export const ART_SETS = cfg.art.sets as Record<ArtName, ArtSet>;
export const ART_NAMES = Object.keys(ART_SETS) as ArtName[];
export const ART_DEFAULT = (process.env.ART_SET || cfg.art.set) as ArtName;
if (!ART_NAMES.includes(ART_DEFAULT)) throw new Error(`ART_SET=${ART_DEFAULT}: no such set in site.config.json (${ART_NAMES.join(', ')})`);
/** URL of an image in a set. */
export const artUrl = (set: ArtName, file: string) => href(`images/art/${set}/${file}`);
/** CSS that shows the chosen set's elements and hides the others' (display:
 *  none also keeps a lazy image from being fetched). */
export const ART_CSS = ART_NAMES.map((n) =>
  `html[data-art="${n}"] .art:not(.art-${n})` + (n === ART_DEFAULT ? `, html:not([data-art]) .art:not(.art-${n})` : '') + '{display:none!important}'
).join('');
/** Runs in <head> before the page is drawn: apply the visitor's saved choice. */
export const ART_BOOT = `try{var a=localStorage.getItem('ramayana-art');if(${JSON.stringify(ART_NAMES)}.indexOf(a)>=0)document.documentElement.dataset.art=a}catch(e){}`;
