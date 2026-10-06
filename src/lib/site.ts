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

/** The illustrations: one set of the two in site.config.json, chosen by
 *  `art.set` or, for a single build, ART_SET in the environment. */
type ArtSet = (typeof cfg.art.sets)[keyof typeof cfg.art.sets];
const ART_NAME = (process.env.ART_SET || cfg.art.set) as keyof typeof cfg.art.sets;
if (!(ART_NAME in cfg.art.sets)) throw new Error(`ART_SET=${ART_NAME}: no such set in site.config.json (${Object.keys(cfg.art.sets).join(', ')})`);
export const ART: ArtSet & { name: string } = { ...cfg.art.sets[ART_NAME], name: ART_NAME };
/** URL of an image in the chosen set. */
export const art = (file: string) => href(`images/art/${ART_NAME}/${file}`);
