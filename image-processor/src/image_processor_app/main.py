from __future__ import annotations

import asyncio
import time
import cv2
import glob
import os
from PIL import Image
import edifice as ed
import components as com
import logging
from PySide6.QtGui import QImage

logger = logging.getLogger("Edifice")
logger.setLevel(logging.INFO)

@ed.component
def Main(self):
    source_folder, _source_folder_setter = ed.provide_context("source_folder_context_key", "")
    output_folder, _output_folder_setter = ed.provide_context("output_folder_context_key", "")
    reload_preview, reload_preview_setter = ed.use_state(False)

    current_hue, current_hue_setter = ed.provide_context("hue_context_key", 0)
    current_saturation, current_saturation_setter = ed.provide_context("saturation_context_key", 0)
    current_value, current_value_setter = ed.provide_context("value_context_key", 0)
    current_sharpness, current_sharpness_setter = ed.provide_context("sharpness_context_key", 0)

    selected_image_name, selected_image_setter = ed.provide_context("selected_image_context_key", "")
    selected_preview_name, selected_preview_name_setter = ed.use_state("")
    preview_image, preview_image_setter = ed.provide_context("preview_image_context_key", QImage())
    images, images_setter = ed.use_state([])
    image_names, image_names_setter = ed.use_state([])
    firstImage = 0
    progressBarValue, progressBarValue_setter = ed.use_state(0)
    progressBarFactor, progressBarFactor_setter = ed.use_state(1)
    
    
    async def loadImages():

        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', "*.webp"]
        aux_images = []
        aux_image_names = []
        progressBarValue_setter(0)

        if source_folder is not None and os.path.isdir(source_folder):
            progressBarFactor_setter(lambda _: len(os.listdir(source_folder)))
            print("Loading images from:", source_folder)
            print("Total files in source folder:", progressBarFactor)
            for extension in extensions:
                image_paths = glob.glob(os.path.join(source_folder, extension))
                for image_path in image_paths:
                    try:
                        img = Image.open(image_path)
                        if img is not None:
                            aux_images.append(img)
                            aux_image_names.append(image_path)
                            progressBarValue_setter(lambda old: old + 1)
                            await asyncio.sleep(0)
                            logger.info(f"Image loaded: {image_path}")
                    except Exception as e:
                        logger.error(f"Error loading image {image_path}: {e}")
            images_setter(aux_images)
            image_names_setter(aux_image_names)
            logger.info(f"{len(aux_image_names)} images loaded.")
            selected_image_setter(aux_image_names[firstImage])
            reload_preview_setter(not reload_preview)
        else:
            logger.warning("Source folder is not set or does not exist.")

    ed.use_async(loadImages, source_folder)

    async def loadPreviewImage():
        
        if source_folder == "" or not os.path.isdir(source_folder):
            logger.warning("Source folder is not set or does not exist.")
            return

        if output_folder == "" or not os.path.isdir(output_folder):
            logger.warning("Output folder is not set or does not exist.")
            return
        
        updatePreviewImage(firstImage)
        
    

    ed.use_async(loadPreviewImage,[source_folder, output_folder, reload_preview])

    
    def selectImage(direction):
    
        currentImageIndex = image_names.index(selected_image_name) if selected_image_name in image_names else -1
        logger.info(f"Current index: {currentImageIndex}, Direction: {direction}")
        currentImageIndex += direction

        if len(image_names) < 1:
            logger.info("No images available to select.")
            return

        if 0 <= currentImageIndex < len(image_names):           
            selected_image_setter(image_names[currentImageIndex])
            updatePreviewImage(currentImageIndex)
        elif image_names.index(selected_image_name) == 0 and direction == -1:
            selected_image_setter(image_names[len(image_names)-1]) #if we are at the first image and click previous, we select the last image
            updatePreviewImage(len(image_names)-1)
        elif image_names.index(selected_image_name) == len(image_names)-1 and direction == 1:
            selected_image_setter(image_names[0]) #if we are at the last image and click next, we select the first image
            updatePreviewImage(0)

        logger.info(f"Selected image: {selected_image_name}")
        
    
    def updatePreviewImage(index):
        try:
            preview_img = Image.open(image_names[index])
            if preview_img is not None:
                img_path = os.path.join(output_folder, "preview.png")
                preview_img.save(img_path)
                selected_preview_name_setter(img_path)
                preview_image_setter(QImage(img_path))
                logger.info(f"Preview image updated: {img_path}")
        except Exception as e:
            logger.error(f"Error loading preview image: {e}", exc_info=True)


    with ed.Window(title="Image Processor", _size_open=(800, 600)):
        with ed.VBoxView(style={"align": "top"}):
            with ed.HBoxView(style={"padding": 10}):
                com.ButtonWidget(label=source_folder, buttonLabel="Source Folder")
                com.ButtonWidget(label=output_folder, buttonLabel="Output Folder")
            with ed.HBoxView(style={"padding": 10}):
                with ed.VBoxView(style={"align": "top"}):   
                    com.ImageComponent(label="Original Image")
                    with ed.HBoxView(style={"align": "center"}):
                        ed.Button("Previous",on_click=lambda _: selectImage(-1))
                        ed.Button("Next", on_click= lambda _: selectImage(1))
                com.ImageComponent(label="Preview Image")
            with ed.HBoxView(style={"align": "center"}):
                ed.Button("Apply", on_click= lambda _: print("Clicked!"),style={"margin-left": "100px", "margin-right": "200px"})
                com.EditorWidget()
            with ed.HBoxView(style={"align": "center", "padding": 50}):
                ed.ProgressBar(
                        value=int((progressBarValue / progressBarFactor) *100),
                        min_value=0,
                        max_value=100,
                        format="",
                        style={"width": "600%"}
                    )

   

if __name__ == "__main__":
    ed.App(Main()).start()