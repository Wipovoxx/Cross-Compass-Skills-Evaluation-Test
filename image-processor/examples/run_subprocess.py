#
# python examples/run_subprocess.py
#
from __future__ import annotations

import asyncio
from asyncio import subprocess
import functools
import multiprocessing
from multiprocessing import Queue
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast
import typing

import edifice as ed
import logging
logger = logging.getLogger("Edifice")
logger.setLevel(logging.INFO)

@dataclass
class WorkItem:
    items: list[str]
    value: int



def my_subprocess(msq_queue: Queue[WorkItem] ,callback: typing.Callable[[str, int | None], None]) -> str:
    # This function will run in a new Process.
    firstMessage = msq_queue.get()
    logger.info(f"Received in subprocess: {firstMessage.items} in process_id: {multiprocessing.current_process().pid}, ")
    callback(f"First result: {firstMessage.items[0]} with value {firstMessage.value} ", multiprocessing.current_process().pid)
    time.sleep(10)  # Simulate some work
    secondMessage = msq_queue.get()
    logger.info(f"Received in subprocess: {secondMessage.items} in process_id: {multiprocessing.current_process().pid}")
    callback(f"Second result: {secondMessage.items[0]} with value {secondMessage.value} ", multiprocessing.current_process().pid)
    return "Subprocess completed"

@ed.component
def Main(self):
    results, set_results = ed.use_state("")
    start, start_setter = ed.use_state(False)
    execute, set_execute = ed.use_state(False)
    result_message, set_result_message = ed.use_state("")

    variable_for_subprocess, set_variable_for_subprocess = ed.use_state("This is a variable for the subprocess")

    msg_queue: multiprocessing.Queue[WorkItem] = multiprocessing.get_context("spawn").Queue()
    

    def my_callback(result: str, process_id: int | None = None) -> None:
        if execute:
            logger.info(f"Received result: {result} from process_id: {process_id}")
            logger.info(f"Current results before update: {results} in process_id: {multiprocessing.current_process().pid}")            
            set_results(lambda r: r + result) # noqa: RUF005      
            
            set_execute(False)
        else:
            return  

    async def send_messages():
        msg_queue.put(WorkItem(items=["First message"], value=1))
        msg_queue.put(WorkItem(items=["Second message"], value=2))

    async def run_subprocess():
        if execute:
            set_result_message("Subprocess started...")
            set_results("")  # Clear previous results

            x, _ = await asyncio.gather(
                ed.run_subprocess_with_callback(functools.partial(my_subprocess, msg_queue), my_callback),
                send_messages(),
            )
            set_result_message(x)
            set_execute(False)
        else:
            return

    ed.use_async(lambda: run_subprocess(), start)

    def on_start_click(event):
        start_setter(not start)
        set_execute(not execute)

    with ed.VBoxView(style={"align": "top"}):
        ed.Button(title="Start Subprocess", on_click=on_start_click)
        ed.Slider(value=0, min_value=0, max_value=200)
        ed.Label(text=f"Result: {results}")
        ed.Label(text=result_message)


if __name__ == "__main__":
    ed.App(ed.Window(title="Async Example", _size_open=(800,600))(Main())).start()