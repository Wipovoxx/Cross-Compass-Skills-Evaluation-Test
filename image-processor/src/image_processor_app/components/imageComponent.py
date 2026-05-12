import edifice as ed

@ed.component
def OriginalImageComponent(self):


    with ed.VBoxView(style={"align": "top", "padding": 10}):
        ed.Label("Preview Image")
        ed.Image(src="",
                  style={"max-width": "100%"})
        with ed.HBoxView(style={"padding": 10}):
            ed.Button("Previous")
            ed.Button("Next")

@ed.component
def PreviewImageComponent(self):

    with ed.VBoxView(style={"align": "top", "padding": 10}):
        ed.Label("Preview Image")
        ed.Image(src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/640px-PNG_transparency_demonstration_1.png",
                  style={"max-width": "100%"})