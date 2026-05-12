from __future__ import annotations

import asyncio

import edifice as ed
from components.imageFolderComponent import ButtonWidget
from components.imageComponent import OriginalImageComponent, PreviewImageComponent   

@ed.component
def Main(self):
    with ed.Window(title="Image Processor"):
        with ed.VBoxView(style={"align": "top"}):
            with ed.HBoxView(style={"padding": 10}):
                ButtonWidget(label="C:\\Path\\To\\Source", buttonLabel="Source Folder")
                ButtonWidget(label="C:\\Path\\To\\Output", buttonLabel="Output Folder")
            with ed.HBoxView(style={"padding": 10}):
                OriginalImageComponent()
                PreviewImageComponent()


if __name__ == "__main__":
    ed.App(Main()).start()