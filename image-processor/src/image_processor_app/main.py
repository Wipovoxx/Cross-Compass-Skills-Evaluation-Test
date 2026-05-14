from __future__ import annotations

import asyncio

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

    def testFuction():
        print("Test function called!")

    with ed.Window(title="Image Processor", _size_open=(800, 600)):
        with ed.VBoxView(style={"align": "top"}):
            with ed.HBoxView(style={"padding": 10}):
                com.ButtonWidget(label=source_folder, buttonLabel="Source Folder")
                com.ButtonWidget(label=output_folder, buttonLabel="Output Folder")
            with ed.HBoxView(style={"padding": 10}):
                with ed.VBoxView(style={"align": "top"}):
                    com.ImageComponent(label="Original Image")
                    with ed.HBoxView(style={"align": "center"}):
                        ed.Button("Previous",on_click=lambda _: print("Clicked!"))
                        ed.Button("Next", on_click= lambda _: print("Clicked!"))
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
                    )

   

if __name__ == "__main__":
    ed.App(Main()).start()