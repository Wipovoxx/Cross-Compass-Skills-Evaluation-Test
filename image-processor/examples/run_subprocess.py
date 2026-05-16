#
# python examples/run_subprocess.py
#


import time
from collections.abc import Callable
from typing import cast

import edifice as ed
import logging
logger = logging.getLogger("Edifice")
logger.setLevel(logging.INFO)


def my_subprocess(
    callback: Callable[[int, int], None],
) -> None:
    callback(1, 1)
    time.sleep(1)
    callback(2, 2)
    time.sleep(1)
    callback(3, 3)

@ed.component
def Main(self):
    results, set_results = ed.use_state(cast(int, 0))
    start, start_setter = ed.use_state(False)
    execute, set_execute = ed.use_state(False)


    def my_callback(result: int, process_id: int):
        if execute:
            logger.info(f"Received result: {result} from process_id: {process_id}")
            logger.info(f"Current results before update: {results} in process_id: {process_id}")
            set_results(lambda r: r + result) # noqa: RUF005
            set_execute(False)
        else:
            return  

    ed.use_async(lambda:ed.run_subprocess_with_callback(my_subprocess, my_callback), start, 3)

    def on_start_click(event):
        start_setter(not start)
        set_execute(not execute)

    with ed.VBoxView(style={"align": "top"}):
        ed.Button(title="Start Subprocess", on_click=on_start_click)
        ed.Label(text=f"Result: {results}")


if __name__ == "__main__":
    ed.App(ed.Window(title="Async Example", _size_open=(800,600))(Main())).start()