"""Download and extract the Stack Exchange data used in the paper.

The paper uses the dump that ends on 31 March 2024 (Internet Archive item "stackexchange").
For every community this script fetches <site>.7z and extracts Posts.xml and Comments.xml into
data/<name>/. If the download is not possible (e.g. the archive requires a login), download the
.7z files manually from https://archive.org/details/stackexchange, put them into data/, and run
this script again: existing archives are not downloaded again.

Usage: python -m experiments.get_data [--sites DataScience AI ...]
"""

import argparse
import os
import urllib.request

from .config import DATA_DIR, SITES

URL = "https://archive.org/download/stackexchange/{site}.7z"
NEEDED = ("Posts.xml", "Comments.xml")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", nargs="*", default=list(SITES))
    a = ap.parse_args()
    import py7zr                                    # pip install py7zr

    os.makedirs(DATA_DIR, exist_ok=True)
    for name in a.sites:
        site = SITES[name]
        out = os.path.join(DATA_DIR, name)
        if all(os.path.exists(os.path.join(out, f)) for f in NEEDED):
            print(f"{name}: already extracted")
            continue
        archive = os.path.join(DATA_DIR, f"{site}.7z")
        if not os.path.exists(archive):
            print(f"{name}: downloading {URL.format(site=site)}")
            urllib.request.urlretrieve(URL.format(site=site), archive)
        os.makedirs(out, exist_ok=True)
        with py7zr.SevenZipFile(archive, "r") as z:
            z.extract(path=out, targets=list(NEEDED))
        print(f"{name}: extracted {', '.join(NEEDED)} to {out}")


if __name__ == "__main__":
    main()
