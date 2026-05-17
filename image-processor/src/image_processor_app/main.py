from __future__ import annotations

import asyncio
from typing import Callable
import glob
import os
from PIL import Image
from PIL import ImageFilter
import numpy as np
import edifice as ed
import components as com
import logging
from PySide6.QtGui import QImage
from dataclasses import dataclass
import multiprocessing
from multiprocessing import Queue
import functools
import math


logger = logging.getLogger("Edifice")
logger.setLevel(logging.INFO)

@dataclass
class WorkItem:
    images: list[str]
    folder: str
    hue: int
    saturation: int
    value: int
    sharpness: int



def subProcess( msg_queue: Queue[WorkItem],
    callback: Callable[[int], None],
) -> str:
    WorkItem = msg_queue.get()
    images = WorkItem.images
    output_folder = WorkItem.folder
    hue = WorkItem.hue
    saturation = WorkItem.saturation
    value = WorkItem.value
    sharpness = WorkItem.sharpness
    logger.info(f"Process: {multiprocessing.current_process().pid} is processing: {len(images)} images")
    for image in images:
        try:
            result = editImage(image, hue, saturation, value, sharpness)
            output_path = os.path.join(output_folder, os.path.basename(image))
            result.save(output_path)
            callback(1)
        except Exception as e:
            logger.error(f"Error processing image {image}: {e}", exc_info=True)
    
    return f"Process: {multiprocessing.current_process().pid} processed: {len(images)} images"


def editImage(image: str, hue: int, saturation: int, value: int, sharpness: int) -> Image.Image:

    img = Image.open(image)
    hsv_img = img.convert('HSV')

    # Convert to numpy array
    hsv_array = np.array(hsv_img)

    # Modify H, S, V
    h, s, v = hsv_array[:,:,0], hsv_array[:,:,1], hsv_array[:,:,2]

    # Modify Hue
    if 0 < hue < 360:
        h = (h.astype(np.int16) + int(hue * 255 / 360)) % 256
        h = h.astype(np.uint8)

    # Modify Saturation
    if saturation != 100:
        saturation_factor = float(saturation / 100.0)
        s = np.clip(s * saturation_factor, 0, 255).astype(np.uint8)

    # Modify Value
    if value != 100:
        value_factor = float(value / 100.0)
        v = np.clip(v * value_factor, 0, 255).astype(np.uint8)

    # Reconstruct the image
    modified_hsv = np.stack([h, s, v], axis=2)
    modified_hsv_img = Image.fromarray(modified_hsv, 'HSV')

    # Convert back to RGB
    result = modified_hsv_img.convert('RGB')

    # Modify Sharpness/Blur
    if sharpness > 100:
        result = result.filter(ImageFilter.GaussianBlur(radius=(sharpness - 100) / 20))
    elif sharpness < 100:
        result = result.filter(ImageFilter.UnsharpMask(percent=150 -sharpness))

    return result

