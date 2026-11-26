#!/usr/bin/env python3
"""Create a side-by-side contact sheet from ordinary local video files.

A self-contained, general-purpose utility; no tracking or detection engine.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np


def evenly_spaced_frames(frame_count: int, n: int) -> list[int]:
    """Choose up to *n* unique representative frame indices from one video."""
    if frame_count <= 0:
        raise ValueError("Video frame count must be positive")
    if n <= 0:
        raise ValueError("--n must be positive")
    count = min(n, frame_count)
    return [min(frame_count - 1, int((i + 0.5) * frame_count / count)) for i in range(count)]


def read_video_frame(video_path: str, index: int) -> np.ndarray:
    if index < 0:
        raise ValueError("Frame indices cannot be negative")
    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        capture.set(cv2.CAP_PROP_POS_FRAMES, float(index))
        ok, frame = capture.read()
        if not ok or frame is None:
            raise ValueError(f"Could not read frame {index} from {video_path}")
        return frame
    finally:
        capture.release()


def number_of_frames(video_path: str) -> int:
    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        return int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    finally:
        capture.release()


def render_tile(frame: np.ndarray, width: int, frame_index: int) -> np.ndarray:
    if width < 32:
        raise ValueError("Tile width must be at least 32 pixels")
    height, image_width = frame.shape[:2]
    if height <= 0 or image_width <= 0:
        raise ValueError("Frame must have positive width and height")
    tile_height = max(1, round(height * width / image_width))
    tile = cv2.resize(frame, (width, tile_height), interpolation=cv2.INTER_AREA)
    label = f"Frame {frame_index}"
    label_width = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0][0]
    cv2.rectangle(tile, (0, 0), (min(width - 1, label_width + 12), min(tile_height - 1, 26)), (0, 0, 0), -1)
    cv2.putText(tile, label, (6, min(tile_height - 5, 18)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
    return tile


def make_contact_sheet(videos: Sequence[str], frames: Sequence[int], width: int) -> np.ndarray:
    if not videos:
        raise ValueError("At least one video is required")
    if not frames:
        raise ValueError("At least one frame index is required")
    if any(i < 0 for i in frames):
        raise ValueError("Frame indices cannot be negative")
    rows = []
    for index in frames:
        tiles = [render_tile(read_video_frame(video, index), width, index) for video in videos]
        row_height = max(tile.shape[0] for tile in tiles)
        padded = [cv2.copyMakeBorder(tile, 0, row_height - tile.shape[0], 0, 0,
                                     cv2.BORDER_CONSTANT, value=(0, 0, 0)) for tile in tiles]
        rows.append(np.hstack(padded))
    return np.vstack(rows)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--videos", nargs="+", required=True, help="One or more video filenames")
    parser.add_argument("--frames", nargs="*", type=int, help="Explicit zero-based frame indices")
    parser.add_argument("--n", type=int, default=4, help="Frames to sample when --frames is omitted")
    parser.add_argument("--width", type=int, default=480, help="Width of each video tile in pixels")
    parser.add_argument("--out", required=True, help="Output image (.png, .jpg or .jpeg)")
    args = parser.parse_args(argv)
    try:
        if args.width < 32:
            raise ValueError("--width must be at least 32")
        if args.n < 1:
            raise ValueError("--n must be at least 1")
        output = Path(args.out)
        if output.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            raise ValueError("--out must end in .png, .jpg or .jpeg")
        frames = list(args.frames) if args.frames else evenly_spaced_frames(number_of_frames(args.videos[0]), args.n)
        result = make_contact_sheet(args.videos, frames, args.width)
        output.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(output), result):
            raise ValueError(f"Unable to write output image: {output}")
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Wrote {output} ({len(frames)} rows, {len(args.videos)} video(s)); frames={frames}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
