#
# python examples/run_multiplesubprocess.py
#
from __future__ import annotations

import asyncio
import functools
import math
import multiprocessing
import time
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
    chunk_id: int


def my_subprocess(
    msg_queue: multiprocessing.Queue[WorkItem | None],
    callback: typing.Callable[[str, int | None], None],
) -> str:
    """Worker function that runs in a spawned subprocess."""
    while True:
        work_item = msg_queue.get()
        if work_item is None:
            break

        logger.info(
            f"Worker got chunk {work_item.chunk_id} with {len(work_item.items)} items"
        )
        time.sleep(0.5)  # simulate work
        callback(
            f"chunk {work_item.chunk_id}: processed {len(work_item.items)} items\n",
            multiprocessing.current_process().pid,
        )

    return "worker done"


@ed.component
def Main(self):
    results, set_results = ed.use_state("")
    start, set_start = ed.use_state(False)
    result_message, set_result_message = ed.use_state("")

    async def send_chunks(queues: list[multiprocessing.Queue[WorkItem | None]], all_chunks: list[list[str]]):
        for chunk_id, chunk in enumerate(all_chunks):
            queues[chunk_id].put(WorkItem(items=chunk, chunk_id=chunk_id))

        # send a sentinel to each worker so they stop after their assigned work
        for queue in queues:
            queue.put(None)

    async def run_subprocess():
        context = multiprocessing.get_context("spawn")
        num_workers = 3
        big_list = [f"item {i}" for i in range(20)]

        chunk_size = math.ceil(len(big_list) / num_workers)
        chunks = [
            big_list[i * chunk_size : (i + 1) * chunk_size]
            for i in range(num_workers)
        ]

        queues = [context.Queue() for _ in range(num_workers)]

        def my_callback(result: str, process_id: int | None = None) -> None:
            logger.info(f"Received result from process_id {process_id}: {result.strip()}")
            set_results(lambda prev: prev + result)

        workers = [
            ed.run_subprocess_with_callback(
                functools.partial(my_subprocess, queue),
                my_callback,
            )
            for queue in queues
        ]

        results = await asyncio.gather(
            *workers,
            send_chunks(queues, chunks),
        )
        worker_results = results[:-1]

        set_result_message(f"All workers finished: {worker_results}")
        

    ed.use_async(lambda: run_subprocess(), start)

    def on_start_click(event):
        set_results("")
        set_result_message("Starting workers...")
        set_start(not start)

    with ed.VBoxView(style={"align": "top"}):
        ed.Button(title="Start Multiple Subprocesses", on_click=on_start_click)
        ed.Label(text=f"Result: {results}")
        ed.Label(text=result_message)


if __name__ == "__main__":
    ed.App(ed.Window(title="Multiple Subprocess Example", _size_open=(800, 600))(Main())).start()
