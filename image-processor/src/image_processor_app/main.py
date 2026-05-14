from __future__ import annotations

import asyncio
import cv2
import glob
import os

import edifice as ed
import components as com



@ed.component
def Main(self):
    source_folder, _source_folder_setter = ed.provide_context("source_folder_context_key", "")
    output_folder, _output_folder_setter = ed.provide_context("output_folder_context_key", "")

    current_hue, current_hue_setter = ed.provide_context("hue_context_key", 0)
    current_saturation, current_saturation_setter = ed.provide_context("saturation_context_key", 0)
    current_value, current_value_setter = ed.provide_context("value_context_key", 0)
    current_sharpness, current_sharpness_setter = ed.provide_context("sharpness_context_key", 0)

    selected_image, selected_image_setter = ed.provide_context("selected_image_context_key", "")
    images, images_setter = ed.use_state([])
    image_names, image_names_setter = ed.use_state([])
    
    
    def loadImages():

        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', "*.webp"]
        aux_images = []
        aux_image_names = []

        if source_folder is not None and os.path.isdir(source_folder):
            for extension in extensions:
                image_paths = glob.glob(os.path.join(source_folder, extension))
                for image_path in image_paths:
                    try:
                        img = cv2.imread(image_path)
                        if img is not None:
                            aux_images.append(img)
                            aux_image_names.append(image_path)
                    except Exception as e:
                        print(f"Error loading image {image_path}: {e}")
            images_setter(aux_images)
            image_names_setter(aux_image_names)
            print(len(image_names), "images loaded.")
            selected_image_setter(aux_image_names[0])
        else:
            print("Source folder is not set or does not exist.")

    def selectImage(direction):
    
        currentImageIndex = image_names.index(selected_image) if selected_image in image_names else -1
        print("Current index:", currentImageIndex, "Direction:", direction)
        currentImageIndex += direction
        if 0 <= currentImageIndex < len(image_names):
            print("Selected image:", image_names[currentImageIndex])
            selected_image_setter(image_names[currentImageIndex])


    with ed.Window(title="Image Processor", _size_open=(800, 600)):
        with ed.VBoxView(style={"align": "top"}):
            with ed.HBoxView(style={"padding": 10}):
                com.ButtonWidget(label=source_folder, buttonLabel="Source Folder")
                com.ButtonWidget(label=output_folder, buttonLabel="Output Folder")
            with ed.HBoxView(style={"padding": 10}):
                with ed.VBoxView(style={"align": "top"}):
                    ed.Button("Load Images", on_click=lambda _:loadImages())   
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
                        value=50,
                        min_value=0,
                        max_value=100,
                        format="",
                        style={"width": "600%"}
                    )

   

if __name__ == "__main__":
    ed.App(Main()).start()