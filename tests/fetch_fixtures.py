#!/usr/bin/env python3
"""Download the public SCORM packages the tests run against (~/.cache/scorm-kit/fixtures).

Every package here is public:

* Rustici "Golf Explained" examples (scorm.com) -- plain-HTML SCOs in SCORM 1.2,
  2004 3rd and 4th Edition, plus the 1.1 and 2004 2nd Edition ones we refuse.
* GSA Section508.gov online-training courses (US-government work, public domain)
  -- real Articulate Rise 360 exports, in two of Rise's data layouts, one with a
  Storyline 360 publish inside it. They are published as web exports, so each is
  wrapped with an imsmanifest.xml here to make the SCORM package an LMS would get.

Needs network and git. Re-running skips what is already downloaded.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Outside the plugin folder, so installing the plugin never copies them.
OUT = Path(
    os.environ.get(
        "SCORM_KIT_FIXTURES", Path.home() / ".cache" / "scorm-kit" / "fixtures"
    )
)
GOLF = "https://scorm.com/wp-content/assets/golf_examples/PIFS/{}.zip"
GOLF_PACKAGES = (
    "ContentPackagingSingleSCO_SCORM12",
    "ContentPackagingOneFilePerSCO_SCORM12",
    "ContentPackagingOneFilePerSCO_SCORM20043rdEdition",
    "SequencingPostTestRollup4thEd_SCORM20044thEdition",
    "ContentPackagingSingleSCO_SCORM11",
    "ContentPackagingSingleSCO_SCORM20042ndEdition",
)
GSA_REPO = "https://github.com/GSA/Section508.gov.git"
GSA_DIR = "assets/online-training"
GSA_COURSES = {
    # Rise, course JSON base64-inlined in index.html.
    "accessible-meetings": ("rise-inline-scorm12.zip", "1.2"),
    # Rise, course JSON in locales/und.js; has a Storyline block inside.
    "section-508-what-is-it-and-why-its-important": (
        "rise-locales-scorm2004-4th.zip",
        "2004 4th Edition",
    ),
}
STORYLINE_INSIDE = (
    "section-508-what-is-it-and-why-its-important",
    "assets/1ZMDuzLFg4bIe5e_",
)

MANIFEST = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{ident}" version="1" xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
  xmlns:adlcp="{adlcp}">
  <metadata><schema>ADL SCORM</schema><schemaversion>{version}</schemaversion></metadata>
  <organizations default="org"><organization identifier="org"><title>{title}</title>
    <item identifier="item" identifierref="res"><title>{title}</title></item>
  </organization></organizations>
  <resources><resource identifier="res" type="webcontent"
    adlcp:{stype}="sco" href="{href}"/></resources>
</manifest>
"""


def wrap(
    folder: Path,
    target: Path,
    *,
    version: str,
    title: str,
    content_root: str,
    href: str,
) -> None:
    adlcp = (
        "http://www.adlnet.org/xsd/adlcp_rootv1p2"
        if version == "1.2"
        else "http://www.adlnet.org/xsd/adlcp_v1p3"
    )
    stype = "scormtype" if version == "1.2" else "scormType"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "imsmanifest.xml",
            MANIFEST.format(
                ident=target.stem,
                adlcp=adlcp,
                version=version,
                title=title,
                stype=stype,
                href=href,
            ),
        )
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                zf.write(path, content_root + path.relative_to(folder).as_posix())
    print(f"built {target.name} ({target.stat().st_size // 1024} KB)")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in GOLF_PACKAGES:
        target = OUT / f"golf-{name}.zip"
        if not target.exists():
            # scorm.com answers 403 to Python's default User-Agent.
            req = urllib.request.Request(
                GOLF.format(name), headers={"User-Agent": "scorm-kit-tests"}
            )
            with urllib.request.urlopen(req) as resp:
                target.write_bytes(resp.read())
            print(f"downloaded {target.name}")

    wanted = [OUT / z for z, _ in GSA_COURSES.values()] + [
        OUT / "storyline-scorm12.zip"
    ]
    if all(p.exists() for p in wanted):
        return 0
    clone = OUT / "_gsa"
    if not clone.exists():
        subprocess.run(
            [
                "git",
                "clone",
                "-q",
                "--depth",
                "1",
                "--filter=blob:none",
                "--sparse",
                GSA_REPO,
                str(clone),
            ],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(clone),
                "sparse-checkout",
                "set",
                *[f"{GSA_DIR}/{c}" for c in GSA_COURSES],
            ],
            check=True,
        )
    for course, (zip_name, version) in GSA_COURSES.items():
        wrap(
            clone / GSA_DIR / course,
            OUT / zip_name,
            version=version,
            title=course,
            content_root="scormcontent/",
            href="scormcontent/index.html",
        )
    course, sub = STORYLINE_INSIDE
    wrap(
        clone / GSA_DIR / course / sub,
        OUT / "storyline-scorm12.zip",
        version="1.2",
        title="Section 508 certificate (Storyline)",
        content_root="",
        href="story.html",
    )
    shutil.rmtree(clone)
    return 0


if __name__ == "__main__":
    sys.exit(main())
