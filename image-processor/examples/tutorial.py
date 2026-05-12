from edifice import App, Label, TextInput, HBoxView, Window, component, use_state

METERS_TO_FEET = 3.28084

@component
def ConversionWidget(self, from_unit:str, to_unit:str, factor:float):

    current_text, current_text_set = use_state("0.0")

    from_label_style = {"min-width": 170}
    to_label_style = {"margin-left": 60, "min-width": 220}
    input_style = {"padding": 2, "width": 120}

    with HBoxView(style={"padding": 10}):
        Label(f"Measurement in {from_unit}:", style=from_label_style)
        TextInput(current_text, style=input_style, on_change=current_text_set)
        try:
            to_text = f"{float(current_text) * factor :.3f}"
            Label(f"Measurement in {to_unit}: {to_text}", style=to_label_style)
        except ValueError: # Could not convert string to float
            pass # So don't render the Label


@component
def MyApp(self):
    with Window(title="Measurement Conversion"):
        ConversionWidget("meters", "feet", METERS_TO_FEET)
        ConversionWidget("feet", "meters", 1 / METERS_TO_FEET)

if __name__ == "__main__":
    App(MyApp()).start()