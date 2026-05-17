import unittest
import tempfile
import os
import shutil
import numpy as np
from PIL import Image
from image_processor_app.main import editImage


class TestEditImage(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _save_image(self, array, filename="test.png"):
        path = os.path.join(self.test_dir, filename)
        Image.fromarray(array.astype(np.uint8), "RGB").save(path)
        return path

    def _solid(self, color, size=(50, 50)):
        return np.full((*size, 3), color, dtype=np.uint8)

    def _hsv_array(self, img):
        return np.array(img.convert("HSV"))

    # --- output type and shape ---

    def test_returns_pil_image(self):
        path = self._save_image(self._solid([255, 0, 0]))
        result = editImage(path, 0, 100, 100, 100)
        self.assertIsInstance(result, Image.Image)

    def test_output_mode_is_rgb(self):
        path = self._save_image(self._solid([255, 0, 0]))
        result = editImage(path, 0, 100, 100, 100)
        self.assertEqual(result.mode, "RGB")

    def test_output_size_matches_input(self):
        path = self._save_image(self._solid([255, 0, 0], size=(80, 120)))
        input_size = Image.open(path).size
        result = editImage(path, 45, 150, 80, 50)
        self.assertEqual(result.size, input_size)

    # --- identity ---

    def test_default_params_do_not_change_image(self):
        # hue=0, sat=100, val=100, sharpness=100 are all no-ops
        path = self._save_image(self._solid([255, 0, 0]))
        original = np.array(Image.open(path))
        result = np.array(editImage(path, 0, 100, 100, 100))
        np.testing.assert_array_equal(original, result)

    # --- hue ---

    def test_hue_zero_is_not_applied(self):
        # 0 < 0 < 360 is False, so hue=0 must leave H channel unchanged
        path = self._save_image(self._solid([255, 0, 0]))
        original_h = self._hsv_array(Image.open(path))[:, :, 0]
        result_h = self._hsv_array(editImage(path, 0, 100, 100, 100))[:, :, 0]
        np.testing.assert_array_equal(original_h, result_h)

    def test_hue_360_is_not_applied(self):
        # 0 < 360 < 360 is False, so hue=360 must leave H channel unchanged
        path = self._save_image(self._solid([255, 0, 0]))
        original_h = self._hsv_array(Image.open(path))[:, :, 0]
        result_h = self._hsv_array(editImage(path, 360, 100, 100, 100))[:, :, 0]
        np.testing.assert_array_equal(original_h, result_h)

    def test_hue_shift_rotates_h_channel(self):
        # Red has H=0; a 180-degree shift should produce H≈127 (180*255/360)
        path = self._save_image(self._solid([255, 0, 0]))
        original_h = self._hsv_array(Image.open(path))[:, :, 0].astype(np.int16)
        result_h = self._hsv_array(editImage(path, 180, 100, 100, 100))[:, :, 0].astype(np.int16)
        expected_shift = int(180 * 255 / 360)
        actual_shift = (result_h - original_h) % 256
        np.testing.assert_allclose(actual_shift, expected_shift, atol=1)

    # --- saturation ---

    def test_saturation_100_does_not_change_s_channel(self):
        path = self._save_image(self._solid([255, 0, 0]))
        original_s = self._hsv_array(Image.open(path))[:, :, 1]
        result_s = self._hsv_array(editImage(path, 0, 100, 100, 100))[:, :, 1]
        np.testing.assert_array_equal(original_s, result_s)

    def test_saturation_zero_removes_color(self):
        path = self._save_image(self._solid([255, 0, 0]))
        result_s = self._hsv_array(editImage(path, 0, 0, 100, 100))[:, :, 1]
        np.testing.assert_array_equal(result_s, 0)

    # --- value ---

    def test_value_100_does_not_change_v_channel(self):
        path = self._save_image(self._solid([255, 0, 0]))
        original_v = self._hsv_array(Image.open(path))[:, :, 2]
        result_v = self._hsv_array(editImage(path, 0, 100, 100, 100))[:, :, 2]
        np.testing.assert_array_equal(original_v, result_v)

    def test_value_zero_produces_black_image(self):
        path = self._save_image(self._solid([255, 0, 0]))
        result = np.array(editImage(path, 0, 100, 0, 100))
        np.testing.assert_array_equal(result, 0)

    # --- sharpness / blur ---

    def test_sharpness_100_does_not_change_image(self):
        path = self._save_image(self._solid([255, 0, 0]))
        original = np.array(Image.open(path))
        result = np.array(editImage(path, 0, 100, 100, 100))
        np.testing.assert_array_equal(original, result)

    def test_sharpness_above_100_blurs_image(self):
        # Use a checkerboard so there are edges for the blur to soften
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        arr[::2, ::2] = [255, 255, 255]
        path = self._save_image(arr)
        original = np.array(Image.open(path))
        result = np.array(editImage(path, 0, 100, 100, 200))
        self.assertFalse(np.array_equal(original, result))

    def test_sharpness_below_100_sharpens_image(self):
        # A sharp step edge creates a large |original - blurred| difference near
        # the boundary, which exceeds UnsharpMask's threshold and triggers the filter.
        # A smooth gradient or extreme 0/255 values both fail: the gradient stays
        # below the threshold, and 0/255 clip back to the same values.
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        arr[:50] = [80, 80, 80]
        arr[50:] = [180, 180, 180]
        path = self._save_image(arr)
        original = np.array(Image.open(path))
        result = np.array(editImage(path, 0, 100, 100, 0))
        self.assertFalse(np.array_equal(original, result))


if __name__ == "__main__":
    unittest.main()
