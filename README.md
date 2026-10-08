# SCORM Kit

Gets the content of a SCORM course back out of its LMS runtime: every lesson,
block, image and quiz answer key. The result is a folder an LLM can build from,
for example "make a single-file HTML page from lessons 1–3", a quiz bank, a
slide outline or a translation.

It's one [Agent Skill](skills/scorm-kit/SKILL.md) plus a standard-library Python
script, packaged so the same folder installs in **Claude Code**, **claude.ai**,
**Codex** and **ChatGPT**.

**Runs locally, offline.** Parsing and export are plain Python on your machine (or the
assistant's sandbox). Nothing calls AmpUp or any other API, and the viewer page loads no
remote scripts. The tests enforce this. Only `tests/fetch_fixtures.py` touches the network,
and only to download the public test packages.

```
python3 skills/scorm-kit/scripts/scorm_kit.py export course.zip --out kit/ \
  --task "Create a single-file HTML microlearning page from lessons 1-2"
```

```
kit/
  instructions.md   # what the course is, the outline, rules for the LLM, known gaps, your task
  course.json       # units[] -> blocks[] -> questions[], assets[], manifest
  units/NN-*.md     # one per lesson/slide/SCO, full text in reading order
  questions.json    # graded questions with correct answers and feedback
  assets/           # images the units use (--media all adds video/audio/PDF)
  viewer.html       # browsable overview of what was parsed (open locally, or use as an artifact)
```

## What it reads

| | |
|---|---|
| **Standards** | SCORM 1.2 · SCORM 2004 3rd Edition · SCORM 2004 4th Edition. Rise and Storyline web exports (no manifest) are read too and flagged as having no LMS tracking. |
| **Refused, with a reason** | SCORM 2004 2nd Edition (CAM 1.3), SCORM 1.1, AICC, xAPI/Tin Can, cmi5, Flash-era Storyline |
| **Articulate Rise 360** | lessons, sections, all block types, knowledge checks and quiz lessons **with answer keys**, embedded Storyline blocks. All three ways Rise ships its course data (`runtime-data.js`, inlined in `index.html`, `locales/*.js`). |
| **Articulate Storyline 360** | slides in scene order, on-screen text, pictures, slide video, question prompts (Storyline does not export its answer keys) |
| **Anything else** | the manifest outline plus the text, images and media of each SCO's HTML files |

What we learned about each format, including the traps:
[skills/scorm-kit/references/formats.md](skills/scorm-kit/references/formats.md).

## Install

**Claude Code**

```
/plugin marketplace add A79-ai/scorm-kit
/plugin install scorm-kit@scorm-kit
```

To try it from a clone without installing, run `claude --plugin-dir .` in the repo root.

**claude.ai**: zip the skill and upload it under *Settings → Capabilities → Skills*.

```bash
cd skills && zip -r ../scorm-kit-skill.zip scorm-kit -x '*/__pycache__/*'
```

**Codex** (CLI and app)

```bash
codex plugin marketplace add A79-ai/scorm-kit
```

```bash
codex plugin add scorm-kit@scorm-kit
```

**ChatGPT**: if your workspace has Skills, upload the same `scorm-kit-skill.zip`.
Otherwise, make a Custom GPT. Paste the body of `SKILL.md` as its instructions,
attach `scripts/scorm_kit.py`, `assets/viewer.html` and `references/formats.md`
as knowledge, and turn on Code Interpreter. The script needs nothing beyond
Python's standard library, so it runs in ChatGPT's sandbox.

## Test

```bash
python3 tests/fetch_fixtures.py               # public packages -> ~/.cache/scorm-kit/fixtures
python3 -m unittest discover -s tests -v
```

The synthetic tests cover every standard, every Rise data layout, Storyline, the
answer-key rules, unsafe paths (zip-slip, Windows-style paths, symlinks),
hostile course text, XML entities, the zipped-folder mistake and the offline guarantee. They
always run. The public-package tests are skipped until you run the fetch. The
public packages are:

- **Rustici "Golf Explained"** examples from [scorm.com](https://scorm.com/scorm-explained/technical-scorm/golf-examples/): HTML SCOs in SCORM 1.2, 2004 3rd and 4th Edition, plus 1.1 and 2004 2nd Edition (which must be refused).
- **GSA [Section508.gov](https://github.com/GSA/Section508.gov) online-training courses**: US-government, public-domain Rise 360 courses in two of Rise's data layouts, one with a Storyline 360 publish inside. They are published as web exports, so the fetch wraps each in an `imsmanifest.xml` to produce the package an LMS would get.

To add a package that broke something, drop it in the fixtures folder and add
a test case that names what it exercises. Issues and PRs welcome.

## License

MIT. See [LICENSE](LICENSE).
