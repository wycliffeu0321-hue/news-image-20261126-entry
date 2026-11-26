#!/usr/bin/env python3
"""Copy the poster image (entry.png, beside this script) to the output dir.

The output dir is $MAKEFUN_OUTPUT_DIR when set, else /output. After
copying, the written bytes are verified against the source bytes and
the byte count is printed.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    dst = os.path.join(OUT_DIR, "entry.png")
    shutil.copyfile(SRC, dst)
    with open(SRC, "rb") as f:
        src_bytes = f.read()
    with open(dst, "rb") as f:
        dst_bytes = f.read()
    if dst_bytes != src_bytes:
        raise SystemExit(f"verification failed: {dst} differs from {SRC}")
    print(f"wrote {dst}: {len(dst_bytes)} bytes (verified identical)")


if __name__ == "__main__":
    main()
