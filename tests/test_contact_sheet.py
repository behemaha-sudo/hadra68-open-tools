"""Tests use only synthetic frames; no private footage or project assets."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import cv2
import numpy as np

from contact_sheet import evenly_spaced_frames, make_contact_sheet, main, render_tile


class ContactSheetTests(unittest.TestCase):
    def test_evenly_spaced_indices_are_unique(self):
        self.assertEqual(evenly_spaced_frames(2, 8), [0, 1])
        self.assertEqual(len(evenly_spaced_frames(120, 6)), 6)
        self.assertEqual(len(set(evenly_spaced_frames(120, 6))), 6)

    def test_invalid_frame_counts(self):
        for count, n in [(0, 4), (4, 0), (-1, 2)]:
            with self.assertRaises(ValueError):
                evenly_spaced_frames(count, n)

    def test_tile_width_and_label(self):
        frame = np.full((50, 100, 3), 100, dtype=np.uint8)
        tile = render_tile(frame, 200, 3)
        self.assertEqual(tile.shape, (100, 200, 3))
        self.assertFalse(np.array_equal(tile[10, 10], np.array([100, 100, 100])))

    def test_bad_input(self):
        with self.assertRaisesRegex(ValueError, "At least one video"):
            make_contact_sheet([], [0], 120)
        with self.assertRaisesRegex(ValueError, "At least one frame"):
            make_contact_sheet(["example.avi"], [], 120)
        with self.assertRaisesRegex(ValueError, "negative"):
            make_contact_sheet(["example.avi"], [-1], 120)
        with self.assertRaisesRegex(ValueError, "Cannot open"):
            make_contact_sheet(["does_not_exist.avi"], [0], 120)

    def test_synthetic_avi_end_to_end(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp)
            videos = []
            for j, (w, h) in enumerate([(80, 60), (80, 40)]):
                path = p / f"synthetic_{j}.avi"
                writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10, (w, h))
                if not writer.isOpened():
                    self.skipTest("MJPG AVI encoder unavailable on this system")
                for i in range(6):
                    frame = np.full((h, w, 3), (20 + i * 5, 30 + j * 10, 40), dtype=np.uint8)
                    writer.write(frame)
                writer.release()
                videos.append(str(path))
            sheet = make_contact_sheet(videos, [1, 4], 120)
            self.assertEqual(sheet.shape, (180, 240, 3))
            out = p / "results" / "sheet.png"
            self.assertEqual(main(["--videos", *videos, "--frames", "1", "4", "--width", "120", "--out", str(out)]), 0)
            self.assertTrue(out.is_file())
            self.assertEqual(cv2.imread(str(out)).shape, sheet.shape)


if __name__ == "__main__":
    unittest.main()
