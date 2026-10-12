# Creative direction: the Deimos AI org profile (`deimos-hq/.github` → `profile/README.md`)

Written 11 Oct 2026. Facts come only from the earlier brief: the five products, OpenSSF Silver ×2, patents pending, the beta on 10 Nov 2026, 1,000 effects/month free, the 83% figure, Gaming Wall St and the four rules. Never say how anything works. No invented numbers.

The coordinator builds the hero (a Blender animated WebP: Mars, Deimos, the 3D tetrahedron that locks into the flat mark, then "DEIMOS"). Everything below is planned around that hero and does not redo it.

---

## 1. Concept

**MISSION CONTROL FOR THE AGE OF AGENTS.**

The personal page is a neon map of one mind. The company page is the **space agency**. It is quiet, enormous and exact, like a mission dossier opened on the reader's desk. Deimos is the moon that circles Mars, and its name means dread. The story the page tells: *agents are launching everywhere, someone has to run mission control, and that's us.* The page moves from orbit (the hero) to the missions (five products as mission patches), the live mission board, the Flight Rules (the four rules), a reckoning with the name ("named for dread"), the open hatch (open source), boarding (the Clockford beta) and the mission log. The register is black space, white type and one colour per mission. Motion is slow and heavy, like real hardware: nothing bounces, everything *settles*. The swagger is in the restraint.

**Palette:** void `#05040a`, starlight `#f2f0ea`, Mars rust `#c1440e` (the company accent), and the five mission colours used only inside their patches: gold, green, pink, cyan, orange. **Light theme:** a "flight manual" register: off-white paper `#fbfaf7`, black technical linework, rust as the only colour, and registration marks in the corners. Every SVG section ships as a `<picture>` dark/light pair.

**Type in SVG:** system sans at weight 900 for headlines, with 0.3 em letter-spacing in capitals, and the system mono for every label and number. No emoji.

