# What SCORM packages actually look like

Learned from importing real Rise and Storyline courses into a production LMS
product, and checked against public packages (see the plugin's `tests/`).

## The standard: `imsmanifest.xml`

- Must sit at the **zip root**. The commonest packaging mistake is zipping the
  folder instead of its contents; every LMS rejects that. The kit reads through
  the extra folder and warns.
- The version is `<metadata><schemaversion>`: `1.2`, `2004 3rd Edition`,
  `2004 4th Edition`. `CAM 1.3` means 2004 **2nd** Edition. SCORM 1.1 has no
  manifest at all — it ships `CSF.xml`.
- Some 1.2 manifests omit `schemaversion`; the `adlcp_rootv1p2` namespace still
  identifies them. 2004 uses `adlcp_v1p3`.
- The outline is `<organizations default="…">` → `<organization>` → nested
  `<item identifierref="…">`. An item points at a `<resource>`; `adlcp:scormtype`
  (1.2) / `adlcp:scormType` (2004) says whether it is a `sco` (talks to the LMS)
  or an `asset`.
- `xml:base` on `<resources>` or `<resource>` prefixes every `href` under it.
  Ignoring it silently resolves to the wrong file.
- `item@parameters` is appended to the resource `href` (often a query string).
- Mastery score: `adlcp:masteryscore` (1.2), `imsss:minNormalizedMeasure` (2004).
- Never expand XML entities from a manifest (billion-laughs); the kit refuses
  any manifest that declares one.
- The manifest does **not** survive most hosting pipelines: anything that reads
  a package after it was unpacked must be told the version separately.

## Articulate Rise 360

Layout: `scormdriver/` (Rustici LMS bridge, the manifest's launch file) frames
`scormcontent/index.html`, which is a self-sufficient runtime. A Rise *web*
export is just the `scormcontent/` folder, no manifest.

Fingerprint: `lib/rise/` under the content root.

The authored course is JSON, base64-encoded, shipped in **one of three places**:

1. `scormcontent/runtime-data.js` (classic exports)
2. inlined into `scormcontent/index.html` (newer exports)
3. `scormcontent/locales/<lang>.js`, loaded through `__resolveJsonp("course:<lang>", "<base64>")`
   (localised exports — `und.js` when no language is set)

Decode: take the longest base64 run that decodes to an object with a `course` key.

Model: `course.lessons[]`. A lesson with `type: "section"` is a heading for the
lessons after it, not something a learner plays. `type: "quiz"` lessons hold
questions directly in `items`. Every other lesson's `items[]` are blocks with
`family` + `variant` (`text/heading paragraph`, `image/full`, `multimedia/video`,
`interactive/accordion`, `interactive-fullscreen/timeline`, `flashcard`,
`knowledgeCheck/multiple choice`, `360/storyline`, `continue`, …).

Authored words live in `heading`, `title`, `paragraph`, `description`,
`caption`, `name` of a block's sub-items, as HTML. `settings`, `background` and
`media.tmp` hold styling and Rise's stock placeholder images, not content.

Images: `media.image.crushedKey` is the published copy, `key` is often the
author's library path that the package does not ship. Keys can be URL-encoded
(`health%20app.jpg` for `health app.jpg`). Resolve by matching the longest
path tail any shipped file has; refuse a tail two files share.

**Answer keys are recorded three ways and they disagree** when an author has
switched a question's type:

- `correct` (one answer id) — authoritative for `MULTIPLE_CHOICE` in quiz lessons
- `corrects` (ids) — authoritative for `MULTIPLE_RESPONSE`
- per-answer `correct: true` — the only key in knowledge-check blocks; stale
  elsewhere

In the public Section 508 course, 8 of 10 quiz questions have `correct` and
`corrects` pointing at different answers; `correct` is the one the feedback
text agrees with. One knowledge check flags two answers on a single-answer
question — an authoring error the kit reports instead of resolving.

**Feedback is also recorded more than once.** `feedbackType` decides what the
learner sees: `ANY` → `feedback`; `CORRECT_INCORRECT` → `feedbackCorrect` /
`feedbackIncorrect`; per-answer `feedback` otherwise. The unused fields keep
whatever template text the block was created with — the public Accessible
Meetings course carries a stale `feedbackCorrect` about "Kaylee" and "The Gizmo"
on every `ANY` question.

Alt text is `media.image.alt`. A decorative image's alt is the two-character
string `""`, which is not a description.

A `360/storyline` block embeds a full Storyline publish under
`assets/<id>/` (see below); the kit reads its slides too.

Newer Rise builds set `loadOnlyInLms: true` and refuse to render outside an
LMS — relevant only if you re-host the runtime, not for reading content.

## Articulate Storyline 360

Fingerprint: `html5/data/js/data.js`. Flash-era publishes (`story.swf`) have no
`html5/` folder and nothing readable.

Every file under `html5/data/js/` is `window.globalProvideData('<kind>', '<json>')`
behind a UTF-8 BOM. The payload is a JS single-quoted string: only `\'` and `\\`
are the envelope's escaping; everything else belongs to the JSON. Kinds:
`data` (course: scenes, `assetLib` media registry, scoring), `frame` (player
chrome), `paths` (vector artwork **and the painted text**), one `slide` per slide.

- Slide order comes from `data.js → scenes[].slides[]`, not file names.
  `isMessageScene` scenes are player prompts, not content.
- On-screen text: any object's `textLib[].vartext.blocks[].spans[].text`. One
  block per object, not per span (a label is split into a span per formatting run).
- Bare page numbers ("9") are slide furniture.
- `imagedata.altText` defaults to the dropped-in file name (`BASE.png`); that is
  not a caption.
- Video: `video.data.videodata.assetId` → `assetLib[id].url`. Text burnt into a
  video cannot be extracted.
- Scored objects: `kind: "question"` (graded) and `kind: "interaction"`. Their
  answer keys are not in the publish in a readable form — the kit leaves them
  unknown (`correct: null`) rather than guessing.
- Layout is vector artwork with pre-computed glyph advances: text is readable,
  not reflowable.

## Everything else

Plain HTML SCOs (hand-built, Rustici "Golf" examples, many Captivate/iSpring
HTML5 exports): read the manifest outline, then the visible text, `<img>` and
`<video>/<audio>` of the item's `href` and of every HTML file its resource
lists. Pages that build their content in JavaScript (most quiz SCOs, most
framework runtimes) yield little or no text — the kit reports which.

## Formats deliberately not supported

| Format | How to recognise it | Why left out |
|---|---|---|
| SCORM 1.1 | `CSF.xml`, no manifest | obsolete since 2001 |
| SCORM 2004 2nd Ed | `schemaversion` = `CAM 1.3` | superseded; re-publish as 3rd/4th |
| AICC | `.au` / `.crs` / `.des` files | different standard |
| xAPI / Tin Can | `tincan.xml` | different standard |
| cmi5 | `cmi5.xml` | different standard |

## Prompt injection: what the kit does and does not do

A package is third-party content, so its text can be written to look like
instructions to whichever model reads the kit. Defences, from strongest:

1. **The model treats course content as data.** `SKILL.md` and rule 0 of
   `instructions.md` say so, and every unit file opens with a data-only banner.
   This is the actual boundary.
2. **Package words stay out of the trusted file.** Warnings in `instructions.md`
   carry only ids, paths reduced to `[A-Za-z0-9._/-]`, and numbers. Titles are
   flattened to one line, and withheld when they read like instructions.
3. **A heuristic flag.** Text that addresses an AI or tells it to ignore its
   instructions is listed as a warning, which `SKILL.md` tells the model to
   relay. Unicode is NFKC-normalised and zero-width characters stripped first.
   Rewording will get past any pattern, so treat the flag as a courtesy to the
   user, never as proof that a package is clean.
