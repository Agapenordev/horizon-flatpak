from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "dev.playhorizon.Horizon.yml"
METAINFO = ROOT / "dev.playhorizon.Horizon.metainfo.xml"
API_URL = "https://api.github.com/repos/horizon-rust/horizon/releases?per_page=100"
ARCHIVE_NAME = "horizon-launcher-linux-x86_64.tar.gz"


def request(url: str):
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": "horizon-flatpak-updater"})
    )


def write_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write(f"{name}={value}\n")


def main() -> None:
    with request(API_URL) as response:
        releases = json.load(response)

    release = next(
        release
        for release in releases
        if not release["draft"] and release["tag_name"].startswith("launcher@")
    )
    version = release["tag_name"].removeprefix("launcher@")
    asset = next(asset for asset in release["assets"] if asset["name"] == ARCHIVE_NAME)

    manifest = MANIFEST.read_text(encoding="utf-8")
    archive_pattern = re.compile(
        r"        url: https://github\.com/horizon-rust/horizon/releases/download/"
        r"launcher%40[^\n]+\n        sha256: [0-9a-f]{64}"
    )
    match = archive_pattern.search(manifest)
    if not match:
        raise RuntimeError("Could not find the launcher archive in the manifest")

    current_version = re.search(r"launcher%40([^/\n]+)", match.group(0)).group(1)
    if current_version == version:
        print(f"Horizon launcher {version} is already packaged")
        write_output("changed", "false")
        return

    digest = hashlib.sha256()
    with request(asset["browser_download_url"]) as response:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
    sha256 = digest.hexdigest()
    published_digest = asset.get("digest", "").removeprefix("sha256:")
    if published_digest and sha256 != published_digest:
        raise RuntimeError("Downloaded archive does not match GitHub's asset digest")

    archive = (
        "        url: https://github.com/horizon-rust/horizon/releases/download/"
        f"launcher%40{version}/{ARCHIVE_NAME}\n        sha256: {sha256}"
    )
    MANIFEST.write_text(
        archive_pattern.sub(lambda _: archive, manifest, count=1), encoding="utf-8"
    )

    metainfo = METAINFO.read_text(encoding="utf-8")
    release_date = release["published_at"][:10]
    entry = f'    <release version="{version}" date="{release_date}"/>\n'
    METAINFO.write_text(
        metainfo.replace("  <releases>\n", f"  <releases>\n{entry}", 1),
        encoding="utf-8",
    )

    print(f"Updated Horizon launcher from {current_version} to {version}")
    write_output("changed", "true")
    write_output("version", version)


if __name__ == "__main__":
    main()