**Hero hand-off (for the coordinator's render):** end the WebP on a frame whose bottom 40 px fade to exactly `#05040a`, so the first SVG below continues the black without a seam. GitHub can't swap an animated WebP by theme cheaply, so give the WebP itself a 22 px rounded mask and a 1 px `#ffffff1f` border. In light mode it then reads as a framed viewport onto space, which looks deliberate. Keep it under ~5 MB (960 px wide is enough for a 900 px column).

---

## 2. Running order after the hero

### S1. STATEMENT: real Markdown, centred

**Purpose:** a human sentence and search text in the first screen. See §4 for the exact block. Under it, one row of three small black shields with mono labels: `clockford.com` · `ratchetgate.com` · `github: crimp`.

### S2. THE MISSIONS: five mission patches in one row, each its own linked image

**Purpose:** the portfolio, which you can take in at a glance and click.
**Visual:** five round SVG patches (`patch-clockford.svg` … at 400×400, shown at `width="18%"`). Each is drawn as **embroidery**: a thick twill border made of short dashed strokes, satin-stitch fills made of fine parallel hatch lines at 30°, and a merrowed edge ring. Every patch has the product name curved along the top border and a one-word mission name along the bottom. Motion is restrained: a thread-sheen highlight sweeps across each patch once every 9 s, staggered by 1.2 s so the row ripples left to right.

| patch | centre motif | top arc / bottom arc | link |
|---|---|---|---|
| CLOCKFORD | **Rook** in embroidery, holding a phone up | CLOCKFORD / OVERSIGHT | clockford.com |
| RATCHET | a single gear tooth over the number 1 | RATCHET / ONCE | ratchetgate.com |
| CRIMP | a seal lifting off a page | CRIMP / ACCOUNTABLE | github crimp repo |
| MARKLODE | a dossier with a verdict stamp | MARKLODE / RECON | marklode.com |
| M.A.X | a calm line inside a band | M.A.X / BASELINE | deimoscore.com |

**Characters:** Rook appears only here, inside his own patch, because he lives in Clockford. He is rendered as a stitched silhouette traced from `rook.webp` (potrace on the alpha mask, then hatch fill), not a photo cut-out. This is the company register: characters become insignia, not actors.

**Alt (each):** "Clockford mission patch: see, approve and stop your AI agents from your phone. Patent pending; private beta 10 November 2026." Write the same pattern for each product, using its real one-liner.

### S3. MISSION BOARD: live (`board.svg`, 1280×360)

**Purpose:** proof that this is a live operation and not a pitch deck. Regenerated daily.
**Visual:** a mission-control status wall. Five rows of "telemetry" in mono type, each with a status lamp that breathes slowly. A huge countdown on the right uses a 7-segment style, `T–30 D`, and changes daily. A thin rust scan line crosses the wall every 6 s. The date stamp reads `MISSION BOARD · 11 OCT 2026 · UTC`.
**Copy (rows, each exactly true):**
- `CLOCKFORD   ▸ PRIVATE BETA   T–N DAYS · PATENT PENDING`
- `RATCHET     ▸ LIVE           1,000 EFFECTS / MONTH FREE · OPENSSF SILVER`
- `CRIMP       ▸ OPEN SOURCE    PATENT PENDING · OPENSSF SILVER`
- `MARKLODE    ▸ TAKING IDEAS   24–72 H`
- `M.A.X       ▸ IN THE LAB     OFFLINE-FIRST`

On beta day the countdown becomes `LIFTOFF` and the CLOCKFORD row turns gold.

### S4. FLIGHT RULES (`flight-rules.svg`, 1280×560)

**Purpose:** the values, said the way mission control says them. Space agencies really do keep a *Flight Rules* book: rules written in advance, so nobody improvises under pressure. That fits a company whose four rules are written to be followed.
**Visual:** one page of a bound manual, seen flat. It has a header bar (`DEIMOS AI LLC · FLIGHT RULES · REV A`), rule numbers in the margin, ruled lines and a rust **APPROVED** stamp that lands at 2.5 s with a slight rotation and ink bleed. Each rule types in, one per second.
**Copy:**
- **FR-1 · People stay in charge of what matters.**
- **FR-2 · Assume something is already inside.**
- **FR-3 · If it matters, make it provable.**
- **FR-4 · Bend, don't break.**
- Footer line on the page: *Written before the launch. Followed during it.*

Light theme: this is the one section that is *naturally* paper, and the light variant is almost identical. The dark variant puts the page on a black desk under a single cool key light, with the page edge casting a soft shadow.

### S5. NAMED FOR DREAD (`dread.svg`, 1280×420)

**Purpose:** own the name. This is the cinematic beat that makes people screenshot the page.
**Visual:** a wide black frame holding the rim of a huge planet (a rust gradient arc across the bottom). A small dark irregular moon moves slowly across the planet's lit limb over 12 s as a **transit**: as it crosses, a shadow passes over the surface and the rim light dims by 30%. Then the light comes back. When the light returns, the text resolves letter by letter with a slow 1.2 s opacity fade per word, so it reads as weight and not as a glitch.
**Copy:**
- **DEIMOS.** *(Greek: dread.)*
- **We were named for it.**
- **We build so you never feel it.**
- small: *Agents never sleep. Something has to keep watch.*

### S6. THE OPEN HATCH (`hatch.svg`, linked to the crimp repo, 1280×300)

**Purpose:** the open-source front door, aimed at engineers and contributors.
**Visual:** a heavy circular airlock hatch, seen head-on. Its locking dogs rotate open in sequence (four bolts, 0.4 s each). The hatch swings in 15° to show light from inside, and the light spills onto the type.
**Copy:** **CRIMP IS OPEN.** / An open-source decision gate for AI agents: agents submit the rule and the facts, not a conclusion. When a fact breaks, the decision withdraws itself. / *In 2022, 83% of appealed Medicare Advantage prior-auth denials were overturned.* / tags: OPEN SOURCE · PATENT PENDING · OPENSSF SILVER

### S7. BOARDING: the Clockford beta pass (`boarding-dark.svg` / `-light.svg`, linked to clockford.com, 1280×340)

**Purpose:** the one call to action on the page.
**Visual:** a boarding pass with a perforated stub. Fields in mono type: `PASSENGER: YOU` · `FLIGHT: CLOCKFORD` · `DEPARTS: 10 NOV 2026` · `GATE: clockford.com` · `CLASS: PRIVATE BETA` · `BOARDING IN: N DAYS` (live). The perforation line "tears" a hair every 8 s (a 1 px offset on the stub, then it resettles). A holographic foil strip on the stub runs a slow rust-to-gold hue shift.
**The wolf, exactly once on the org page:** a tiny embroidered wolf patch, 40 px, stitched in the stub's corner, with the field next to it reading `CREW: 1 WOLF · CHEESE DECLARED`. That's the whole appearance.
**Why so little wolf:** the company register stays cinematic and serious, and one wink rewards people who know the Architect's page. It also ties the two pages together, so the wolf hunt can include this spot (the personal page's daily Action can name `org-pass` as a hiding slot on some days).
**Copy above the pass (in the SVG):** **NOW BOARDING.** / See, approve and stop your AI agents from your phone, whichever company built them.

### S8. MISSION LOG: footer (`log-dark.svg` / `-light.svg`, 1280×220)

**Purpose:** the sign-off, the people and the lineage.
**Visual:** a ground-track line, the sinuous trace a satellite draws across a flat world map, in rust, drawn across the frame over 10 s. A small Deimos mark rides the trace. Log lines sit on the left in mono type.
**Copy:**
- `LOG 11 OCT 2026 · board refreshed · all missions nominal` (only the date changes daily; "nominal" stays fixed, and nothing is claimed beyond it)
- `FOUNDED BY THE ARCHITECT · github.com/thearchitect0x-glitch`. Link this in Markdown under the image, since SVG text can't be a link.
- `LINEAGE · co-producer, Gaming Wall St (HBO Max, 2022)`
- Last line, large: **DEIMOS AI LLC · KEEPING WATCH.**

---

## 3. Three ideas no org profile on GitHub has

