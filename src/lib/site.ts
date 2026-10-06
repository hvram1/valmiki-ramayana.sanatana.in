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
