# KHADRA68 Open Tools — Video Contact Sheet

A small, open-source utility extracted and independently packaged from the **general-purpose video review tooling** used while developing KHADRA68. It creates a contact sheet: selected video frames stacked as rows, with multiple videos side by side for visual comparison.

**Scope:** video preview and visual debugging only. This repository contains **no object tracker, identity model, lock-on algorithm, trained weights, private videos, internal evaluations, or original Git history**. The primary KHADRA68 project remains private.

## Requirements

- Python 3.10+
- `opencv-python-headless` and `numpy`

Install:

```bash
python -m pip install -r requirements.txt
```

## Use

Choose four evenly spaced frames from one video:

```bash
python contact_sheet.py --videos example.mp4 --n 4 --width 480 --out review.png
```

Compare the same frame indices of two videos:

```bash
python contact_sheet.py --videos original.mp4 processed.mp4 --frames 10 30 50 --width 480 --out comparison.png
```

The output image displays one row per selected frame and one column per input video. Inputs are ordinary local videos, **not included** in the repository. Frame numbering starts at zero. If any requested frame cannot be decoded, the command fails rather than silently omitting it.

## Tests

Tests create short **synthetic videos**, so no footage or model files need downloading.

```bash
python -m unittest discover -s tests -v
```

## Contributing

Bug reports and focused pull requests for the video contact sheet are welcome. Please do not upload third-party footage without permission or disclose private KHADRA68 data in public issues.

## License

MIT — see [LICENSE](LICENSE). This license applies **only to files in this public repository**, not to the separate private KHADRA68 codebase.
