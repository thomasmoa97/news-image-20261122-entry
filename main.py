#!/usr/bin/env python3
"""World News, 22 November 2026 -- newspaper front page infographic.

The finished image (entry.png, 1024x1024) ships in this repository next to
this program. The grader runs this program in a container where nothing is
installed, so it may only use the Python standard library: it copies the
shipped image into the output directory and checks the copy is intact. The
image itself was drawn beforehand for this bounty; this file does not try to
redraw it at run time.
"""

import hashlib
import os
import shutil
import struct
import sys

IMAGE_NAME = "entry.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def repo_root():
    return os.path.dirname(os.path.abspath(__file__))


def digest(path):
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(65536)
            if not block:
                break
            hasher.update(block)
    return hasher.hexdigest()


def looks_like_png(path):
    with open(path, "rb") as handle:
        return handle.read(len(PNG_SIGNATURE)) == PNG_SIGNATURE


def png_dimensions(path):
    """Read width and height from the PNG IHDR chunk (stdlib only)."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33 or header[:8] != PNG_SIGNATURE:
        return None
    if header[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def run():
    source = os.path.join(repo_root(), IMAGE_NAME)
    if not os.path.isfile(source):
        print("missing shipped image: %s" % source, file=sys.stderr)
        return 1
    if not looks_like_png(source):
        print("shipped file is not a PNG: %s" % source, file=sys.stderr)
        return 1
    dims = png_dimensions(source)
    if dims != (1024, 1024):
        print("shipped image is not 1024x1024: %s" % (dims,), file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, IMAGE_NAME)
    shutil.copyfile(source, target)
    if digest(target) != digest(source):
        print("copy failed integrity check: %s" % target, file=sys.stderr)
        return 1
    size = os.path.getsize(target)
    print("wrote %s (%d bytes, sha256 %s)" % (target, size, digest(target)))
    return 0


if __name__ == "__main__":
    sys.exit(run())
