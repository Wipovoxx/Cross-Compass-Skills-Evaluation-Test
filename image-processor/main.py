from edifice import App, Label, Window, Button, component

@component
def HelloWorld(self):
    with Window():
        Label("Hello World!")
        Button("Click me!")

if __name__ == "__main__":
    App(HelloWorld()).start()