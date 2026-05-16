#
# python examples/run_subprocess.py
#


import time
from collections.abc import Callable
from typing import cast

import edifice as ed


def my_subprocess(
    callback: Callable[[int], None],
) -> None:
    callback(1)
    #time.sleep(1)
    callback(2)
    #time.sleep(1)
    callback(3)

@ed.component
def Main(self):
    results, set_results = ed.use_state(cast(int, 0))
    start, start_setter = ed.use_state(False)
    execute, set_execute = ed.use_state(False)


    def my_callback(result: int):
        if execute:
            set_results(lambda r: r + result) # noqa: RUF005
            set_execute(False)
        else:
            return  

    ed.use_async(lambda:ed.run_subprocess_with_callback(my_subprocess, my_callback), start)

    def on_start_click(event):
        start_setter(not start)
        set_execute(not execute)

    with ed.VBoxView(style={"align": "top"}):
        ed.Button(title="Start Subprocess", on_click=on_start_click)
        ed.Label(text=f"Result: {results}")


if __name__ == "__main__":
    ed.App(ed.Window(title="Async Example", _size_open=(800,600))(Main())).start()