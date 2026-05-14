import edifice as ed
import tkinter as tk
from tkinter import filedialog

@ed.component
def OriginalImageComponent(self):


    with ed.VBoxView(style={"align": "top"}):
        ed.Label("Original Image", style={"margin-left": "100px"})
        ed.Image(src="C:\\Users\\aleja\\Pictures\\McQueen.png",
                 style={"margin-left": "100px"} )
        with ed.HBoxView(style={"padding": 10}):
            ed.Button("Previous")
            ed.Button("Next")

@ed.component
def ImageComponent(self, label:str):

    with ed.VBoxView(style={"align": "top", "padding": 10}):
        ed.Label(label)
        ed.Image(src="C:\\Users\\aleja\\Pictures\\McQueen.png",)

@ed.component
def EditorWidget(self):
    with ed.VBoxView(style={"align": "top", "padding": 20, "border": "1px solid #ccc", "border-radius": "50px"}):
        SliderWidget(left_label="Hue", min=-100, max=100)
        SliderWidget(left_label="Saturation", min=-100, max=100)
        SliderWidget(left_label="Value", min=-100, max=100)
        SliderWidget(left_label="Sharpness", min=-100, max=100, right_label="Blur")

@ed.component
def SliderWidget(self, left_label:str, min:int, max:int, right_label:str = ""):

    text_input_style = {"width": "50px","margin-left": "40px", "margin-right": "10px"}
    text_input_right_label_style = { "width": "50px", "margin-right": "10px"}

    current_value, current_value_setter = ed.use_state(0)

    current_hue, current_hue_setter = ed.use_context("hue_context_key", int)
    current_saturation, current_saturation_setter = ed.use_context("saturation_context_key", int)
    current_value, current_value_setter = ed.use_context("value_context_key", int)
    current_sharpness, current_sharpness_setter = ed.use_context("sharpness_context_key", int)

    def on_TextInput_change(text):
        try:
            if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
                value = int(text)
                if min <= value <= max:
                    current_value_setter(value)
                    set_value(value)
                else:
                    current_value_setter(0)
                    set_value(0)
            else:
                current_value_setter(0)
                set_value(0)
                return
        except ValueError:
            pass # Could not convert string to int
    
    def set_value(new_value):
        current_value_setter(new_value)
        match left_label.casefold():
            case "hue": current_hue_setter(new_value)
            case "saturation": current_saturation_setter(new_value)   
            case "value": current_value_setter(new_value)
            case "sharpness": current_sharpness_setter(new_value)

    with ed.HBoxView(style={"align": "right", "padding": 10}):
        ed.Label(left_label, style={"min-width": "60px"})
        ed.Slider(value=current_value, min_value=min, max_value=max, on_change=set_value)
        if right_label:
            ed.Label(right_label, style={"margin-left": "5px", "margin-right": "10px"})
        ed.TextInput(text=str(current_value), on_change=on_TextInput_change,
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