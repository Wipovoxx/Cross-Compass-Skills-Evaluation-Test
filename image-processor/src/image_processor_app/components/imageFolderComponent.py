import edifice as ed

@ed.component
def ButtonWidget(self, label:str, buttonLabel:str):

    with ed.HBoxView(style={"padding": 10}):
        ed.Button(buttonLabel)
        ed.Label(label)
        