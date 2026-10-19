# TIDE project page

Static project page for **Training in Deployment: Human-in-the-Loop Online Post-Training for Robot Manipulation**, featuring a video hero, paper figures, evaluation results, and a real-robot comparison gallery.

## Preview

From this directory:

```bash
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000`. For a remote machine, forward port 8000 to your computer. The page requires no application server or JavaScript build step. The `docs/` directory is the complete static site, ready for a static host such as GitHub Pages.

## Regenerate assets

The default figure and video source is the adjacent `../ICRA2027_TIDE` directory.

Install the optional asset-generation dependencies in a virtual environment:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/prepare_web_assets.py
```

Use `--source /absolute/path/to/manuscript` for another source tree, `--ffmpeg /path/to/ffmpeg` for a specific encoder, or `--skip-videos` to refresh figures without re-encoding the eight clips.

The script reads canonical manuscript PDFs and the eight extracted robot clips. It creates 2400-pixel-wide figure images, 720p H.264 video copies with fast-start metadata, JPEG posters, an asset provenance manifest. Video durations and the supplied playback timing are preserved, and originals are untouched. The raw clips are Git LFS assets in the manuscript repository; download those first if they are still pointer files.

## Content

- Authors, homepage links, and affiliation numbers are in `docs/index.html`. They match the manuscript title block in `../ICRA2027_TIDE/root.tex`.
- Author order: Chun Gu, Xiaofei Wei, Yiming Chen, Bozhou Zhang, Juntong Zhang, Li Zhang.
- Results use the current manuscript figures, including Batch and binary full-task completion. The completion table is transcribed from `ppts/online_post_training_autonomy.json`; the provenance ablation uses 80%, 65%, and 67.5%.
- Warm-start and TIDE recordings have independent controls; they are qualitative examples, not paired quantitative trials. Their existing playback speed is not asserted to be real time.
- The author section provides an arXiv button, disabled until its URL is available, and a BibTeX button linking to the citation section. The citation uses the arXiv preprint format with only `title`, `author`, `journal`, and `year`. The website repository does not contain a manuscript PDF.
- `docs/static/videos/manifest.json` records source hashes, web-copy hashes, sizes and durations. Keep manuscript changes synchronized with the text, table and image exports.

## Design attribution

Design provenance and license information are recorded in `NOTICE`. Paper figures and robot recordings are separate research assets; the design license does not change their distribution terms.

## Citation

```bibtex
@article{gu2026tide,
  title         = {Training in Deployment: Human-in-the-Loop Online Post-Training for Robot Manipulation},
  author        = {Gu, Chun and Wei, Xiaofei and Chen, Yiming and Zhang, Bozhou and Zhang, Juntong and Zhang, Li},
  journal       = {arXiv preprint},
  year          = {2026}
}
```
