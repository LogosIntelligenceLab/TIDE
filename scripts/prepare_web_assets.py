"""Prepare the static page from the adjacent TIDE manuscript and extracted videos.

Requires pymupdf, Pillow and ffmpeg (or imageio-ffmpeg).
Writes only to this project's docs/ directory; manuscript assets stay intact.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from PIL import Image
import pymupdf


ROOT = Path(__file__).resolve().parents[1]
FIGURES = {
    "teaser": "ppts/teaser_enhanced.pdf",
    "pipeline": "images/pipeline.pdf",
    "setup": "images/setup.pdf",
    "tasks": "images/tasks.pdf",
    "results": "images/online_post_training_autonomy.pdf",
    "deployment-diagnostics": "images/deployment_diagnostics.pdf",
    "action-space": "images/action_space.pdf",
}
VIDEOS = {
    "bit-insertion-warm-start": "insert_drill_baseline.mp4",
    "bit-insertion-tide": "insert_drill_ours.mp4",
    "towel-folding-warm-start": "fold_towel_baseline.mp4",
    "towel-folding-tide": "fold_towel_ours.mp4",
    "towel-hanging-warm-start": "hang_towel_baseline.mp4",
    "towel-hanging-tide": "hang_towel_ours.mp4",
    "chain-packing-warm-start": "close_box_baseline.mp4",
    "chain-packing-tide": "close_box_ours.mp4",
}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def duration(ffmpeg, path):
    info = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(path)],
        capture_output=True, text=True, check=False,
    ).stderr
    match = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    if not match:
        raise ValueError(f"Cannot read video duration: {path}")
    hours, minutes, seconds = map(float, match.groups())
    return hours * 3600 + minutes * 60 + seconds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT.parent / "ICRA2027_TIDE")
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    parser.add_argument("--skip-videos", action="store_true")
    args = parser.parse_args()
    source = args.source.resolve()
    docs = ROOT / "docs"
    images = docs / "static/images"
    videos = docs / "static/videos"
    images.mkdir(parents=True, exist_ok=True)
    videos.mkdir(parents=True, exist_ok=True)
    manifest = {"figures": [], "videos": []}
    for name, relative in FIGURES.items():
        path = source / relative
        with pymupdf.open(path) as document:
            page = document[0]
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2400 / page.rect.width, 2400 / page.rect.width),
                alpha=False,
            )
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            temporary = images / f"{name}.tmp.png"
            image.save(temporary, optimize=True)
            temporary.replace(images / f"{name}.png")
        manifest["figures"].append({
            "file": f"{name}.png", "source": relative, "source_sha256": digest(path),
        })
        print(f"Figure: {name}", flush=True)
    if args.skip_videos:
        existing = videos / "manifest.json"
        if existing.exists():
            manifest["videos"] = json.loads(existing.read_text())["videos"]
    else:
        ffmpeg = args.ffmpeg
        if not ffmpeg:
            import imageio_ffmpeg
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        for name, original in VIDEOS.items():
            path = source / "ppts/materials/processed_videos" / original
            if path.stat().st_size < 1000:
                raise ValueError(f"Download the Git LFS object first: {path}")
            target = videos / f"{name}.mp4"
            subprocess.run([
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(path), "-map", "0:v:0",
                "-vf", "scale=1280:720:force_original_aspect_ratio=decrease:force_divisible_by=2,setsar=1",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-pix_fmt", "yuv420p", "-threads", "2", "-an",
                "-movflags", "+faststart", str(target),
            ], check=True)
            subprocess.run([
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-ss", "1", "-i", str(target), "-frames:v", "1",
                "-q:v", "2", str(target.with_suffix(".jpg")),
            ], check=True)
            source_duration = duration(ffmpeg, path)
            web_duration = duration(ffmpeg, target)
            if abs(web_duration - source_duration) > 0.1:
                raise ValueError(f"Video timing changed: {name}")
            manifest["videos"].append({
                "file": target.name, "source": original,
                "source_sha256": digest(path), "source_bytes": path.stat().st_size,
                "web_sha256": digest(target), "web_bytes": target.stat().st_size,
                "duration_seconds": web_duration,
            })
            print(f"Video: {name} ({web_duration:.2f}s)", flush=True)
    (videos / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