@ed.component
def Main(self):
    source_folder, _source_folder_setter = ed.provide_context("source_folder_context_key", "")
    output_folder, _output_folder_setter = ed.provide_context("output_folder_context_key", "")
    reload_preview, reload_preview_setter = ed.use_state(False)

    current_hue, current_hue_setter = ed.provide_context("hue_context_key", 0)
    current_saturation, current_saturation_setter = ed.provide_context("saturation_context_key", 100)
    current_value, current_value_setter = ed.provide_context("value_context_key", 100)
    current_sharpness, current_sharpness_setter = ed.provide_context("sharpness_context_key", 0)

    selected_image_name, selected_image_setter = ed.provide_context("selected_image_context_key", "")
    selected_preview_name, selected_preview_name_setter = ed.use_state("")
    preview_image, preview_image_setter = ed.provide_context("preview_image_context_key", QImage())
    image_names, image_names_setter = ed.use_state([])
    firstImage = 0
    progressBarValue, progressBarValue_setter = ed.use_state(0)
    progressBarFactor, progressBarFactor_setter = ed.use_state(1)

    start, start_setter = ed.use_state(False)
    execute, execute_setter = ed.use_state(False)
    showProgressBar, showProgressBar_setter= ed.use_state(False)
    
    
    async def loadImages():

        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', "*.webp"]
        aux_image_names = []
        progressBarValue_setter(0)
        
        if source_folder is not None and os.path.isdir(source_folder):
            showProgressBar_setter(True)
            progressBarFactor_setter(lambda _: len(os.listdir(source_folder)))
            print("Loading images from:", source_folder)
            print("Total files in source folder:", progressBarFactor)
            for extension in extensions:
                image_paths = glob.glob(os.path.join(source_folder, extension))
                for image_path in image_paths:
                    try:
                        img = Image.open(image_path)
                        if img is not None:
                            aux_image_names.append(image_path)
                            progressBarValue_setter(lambda old: old + 1)
                            await asyncio.sleep(0)
                            logger.info(f"Image loaded: {image_path}")
                    except Exception as e:
                        logger.error(f"Error loading image {image_path}: {e}")
            
            image_names_setter(aux_image_names)
            logger.info(f"{len(aux_image_names)} images loaded.")
            selected_image_setter(aux_image_names[firstImage])
            reload_preview_setter(not reload_preview)
            showProgressBar_setter(False)
        else:
            logger.warning("loadImages(): Source folder is not set or does not exist.")

    ed.use_async(loadImages, source_folder)

    async def loadPreviewImage():
        
        if source_folder == "" or not os.path.isdir(source_folder):
            logger.warning("loadPreviewImage(): Source folder is not set or does not exist.")
            return

        if output_folder == "" or not os.path.isdir(output_folder):
            logger.warning("loadPreviewImage(): Output folder is not set or does not exist.")
            return
        
        updatePreviewImage(firstImage)
        
    

    ed.use_async(loadPreviewImage,[source_folder, output_folder, reload_preview])

    
    def selectImage(direction):
    
        currentImageIndex = image_names.index(selected_image_name) if selected_image_name in image_names else -1
        logger.info(f"Current index: {currentImageIndex}, Direction: {direction}")
        currentImageIndex += direction

        if len(image_names) < 1:
            logger.info("selectImage(): No images available to select.")
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

        logger.info(f"selectImage(): Selected image: {selected_image_name}")
        
    def updatePreviewImage(index):

        if output_folder == "":
            logger.warning("updatePreviewImage(): Output folder is not set or does not exist.")
            return

        try:
            preview_img = Image.open(image_names[index])
            if preview_img is not None:
                img_path = os.path.join(output_folder, "preview.png")
                preview_img.save(img_path)
                selected_preview_name_setter(img_path)
                preview_image_setter(QImage(img_path))
                logger.info(f"updatePreviewImage(): Preview image updated: {img_path}")
        except Exception as e:
            logger.error(f"updatePreviewImage: Error loading preview image: {e}", exc_info=True)


    async def editPreview():
        if selected_preview_name == "":
            logger.warning("editPreview(): No preview image selected.")
            return
        await asyncio.sleep(0.1)
        try:
            edittedPreview = editImage(selected_preview_name, current_hue, current_saturation, current_value, current_sharpness)
        except Exception as e:
            logger.error(f"Error editing preview image: {e}", exc_info=True)
            return

        result_path = os.path.join(output_folder, "edited_preview.png")
        edittedPreview.save(result_path)
        preview_image_setter(QImage(result_path))
        logger.info(f"editPreview(): Preview image edited and saved: {result_path}")

    ed.use_async(editPreview, [selected_preview_name, current_hue, current_saturation, current_value, current_sharpness])

    def on_start_click():
        progressBarValue_setter(0)
        start_setter(not start)
        if not execute:
            execute_setter(not execute)

    async def send_data(queues: list[multiprocessing.Queue[WorkItem]], images: list[list[str]]):
        for i, assigned_images in enumerate(images):
            queues[i].put(WorkItem(images=assigned_images,
                                   folder=output_folder,
                                   hue=current_hue, 
                                   saturation=current_saturation, 
                                   value=current_value, 
                                   sharpness=current_sharpness))

    async def runSubprocess():
        
        if execute:
            progressBarValue_setter(0)
            showProgressBar_setter(True)
            context = multiprocessing.get_context("spawn")
            num_workers = 4

            queues = [context.Queue() for _ in range(num_workers)]

            task_size = int(len(image_names) / num_workers)

            worker_images = [
                image_names[i * task_size : (i + 1) * task_size]
                for i in range(0, num_workers)
            ]

            if len(image_names) % num_workers != 0: #if we cant perfectly divide the workload, we assign the reminder to the last worker           
                worker_images[num_workers - 1] = image_names[ (num_workers - 1) * task_size : len(image_names)]


            workers = [
                ed.run_subprocess_with_callback(
                    functools.partial(subProcess, queue),
                    updateProgressBarValue,
                )
                for queue in queues
            ]
            results = await asyncio.gather(
                *workers,
                send_data(queues, worker_images),
            )
            worker_results = results[:-1]
            logger.info("runSubprocess(): All workers finished.")
            logger.info(f"runSubprocess(): processed: {len(image_names)}")
            showProgressBar_setter(False)
            execute_setter(not execute)
        
    ed.use_async(runSubprocess, start)   

    def updateProgressBarValue(value: int):
        progressBarValue_setter(lambda old: old + value)

    with ed.Window(title="Image Processor", _size_open='Maximized'):
        with ed.VBoxView(style={"align": "top"}):
            with ed.HBoxView(style={"padding": 10}):
                com.ButtonWidget(label=source_folder, buttonLabel="Source Folder")
                com.ButtonWidget(label=output_folder, buttonLabel="Output Folder")
            with ed.HBoxView(style={"padding": 10}):
                if source_folder != "" and output_folder != "":
                    with ed.VBoxView(style={"align": "top"}):
                        com.ImageComponent(label="Original Image")
                        with ed.HBoxView(style={"align": "center"}):
                            ed.Button("Previous",on_click=lambda _: selectImage(-1))
                            ed.Button("Next", on_click= lambda _: selectImage(1))
                    com.ImageComponent(label="Preview Image")
            with ed.HBoxView(style={"align": "center"}):
                if source_folder != "" and output_folder != "":
                    ed.Button("Apply", on_click= lambda _: on_start_click(), 
                              style={"margin-left": "100px", "margin-right": "200px","height":"80px", "width":"80px"})
                    com.EditorWidget()
            with ed.HBoxView(style={"align": "center", "padding": 50}):
                if showProgressBar:
                    ed.ProgressBar(
                        value=int(math.ceil((progressBarValue/progressBarFactor) *100)),
                        min_value=0,
                        max_value=100,
                        format="",
                        style={"width": "600%"}
                    )

   

if __name__ == "__main__":
    ed.App(Main()).start()