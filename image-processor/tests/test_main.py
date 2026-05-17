import unittest
import tempfile
import os
import shutil
from PIL import Image
import numpy as np
from image_processor_app.main import scanImages


class TestScanImages(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _save_image(self, filename):
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        arr[:, :] = [255, 0, 0]
        filepath = os.path.join(self.test_dir, filename)
        Image.fromarray(arr).save(filepath)
        return filepath

    # --- return type ---

    def test_returns_generator(self):
        import types
        result = scanImages(self.test_dir)
        self.assertIsInstance(result, types.GeneratorType)

    # --- empty / missing folder ---

    def test_empty_folder_yields_nothing(self):
        found = list(scanImages(self.test_dir))
        self.assertEqual(found, [])

    def test_nonexistent_folder_yields_nothing(self):
        found = list(scanImages(os.path.join(self.test_dir, "does_not_exist")))
        self.assertEqual(found, [])

    def test_empty_string_yields_nothing(self):
        found = list(scanImages(""))
        self.assertEqual(found, [])

    # --- supported extensions ---

    def test_all_supported_extensions_are_found(self):
        filenames = [
            "image.jpg",
            "image.jpeg",
            "image.png",
            "image.bmp",
            "image.tiff",
            "image.tif",
            "image.webp",
        ]
        expected = [self._save_image(f) for f in filenames]
        found = list(scanImages(self.test_dir))
        self.assertCountEqual(found, expected)

    def test_unsupported_extensions_are_not_found(self):
        unsupported = ["document.txt", "archive.zip", "animation.gif", "data.pdf"]
        for filename in unsupported:
            open(os.path.join(self.test_dir, filename), "w").close()
        found = list(scanImages(self.test_dir))
        self.assertEqual(found, [])

    # --- corrupted files ---

    def test_corrupted_file_is_skipped(self):
        valid_path = self._save_image("valid.jpg")
        corrupted_path = os.path.join(self.test_dir, "corrupted.jpg")
        with open(corrupted_path, "w") as f:
            f.write("this is not an image")
        found = list(scanImages(self.test_dir))
        self.assertIn(valid_path, found)
        self.assertNotIn(corrupted_path, found)

    def test_corrupted_file_does_not_stop_scan(self):
        corrupted_path = os.path.join(self.test_dir, "corrupted.jpg")
        with open(corrupted_path, "w") as f:
            f.write("this is not an image")
        valid_path = self._save_image("valid.png")
        found = list(scanImages(self.test_dir))
        self.assertIn(valid_path, found)

    # --- special character filenames ---

    def test_special_character_filenames_are_found(self):
        filenames = [
            "Assassin's Creed.jpg",           # Apostrophe
            "Assassin's Creed.png",           # Apostrophe with different extension
            "Café Müller.png",                # Accented characters
            "Test & Game.jpg",                # Ampersand
            "File (2023).png",                # Parentheses
            "Game-Title_v2.jpg",              # Hyphen and underscore
            "Spël Ñame.png",                  # More accented chars
            "测试图片.jpg",                    # Chinese characters
            "тест.png",                       # Cyrillic
            "🎮 Game.jpg",                    # Emoji
            "normal_file.jpg",                # Normal filename for comparison
        ]
        expected = []
        for filename in filenames:
            try:
                path = self._save_image(filename)
                if os.path.exists(path):
                    expected.append(path)
            except Exception:
                pass

        found = list(scanImages(self.test_dir))

        for path in found:
            self.assertIn(path, expected)

        for path in expected:
            self.assertIn(path, found)
