from __future__ import annotations

import asyncio

import edifice as ed
import components 

@ed.component
def Main(self):
    with ed.Window(title="Image Processor", _size_open=(800, 600)):
        with ed.VBoxView(style={"align": "top"}):
            with ed.HBoxView(style={"padding": 10}):
                components.ButtonWidget(label="C:\\Path\\To\\Source", buttonLabel="Source Folder")
                components.ButtonWidget(label="C:\\Path\\To\\Output", buttonLabel="Output Folder")
            with ed.HBoxView(style={"padding": 10}):
                components.OriginalImageComponent()
                components.PreviewImageComponent()
            with ed.HBoxView(style={"align": "center"}):
                ed.Button("Apply")
                components.EditorWidget()


if __name__ == "__main__":
    ed.App(Main()).start()