# Image Processor

A desktop GUI for batch image processing. Apply HSV adjustments and blur/sharpen effects to an entire folder of images, with a live side-by-side preview and a parallelized save pipeline that keeps the UI responsive on large batches.

Built with:

- **[pyedifice](https://pyedifice.github.io/)** — React-style declarative framework over PySide6 / Qt
- **[Pillow](https://python-pillow.org/)** + **NumPy** — image processing
- **`multiprocessing`** — parallel apply across spawned worker processes

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package and environment manager
- Python 3.14

uv will handle the Python installation and virtual environment automatically.

### Installing uv

**Windows:**
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS and Linux:**
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

From the `image-processor` directory, install all dependencies:

```
uv sync
```

## Running the app

```
uv run image-processor
```

## Running the tests

```
uv run pytest
```

## Usage

1. Click **Source Folder** to select a folder containing your images via a file dialog. The app will warn you if the selected folder contains no supported images.
2. Click **Output Folder** to select a destination folder for the processed images via a file dialog.
3. Use **◀ Previous Image** / **Next Image ▶** to browse the source images
4. Adjust the effect sliders — the preview panel updates live as you move them
5. Click **Apply** to process and save all images in the source folder with the current settings
6. A progress bar is displayed while processing is in progress

## Features

### Folder-based batch processing
Select a source folder containing images and an output folder for the results via native file dialogs. All images in the source folder are processed in one operation with the current effect settings. The app validates the source folder selection and warns if it contains no supported images.

### Supported formats
JPEG (`.jpg`, `.jpeg`), PNG, BMP, TIFF (`.tif`, `.tiff`), WebP.

### Side-by-side original and preview
The main view displays the original image and the effect-adjusted preview simultaneously side by side. The preview updates in real time as you move the sliders. This design choice allows direct visual comparison without any interaction, which is more practical when tuning multiple sliders.

### HSV colour adjustments
- **Hue** — rotates the colour hue by 0–360 degrees. Values of 0 and 360 leave the image unchanged.
- **Saturation** — scales colour saturation. 100 is neutral; 0 removes all colour; 200 doubles it.
- **Value** — scales brightness. 100 is neutral; 0 makes the image black; 200 doubles brightness.

### Sharpness and blur
A single slider controls both effects. 100 is neutral; values below 100 apply an unsharp mask (sharpening); values above 100 apply a Gaussian blur.

### Reset
The Reset button in the editor panel returns all sliders to their default values.

### Parallel batch processing
When Apply is clicked, the workload is distributed across 4 parallel worker processes so large folders are processed efficiently without blocking the UI.

### Special character filename support
Image filenames containing apostrophes, accented characters, unicode, emoji, and other special characters are handled correctly.

## Architecture

```
image-processor/
├── src/
│   └── image_processor_app/
│       ├── main.py           # App entry point and business logic
│       ├── components.py     # Reusable UI components
│       └── constants.py      # Shared constants (extensions, warning messages)
├── tests/
│   ├── test_edit_image.py    # Unit tests for image editing logic
│   └── test_scan_images.py   # Unit tests for image scanning logic
├── pyproject.toml
└── uv.lock
```

### `main.py`

Contains all business logic and the root `Main` UI component:

- **`scanImages(folder)`** — generator that walks a directory and yields paths to valid image files one at a time, skipping unreadable files without halting the scan. Yielding one path at a time allows `loadImages` to update the progress bar and yield to the Qt event loop between each file, keeping the UI responsive during large folder loads.
- **`editImage(path, hue, saturation, value, sharpness)`** — applies HSV adjustments and sharpness/blur to a single image and returns the result as a PIL Image.
- **`subProcess(queue, callback)`** — worker function executed in a separate process. Reads a `WorkItem` from a queue, processes its assigned images, saves each result with `_edited` appended to the stem (e.g. `photo.jpg` → `photo_edited.jpg`), incrementing a counter suffix if the name already exists (`photo_edited1.jpg`, `photo_edited2.jpg`, …), and calls back with progress updates.
- **`Main`** — the root edifice component. Manages application state (selected folders, current image, slider values, progress) and orchestrates loading, previewing, and batch processing.

### `components.py`

Reusable UI components built with [pyedifice](https://pyedifice.github.io/):

- **`OnboardingWidget`** — welcome screen shown until both folders are selected, with dynamic checkmarks as each step is completed.
- **`ImageComponent`** — displays either the original or the live-edited preview image.
- **`EditorWidget`** — contains the four effect sliders and the Reset button.
- **`SliderWidget`** — a labelled slider with a validated text input that stays in sync. Reads and writes shared context so all sliders communicate with the parent component without prop drilling.
- **`ButtonWidget`** — folder picker button backed by a native `QFileDialog`.

