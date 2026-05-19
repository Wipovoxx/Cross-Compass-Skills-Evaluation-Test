import glob
import os
import edifice as ed
from PySide6.QtWidgets import QFileDialog
from PIL import Image, ImageFile
from PySide6.QtGui import QImage, QIntValidator
from PySide6.QtCore import Qt
import logging
from .constants import (
    IMAGE_EXTENSIONS, 
    SOURCE_EMPTY_WARNING,
    DEFAULT_HUE, 
    DEFAULT_SATURATION, 
    DEFAULT_SHARPNESS, 
    DEFAULT_VALUE,
    DisplayMode)

logger = logging.getLogger("Edifice")
logger.setLevel(logging.INFO)



@ed.component
def DisplayModeWidget(self):

    displayMode, displayMode_setter = ed.use_context("displayMode_context_key", DisplayMode)

    button_style = {
                      "padding": "6px 16px",
                      "margin": "0 4px",
                      "min-width": "130px",
                      "background-color": "#ffffff",
                      "color": "#333",
                      "border": "1px solid #4a90e2",
                      "border-radius": "6px",
                      "font-weight": "normal",
                  }
    selected_button_style = {
                      "padding": "6px 16px",
                      "margin": "0 4px",
                      "min-width": "130px",
                      "background-color": "#4a90e2",
                      "color": "white",
                      "border": "1px solid #4a90e2",
                      "border-radius": "6px",
                      "font-weight": "bold",
                  }


    def setDisplayMode(mode:DisplayMode) :
        displayMode_setter(mode)

    with ed.HBoxView(style={"align": "center", "padding": 5}):
        ed.Label("Display mode:", style={"font-weight": "bold", "margin-right:" : "5px"})
        ed.Button("Side by side", on_click= lambda _: setDisplayMode(DisplayMode.BOTH), style= selected_button_style if displayMode == DisplayMode.BOTH else button_style)
        ed.Button("Original Only", on_click= lambda _: setDisplayMode(DisplayMode.ORIGINAL), style= selected_button_style if displayMode == DisplayMode.ORIGINAL else button_style)
        ed.Button("Preview Only", on_click= lambda _: setDisplayMode(DisplayMode.PREVIEW), style= selected_button_style if displayMode == DisplayMode.PREVIEW else button_style)

@ed.component
def OnboardingWidget(self, source:str, output:str):

    src_check = "✓" if source != "" else "1."
    out_check = "✓" if output != "" else "2."

    with ed.VBoxView(style={"align": "center", "padding": 80}):
                    ed.Label("Welcome to Image Processor",
                             style={"font-size": "28px", "font-weight": "bold", "margin-bottom": "10px"})
                    ed.Label("Apply HSV and blur/sharpen effects to a batch of images.",
                             style={"font-size": "14px", "margin-bottom": "40px"})
                    ed.Label("Get started:",
                             style={"font-size": "16px", "font-weight": "bold", "margin-bottom": "15px"})
                    
                    ed.Label(f"{src_check} Select a Source Folder containing your images",
                             style={"font-size": "14px", "margin-bottom": "8px"})
                    ed.Label(f"{out_check} Select an Output Folder for the processed images",
                             style={"font-size": "14px", "margin-bottom": "8px"})
                    ed.Label("3. Use Previous/Next Image to browse, then adjust the effect sliders",
                             style={"font-size": "14px", "margin-bottom": "8px", "color": "#888"})
                    ed.Label("4. Click Apply to process all images in the source folder",
                             style={"font-size": "14px", "color": "#888"})


@ed.component
def ImageComponent(self, label:str):

    selected_image_name, _selected_image_setter = ed.use_context("selected_image_context_key", str)
    preview_image, preview_image_setter = ed.use_context("preview_image_context_key", QImage)
    displayMode, displayMode_setter = ed.use_context("displayMode_context_key", DisplayMode)

    both_style = {"min-width": "500px", "max-width": "500px", "min-height": "400px", "max-height": "400px"}
    large_style = {"min-width": "702px", "max-width": "702px", "min-height": "504px", "max-height": "504px"}

    with ed.VBoxView(style={"align": "top", "padding": 10}):
        ed.Label(label)
        if label.casefold().startswith("original"):
            ed.Image(src=selected_image_name,aspect_ratio_mode=Qt.AspectRatioMode.KeepAspectRatio,
                     style=large_style if displayMode == DisplayMode.ORIGINAL else both_style  )
        elif label.casefold().startswith("preview"):
            ed.Image(src=preview_image, aspect_ratio_mode=Qt.AspectRatioMode.KeepAspectRatio,
                      style=large_style if displayMode == DisplayMode.PREVIEW else both_style)

