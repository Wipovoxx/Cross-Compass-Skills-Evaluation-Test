from __future__ import annotations

import asyncio
from typing import Callable, Generator
import glob
import os
from PIL import Image
from PIL import ImageFilter
import numpy as np
import edifice as ed
from . import components as com
from .constants import (
    IMAGE_EXTENSIONS,
    DEFAUT_HUE, 
    DEFAULT_SATURATION, 
    DEFAULT_SHARPNESS, 
    DEFAULT_VALUE,
    DisplayMode)
import logging
from PySide6.QtGui import QImage
from dataclasses import dataclass
import multiprocessing
from multiprocessing import Queue
import functools
import math
from enum import Enum


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





def scanImages(folder: str) -> Generator[str, None, None]:
    
    if folder and os.path.isdir(folder):
        for extension in IMAGE_EXTENSIONS:
            for path in glob.glob(os.path.join(folder, extension)):
                try:
                    Image.open(path)
                    yield path
                except Exception as e:
                    logger.error(f"scanImages(): Could not open {path}: {e}")


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
            image_name = os.path.basename(image)
            stem, extension = os.path.splitext(image_name)
            image_name = stem + "_edited" + extension
            result = editImage(image, hue, saturation, value, sharpness)
            output_path = os.path.join(output_folder, image_name)
            n = 1
            while os.path.exists(output_path):
                output_path = os.path.join(output_folder, f"{stem}_edited{n}{extension}")
                n += 1
            
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

    current_hue, current_hue_setter = ed.provide_context("hue_context_key", DEFAUT_HUE)
    current_saturation, current_saturation_setter = ed.provide_context("saturation_context_key", DEFAULT_SATURATION)
    current_value, current_value_setter = ed.provide_context("value_context_key", DEFAULT_VALUE)
    current_sharpness, current_sharpness_setter = ed.provide_context("sharpness_context_key", DEFAULT_SHARPNESS)

    selected_image_name, selected_image_name_setter = ed.provide_context("selected_image_context_key", "")
    preview_image, preview_image_setter = ed.provide_context("preview_image_context_key", QImage())
    image_names, image_names_setter = ed.use_state([])
    firstImage = 0
    progressBarValue, progressBarValue_setter = ed.use_state(0)
    progressBarFactor, progressBarFactor_setter = ed.use_state(1)
    displayMode, displayMode_setter = ed.provide_context("displayMode_context_key", DisplayMode.BOTH)
    start, start_setter = ed.use_state(False)
    execute, execute_setter = ed.use_state(False)
    showProgressBar, showProgressBar_setter= ed.use_state(False)
    
    
    async def loadImages():

        aux_image_names = []
        progressBarValue_setter(0)
        
        if source_folder is not None and os.path.isdir(source_folder):
            showProgressBar_setter(True)
            image_count = sum(len(glob.glob(os.path.join(source_folder, ext))) for ext in IMAGE_EXTENSIONS)
            progressBarFactor_setter(lambda _: image_count)
            for image_path in scanImages(source_folder):
                aux_image_names.append(image_path)
                progressBarValue_setter(lambda old: old + 1)
                await asyncio.sleep(0)
                logger.info(f"loadImages(): Image loaded: {image_path}")
            
            image_names_setter(aux_image_names)
            logger.info(f"{len(aux_image_names)} images loaded.")
            selected_image_name_setter(aux_image_names[firstImage])
            showProgressBar_setter(False)
        else:
            logger.warning("loadImages(): Source folder is not set or does not exist.")

    ed.use_async(loadImages, source_folder)

       
    def selectImage(direction):
    
        currentImageIndex = image_names.index(selected_image_name) if selected_image_name in image_names else -1
        logger.info(f"Current index: {currentImageIndex}, Direction: {direction}")
        currentImageIndex += direction

        if len(image_names) < 1:
            logger.info("selectImage(): No images available to select.")
            return

        if 0 <= currentImageIndex < len(image_names):           
            selected_image_name_setter(image_names[currentImageIndex])
            
        elif image_names.index(selected_image_name) == 0 and direction == -1:
            selected_image_name_setter(image_names[len(image_names)-1]) #if we are at the first image and click previous, we select the last image
            
        elif image_names.index(selected_image_name) == len(image_names)-1 and direction == 1:
            selected_image_name_setter(image_names[0]) #if we are at the last image and click next, we select the first image
            

        logger.info(f"selectImage(): Selected image: {selected_image_name}")
        

    async def editPreview():
        if selected_image_name == "":
            logger.warning("editPreview(): No image selected.")
            return
        await asyncio.sleep(0.1)
        try:
            edittedPreview = editImage(selected_image_name, current_hue, current_saturation, current_value, current_sharpness)
        except Exception as e:
            logger.error(f"Error editing preview image: {e}", exc_info=True)
            return
        edittedPreview = edittedPreview.convert("RGBA")
        editedPreview_data = edittedPreview.tobytes('raw', 'RGBA')
        preview_image_setter(QImage(editedPreview_data, edittedPreview.width, edittedPreview.height, QImage.Format.Format_RGBA8888).copy())
        logger.info(f"editPreview(): Preview image edited: {selected_image_name}")

    ed.use_async(editPreview, [selected_image_name, current_hue, current_saturation, current_value, current_sharpness])

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
            
            logger.info("runSubprocess(): All workers finished.")
            logger.info(f"runSubprocess(): processed: {len(image_names)} images")
            showProgressBar_setter(False)
            execute_setter(not execute)
        
    ed.use_async(runSubprocess, start)   

    def updateProgressBarValue(value: int):
        progressBarValue_setter(lambda old: old + value)

    with ed.Window(title="Image Processor", _size_open='Maximized'):
        with ed.VBoxView(style={"align": "top"}):

            with ed.HBoxView(style={"padding": 5, "align": "center"}):
                com.ButtonWidget(label=source_folder, buttonLabel="Source Folder")
                com.ButtonWidget(label=output_folder, buttonLabel="Output Folder")
            if source_folder == "" or output_folder == "":
                com.OnboardingWidget(source=source_folder,output= output_folder)
            if source_folder != "" and output_folder != "" and image_names:
                    com.DisplayModeWidget()
            with ed.HBoxView(style={"padding": 10, "align": "center"}):
                if source_folder != "" and output_folder != "" and image_names:
                    if displayMode == DisplayMode.BOTH or displayMode == DisplayMode.ORIGINAL:   
                        com.ImageComponent(label="Original Image")
                    if displayMode == DisplayMode.BOTH or displayMode == DisplayMode.PREVIEW:
                        com.ImageComponent(label="Preview Image")
                        
            with ed.HBoxView(style={"align": "center", "padding": 5}):
                if source_folder != "" and output_folder != "" and image_names:
                    current_idx = (image_names.index(selected_image_name) + 1) if selected_image_name in image_names else 0
                    ed.Button("◀  Previous Image", on_click=lambda _: selectImage(-1),
                              style={"margin-right": "20px", "padding": "6px 14px"})
                    ed.Label(f"Image {current_idx} of {len(image_names)}",
                             style={"min-width": "120px", "font-weight": "bold"})
                    ed.Button("Next Image  ▶", on_click=lambda _: selectImage(1),
                              style={"margin-left": "20px", "padding": "6px 14px"})                 
            
            with ed.HBoxView(style={"align": "center", "padding": 10}):
                if source_folder != "" and output_folder != "":
                    com.EditorWidget()
                    ed.Button("Apply", on_click= lambda _: on_start_click(), 
                              style={"height": "60px", "width": "180px", "font-weight": "bold",
                                     "background-color": "#4a90e2", "color": "white",
                                     "margin-left": "30px", "border-radius": "8px",
                                     "font-size": "15px"})
                    
            with ed.HBoxView(style={"align": "center", "padding": 50}):
                if showProgressBar:
                    ed.ProgressBar(
                        value=int(math.ceil((progressBarValue/progressBarFactor) *100)),
                        min_value=0,
                        max_value=100,
                        format="",
                        style={"width": "600%"}
                    )

   

def start():
    ed.App(Main()).start()

if __name__ == "__main__":
    start()