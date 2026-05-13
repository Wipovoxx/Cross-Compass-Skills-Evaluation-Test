import edifice as ed

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
def PreviewImageComponent(self):

    with ed.VBoxView(style={"align": "top", "padding": 10}):
        ed.Label("Preview Image")
        ed.Image(src="C:\\Users\\aleja\\Pictures\\McQueen.png",)

@ed.component
def EditorWidget(self):
    with ed.VBoxView(style={"align": "top", "padding": 20, "border": "1px solid #ccc", "border-radius": "50px"}):
        SliderWidget(label="Hue", min=-100, max=100)
        SliderWidget(label="Saturation", min=-100, max=100)
        SliderWidget(label="Value", min=-100, max=100)
        SliderWidget(label="Sharpness", min=-100, max=100)

@ed.component
def SliderWidget(self, label:str, min:int, max:int):

    current_value, current_value_setter = ed.use_state(0)

    def on_TextInput_change(text):
        try:
            if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
                value = int(text)
                if min <= value <= max:
                    current_value_setter(value)
                else:
                    current_value_setter(0)
            else:
                return
        except ValueError:
            pass # Could not convert string to int

    with ed.HBoxView(style={"align": "right", "padding": 10}):
        ed.Label(label, style={"min-width": "60px"})
        ed.Slider(value=current_value, min_value=min, max_value=max, on_change=current_value_setter)
        ed.TextInput(text=str(current_value), on_change=on_TextInput_change,
                     style={"width": "50px", "margin-right": "10px"})

@ed.component
def ButtonWidget(self, label:str, buttonLabel:str):

    with ed.HBoxView(style={"padding": 10}):
        ed.Button(buttonLabel)
        ed.Label(label)