1. **The real sky, every day.** The daily Action asks NASA JPL's public Horizons API for Deimos's actual position around Mars on that date, and draws a small "TONIGHT" orbit diagram into the footer: Mars, Deimos's orbit ring, and the moon at its real angle, stamped `SOURCE: JPL HORIZONS · <date>`. The data is real and changes daily, so nobody can say it's fake. The page literally tracks its namesake. If the API call fails, keep yesterday's file.
2. **Flight Rules as the values page.** No company states its principles as a signed flight-rules manual, rev-lettered and stamped. When the rules ever change, bump REV B, so the history is visible in git.
3. **A live boarding pass that counts down to the beta**, with a stowaway wolf. Theme-swapped: in light mode it's a printed pass, in dark mode it glows like a phone wallet pass at night.
4. (bonus) **Stitched mission patches.** The product row is real-looking embroidery made from vectors, with Rook stitched into his own patch.

---

## 4. Org metadata ([HAND] = owner sets in org settings)

- **Display name [HAND]:** `Deimos AI`
- **Description [HAND], 123 chars:** `Deimos AI LLC. Controls for AI agents: seen, approved, stoppable, provable. Clockford · Ratchet · Crimp · Marklode · M.A.X.`
- **Website [HAND]:** no company domain is confirmed in the facts. Use `https://clockford.com` until a Deimos domain exists (**owner to confirm**). Do not use deimoscore.com, because that is M.A.X's.
- **Email [HAND]:** `hello@clockford.com` is the only address in use (**owner to confirm** a company address).
- **Verified domains [HAND]:** verify clockford.com (plus ratchetgate.com and marklode.com if they are owned) in org settings. GitHub then shows a **Verified** badge, which is a real trust signal for a security company.
- **Avatar [HAND]:** the Deimos mark in starlight on `#05040a`, centred with 18% padding. Use a 3D still from the hero render only if it still reads at 40 px.
- **Pinned repos [HAND]:** an org can pin **only its own repos**. Transfer `crimp` (and `ratchet`, if public) into deimos-hq: GitHub keeps redirects from the old URLs, and stars and issues move with the repo. Then pin `crimp` first and `ratchet` second. Pin `.github` only if nothing else exists. Update the personal README links after the transfer.
- **Rename note:** after Deimos-Solutions → deimos-hq, the old org URL redirects only until someone claims the old name. Update every link that points to the old org.
- **Repo social previews [HAND]:** stills of the matching mission patch on black, 1280×640.

**Real-text block** (place it directly under the hero, centred):

```markdown
<h3 align="center">Mission control for AI agents.</h3>
<p align="center">
<b>Deimos AI LLC</b> builds the controls that keep people in charge of what their AI agents do: seen, approved, stoppable and provable.<br>
<a href="https://clockford.com"><b>Clockford</b></a>: see, approve and stop your AI agents from your phone, whichever company built them. Patent pending; private beta 10 Nov 2026 ·
<a href="https://ratchetgate.com"><b>Ratchet</b></a>: the effect gate for AI agents; a retried charge, deploy or email happens at most once ·
<a href="https://github.com/deimos-hq/crimp"><b>Crimp</b></a>: open-source decision gate; the decision withdraws itself when a fact breaks ·
<a href="https://marklode.com"><b>Marklode</b></a>: startup due diligence before the pitch, in 24–72 h ·
<a href="https://deimoscore.com"><b>M.A.X</b></a>: offline-first behavioral analysis for litigation teams.<br>
<sub>AI agent security · agent governance · human-in-the-loop approval · AI guardrails · OpenSSF Best Practices Silver (Ratchet, Crimp)</sub>
</p>
```

(Use the crimp link above only after the transfer. Until then, keep `thearchitect0x-glitch/crimp`.)

**Alt texts:** hero: "Deimos AI: the moon Deimos orbits Mars as the Deimos mark turns and locks into place." Board, rules, dread, hatch and pass: write each alt as its own copy, in full and in plain words. Footer: "Mission log: Deimos AI LLC, founded by the Architect."

---

## 5. Top 8 changes, in order

1. **[HAND] Display name, description, avatar, website and email**, plus fixing links after the rename. 10 minutes. This is what every link preview and every search result shows.
2. **The real-text block under the hero.** It makes the page indexable and answers "what is this" in one read.
3. **Hero hand-off details** (black fade at the bottom, rounded mask, ≤5 MB), so the WebP sits correctly in both themes and flows into the page.
4. **Flight Rules page.** One static SVG plus one stamp animation. It's the quickest piece that clearly says "this is a company".
5. **Mission board with the live countdown.** It reuses the personal page's `now()` logic, restyled into the mission-control register.
6. **Five embroidered mission patches**, each linked, with Rook stitched into Clockford's.
7. **Named for Dread transit scene and the boarding pass** (with the one stowaway wolf). These are the two screenshot moments.
8. **Transfer crimp and ratchet into the org, pin them, verify the domains, and turn on the JPL Horizons "TONIGHT" panel in the daily Action.**
