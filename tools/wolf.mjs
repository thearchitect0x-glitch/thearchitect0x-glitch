// The wolf of the day: once a day the wolf moves to a random spot on the profile, with a random look and a line.
// Slots are <!--wolf:NAME-->…<!--/wolf:NAME--> pairs in README.md; every slot is emptied, one is filled.
import { readFileSync, writeFileSync } from 'node:fs';
const README = new URL('../README.md', import.meta.url);
const looks = ['wolf-shades.jpg', 'wolf-cheese.jpg', 'wolf-cheese-full.jpg', 'wolf-back.jpg'];
const lines = [
  'you found the wolf. tell no one.',
  'the wolf was here. the cheese was not.',
  'cheese tax collected. carry on.',
  'he moves every day. come back tomorrow.',
  'unpaid intern. paid in cheese.',
  'head of security (self-appointed).',
  'he read your agent logs. he has notes.',
];
const day = process.env.WOLF_DAY ?? new Date().toISOString().slice(0, 10);
let seed = [...day].reduce((h, c) => (Math.imul(h ^ c.charCodeAt(0), 2654435761) >>> 0), 2166136261);
const rand = (n) => { seed = (Math.imul(seed ^ (seed >>> 15), 2246822519) >>> 0); return seed % n; };
let md = readFileSync(README, 'utf8');
const slots = [...md.matchAll(/<!--wolf:([a-z]+)-->/g)].map((m) => m[1]);
const pick = slots[rand(slots.length)], look = looks[rand(looks.length)], line = lines[rand(lines.length)];
const side = ['left', 'center', 'right'][rand(3)], width = 90 + rand(5) * 15;
for (const s of slots) {
  const body = s === pick ? `\n<p align="${side}"><img src="assets/${look}" width="${width}" alt="the wolf"><br><sub><i>${line}</i></sub></p>\n` : '';
  md = md.replace(new RegExp(`<!--wolf:${s}-->[\\s\\S]*?<!--/wolf:${s}-->`), `<!--wolf:${s}-->${body}<!--/wolf:${s}-->`);
}
writeFileSync(README, md);
console.log(`wolf ${day}: ${pick} · ${look} · ${side} · "${line}"`);
