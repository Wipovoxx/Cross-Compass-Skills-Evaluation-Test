from enum import Enum

IMAGE_EXTENSIONS = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', '*.webp']

SOURCE_EMPTY_WARNING = "⚠ No supported images found in the selected folder"

DEFAUT_HUE = 0
DEFAULT_SATURATION = 100
DEFAULT_VALUE = 100
DEFAULT_SHARPNESS = 100

class DisplayMode(Enum):
     BOTH = 0
     ORIGINAL = 1
     PREVIEW = 2
