# `course.json` schema (scorm-kit 1.x)

```jsonc
{
  "kit":    { "name": "scorm-kit", "version": "1.0.0" },
  "source": { "file": "course.zip", "standard": "SCORM 1.2", "tool": "rise" },   // tool: rise | storyline | html
  "title": "…", "description": "…",
  "manifest": {                       // null for a web export with no imsmanifest.xml
    "identifier": "…", "declared_version": "1.2", "standard": "SCORM 1.2",
    "title": "…", "launch": "scormdriver/indexAPI.html", "resource_count": 1, "sequencing": false,
    "items": [{ "id", "title", "href", "scorm_type", "files": [], "mastery", "children": [] }]
  },
  "stats": { "units", "blocks", "questions", "images", "media", "words",
             "files": { "<kind>": { "files": 0, "bytes": 0 } } },
  "units": [{
    "id": "…",              // the authoring tool's id (Rise lesson id, Storyline slide id, manifest item id)
    "index": 1,             // reading order, 1-based
    "title": "…",
    "group": "…",           // Rise section / Storyline scene / manifest parent item; "" when there is only one
    "kind": "reading",      // reading | video | quiz | interactive
    "duration_ms": null,    // Storyline timeline length
    "blocks": [{
      "id": "…",
      "kind": "text",       // text | image | media | question | interactive | embed | other
      "family": "text", "variant": "heading paragraph",   // the tool's own block type names
      "text": "…",          // full plain text; "- " bullets, newlines between paragraphs
      "images": ["scormcontent/assets/x.jpg"],   // package paths that exist in the package
      "media":  ["story_content/intro.mp4"],
      "alts": { "scormcontent/assets/x.jpg": "Two people on a video call" },   // only images that have real alt text
      "questions": [{
        "id": "…", "type": "multiple_choice",     // multiple_choice | multiple_response | storyline | …
        "prompt": "…",
        "choices": [{ "text": "…", "correct": true, "feedback": "…" }],   // correct: null = not exported by the tool; feedback only when per-answer
        "feedback": "…",            // what the learner sees (correct, or any answer)
        "feedback_incorrect": "…"   // only when the tool shows different feedback for a wrong answer
      }],
      "embedded": { "tool": "storyline", "root": "…", "slides": 1 }   // only on a Rise 360/storyline block
    }]
  }],
  "questions": [ /* every block question, plus "unit_id" */ ],
  "assets": [{ "path": "…", "kind": "image", "bytes": 0, "used_by": ["<unit id>"], "copied": true }],
  "warnings": ["…"]   // things lost or suspicious; also listed in instructions.md
}
```

File kinds: `video`, `audio`, `image`, `captions`, `document`, `html`, `runtime`, `font`, `other`.