@ed.component
def EditorWidget(self):

    reset_counter, reset_counter_setter = ed.use_state(0)

    with ed.VBoxView(style={"align": "top", "border": "1px solid #ccc", "padding" : "5px" ,"border-radius": "50px", "max-width": "800px"}):
        ed.Label("Image Effects", style={"font-weight": "bold", "margin-left": "20px", "margin-top": "5px"})
        SliderWidget(left_label="Hue", initial_value=DEFAULT_HUE, min=0, max=360, reset=reset_counter)
        SliderWidget(left_label="Saturation",initial_value=DEFAULT_SATURATION, min=0, max=200, reset=reset_counter)
        SliderWidget(left_label="Value", initial_value=DEFAULT_VALUE, min=0, max=200, reset=reset_counter)
        SliderWidget(left_label="Sharpness", initial_value=DEFAULT_SHARPNESS, min=0, max=200, right_label="Blur", reset=reset_counter)
        with ed.HBoxView(style={"align": "left", "padding-top": "5px", "padding-bottom": "10px", "padding-left": "20px", "padding-right": "20px"}):
            ed.Button("Reset", on_click=lambda _: reset_counter_setter(lambda c: c + 1))
        

@ed.component
def SliderWidget(self, left_label:str, initial_value:int, min:int, max:int, right_label:str = "", reset:int = 0):

    text_input_style = {"width": "50px","margin-left": "40px", "margin-right": "10px"}
    text_input_right_label_style = { "width": "50px", "margin-right": "10px"}

    slider_value, slider_value_setter = ed.use_state(initial_value)
    ref_input = ed.use_ref()

    current_hue, current_hue_setter = ed.use_context("hue_context_key", int)
    current_saturation, current_saturation_setter = ed.use_context("saturation_context_key", int)
    current_value, current_value_setter = ed.use_context("value_context_key", int)
    current_sharpness, current_sharpness_setter = ed.use_context("sharpness_context_key", int)

    def setup_validator():
        ti = ref_input()
        if ti is None or ti.underlying is None:
            return
        ti.underlying.setValidator(QIntValidator(min, max, ti.underlying))

    ed.use_effect(setup_validator, (min, max))

    def resetSlider():
        if reset > 0:
            set_value(initial_value)

    ed.use_effect(resetSlider, reset)

    def on_TextInput_change(text):
        if text == "":
            return  
        try:
            value = int(text)
        except ValueError:
            set_value(slider_value)  
            return
        if value > max:
            value = max
        set_value(value)
    
    def set_value(new_value):
        slider_value_setter(new_value)
        match left_label.casefold():
            case "hue": current_hue_setter(new_value)
            case "saturation": current_saturation_setter(new_value)   
            case "value": current_value_setter(new_value)
            case "sharpness": current_sharpness_setter(new_value)

    with ed.HBoxView(style={"align": "right", "padding": 10}):
        ed.Label(left_label, style={"min-width": "60px"})
        ed.Slider(value=slider_value, min_value=min, max_value=max, on_change=set_value)
        if right_label:
            ed.Label(right_label, style={"margin-left": "5px", "margin-right": "10px"})
        ed.TextInput(text=str(slider_value), on_change=on_TextInput_change,
                     style=text_input_right_label_style if right_label else text_input_style).register_ref(ref_input)
        

@ed.component
def ButtonWidget(self, label:str, buttonLabel:str):
    source_folder, source_folder_setter = ed.use_context("source_folder_context_key", str)
    output_folder, output_folder_setter = ed.use_context("output_folder_context_key", str)
    warning, warning_setter = ed.use_state("")

    def select_folder(event):
        if buttonLabel.casefold().startswith("source"):
            folder_path = QFileDialog.getExistingDirectory(None, "Select Source Folder")
            if folder_path:
                has_images = any(glob.glob(os.path.join(folder_path, ext)) for ext in IMAGE_EXTENSIONS)
                if not has_images:
                    logger.info("select_folder(): setting empty source folder warning")
                    warning_setter(SOURCE_EMPTY_WARNING)
                    source_folder_setter("")
                    return
                warning_setter("")
                source_folder_setter(folder_path)
        elif buttonLabel.casefold().startswith("output"):
            folder_path = QFileDialog.getExistingDirectory(None, "Select Output Folder")
            if folder_path:
                warning_setter("")
                output_folder_setter(folder_path)

    with ed.HBoxView(style={"padding": 10}):
        ed.Button(buttonLabel, on_click=select_folder)
        if warning:
            ed.Label(warning, style={"color": "red"})
        else:
            ed.Label(source_folder if buttonLabel.casefold().startswith("source")
                     else output_folder if buttonLabel.casefold().startswith("output") else "")
        