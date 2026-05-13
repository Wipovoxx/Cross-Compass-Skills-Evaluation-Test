from __future__ import annotations

import asyncio

import edifice as ed
import components as com



@ed.component
def Main(self):
    source_folder, _source_folder_setter = ed.provide_context("source_folder_context_key", "")
    output_folder, _output_folder_setter = ed.provide_context("output_folder_context_key", "")

    with ed.Window(title="Image Processor", _size_open=(800, 600)):
        with ed.VBoxView(style={"align": "top"}):
            with ed.HBoxView(style={"padding": 10}):
                com.ButtonWidget(label=source_folder, buttonLabel="Source Folder")
                com.ButtonWidget(label=output_folder, buttonLabel="Output Folder")
            with ed.HBoxView(style={"padding": 10}):
                with ed.VBoxView(style={"align": "top"}):
                    com.ImageComponent(label="Original Image")
                    with ed.HBoxView(style={"align": "center"}):
                        ed.Button("Previous")
                        ed.Button("Next")
                com.ImageComponent(label="Preview Image")
            with ed.HBoxView(style={"align": "center"}):
                ed.Button("Apply", style={"margin-left": "100px", "margin-right": "200px"})
                com.EditorWidget()

   

if __name__ == "__main__":
    ed.App(Main()).start()