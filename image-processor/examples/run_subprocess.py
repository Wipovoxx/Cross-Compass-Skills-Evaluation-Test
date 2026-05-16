#
# python examples/run_subprocess.py
#


import asyncio
import time
from collections.abc import Callable
from typing import cast
import typing

import edifice as ed
import logging
logger = logging.getLogger("Edifice")
logger.setLevel(logging.INFO)


def my_subprocess(callback: typing.Callable[[int], None]) -> str:
    # This function will run in a new Process.

    async def work() -> str:
        callback(1)
        callback(2)
        callback(3)
        callback(4)
        callback(5)
        callback(6)
        callback(7)
        callback(8)
        await asyncio.sleep(1)
        return "done"

    return asyncio.new_event_loop().run_until_complete(work())

@ed.component
def Main(self):
    results, set_results = ed.use_state(cast(int, 0))
    start, start_setter = ed.use_state(False)
    execute, set_execute = ed.use_state(False)


    def my_callback(result: int, process_id = 0):
        if execute:
            logger.info(f"Received result: {result} from process_id: {process_id}")
            logger.info(f"Current results before update: {results} in process_id: {process_id}")
            set_results(lambda r: r + result) # noqa: RUF005
            set_execute(False)
        else:
            return  

    async def _run_subprocess_and_ignore():
        await ed.run_subprocess_with_callback(my_subprocess, my_callback)

    ed.use_async(lambda: _run_subprocess_and_ignore(), start, 3)

    def on_start_click(event):
        start_setter(not start)
        set_execute(not execute)

    with ed.VBoxView(style={"align": "top"}):
        ed.Button(title="Start Subprocess", on_click=on_start_click)
        ed.Slider(value=0, min_value=0, max_value=10)
        ed.Label(text=f"Result: {results}")


if __name__ == "__main__":
    ed.App(ed.Window(title="Async Example", _size_open=(800,600))(Main())).start()