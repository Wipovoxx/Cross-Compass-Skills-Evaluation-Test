import edifice as ed
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageFile
from PySide6.QtGui import QImage
from PySide6.QtCore import Qt




@ed.component
def ImageComponent(self, label:str):

    selected_image_name, _selected_image_setter = ed.use_context("selected_image_context_key", str)
    preview_image, preview_image_setter = ed.use_context("preview_image_context_key", QImage)

    with ed.VBoxView(style={"align": "top", "padding": 10}):
        ed.Label(label)
        if label.casefold().startswith("original"):
            ed.Image(src=selected_image_name,aspect_ratio_mode=Qt.AspectRatioMode.KeepAspectRatioByExpanding  ,style={"max-width": "900px", "max-height": "650px"})
        elif label.casefold().startswith("preview"):
            ed.Image(src=preview_image, aspect_ratio_mode=Qt.AspectRatioMode.KeepAspectRatioByExpanding , style={"max-width": "900px", "max-height": "650px"})

@ed.component
def EditorWidget(self):
    with ed.VBoxView(style={"align": "top", "border": "1px solid #ccc", "padding" : "5px" ,"border-radius": "50px", "max-width": "800px"}):
        SliderWidget(left_label="Hue", initial_value=0, min=0, max=360)
        SliderWidget(left_label="Saturation",initial_value=100, min=0, max=200)
        SliderWidget(left_label="Value", initial_value=100, min=0, max=200)
        SliderWidget(left_label="Sharpness", initial_value=100, min=0, max=200, right_label="Blur")
        

@ed.component
def SliderWidget(self, left_label:str, initial_value:int, min:int, max:int, right_label:str = ""):

    text_input_style = {"width": "50px","margin-left": "40px", "margin-right": "10px"}
    text_input_right_label_style = { "width": "50px", "margin-right": "10px"}

    slider_value, slider_value_setter = ed.use_state(initial_value)

    current_hue, current_hue_setter = ed.use_context("hue_context_key", int)
    current_saturation, current_saturation_setter = ed.use_context("saturation_context_key", int)
    current_value, current_value_setter = ed.use_context("value_context_key", int)
    current_sharpness, current_sharpness_setter = ed.use_context("sharpness_context_key", int)

    def on_TextInput_change(text):
        try:
            if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
                value = int(text)
                if min <= value <= max:
                    set_value(value)
                else:
                    set_value(initial_value)
            else:
                set_value(initial_value)
                return
        except ValueError:
            pass # Could not convert string to int
    
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
                     style=text_input_right_label_style if right_label else text_input_style)
        

@ed.component
def ButtonWidget(self, label:str, buttonLabel:str):
    source_folder, _source_folder_setter = ed.use_context("source_folder_context_key", str)
    output_folder, _output_folder_setter = ed.use_context("output_folder_context_key", str)

    def select_folder(event):
        
        if buttonLabel.casefold().startswith("source"):
            folder_path = filedialog.askdirectory(title="Select Source Folder")
            if folder_path:
                _source_folder_setter(folder_path)
        elif buttonLabel.casefold().startswith("output"):
            folder_path = filedialog.askdirectory(title="Select Output Folder")
            if folder_path:
                _output_folder_setter(folder_path)

    with ed.HBoxView(style={"padding": 10}):
        ed.Button(buttonLabel, on_click=select_folder)
        ed.Label(source_folder if buttonLabel.casefold().startswith("source") 
                 else output_folder if buttonLabel.casefold().startswith("output") else "")