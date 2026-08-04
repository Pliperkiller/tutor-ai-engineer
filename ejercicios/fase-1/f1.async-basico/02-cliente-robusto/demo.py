# DEMO — tutor's minimal example. Run: python demo.py
"""What asyncio.gather does when one task raises an exception."""

import asyncio


async def work(task_id: int) -> str:
    if task_id == 3:
        await asyncio.sleep(0.1)
        raise ValueError(f"task {task_id} exploded")
    await asyncio.sleep(0.3)
    print(f"  task {task_id} finished fine")
    return f"result-{task_id}"


async def gather_default() -> None:
    print("--- 1) gather by default ---")
    try:
        results = await asyncio.gather(*(work(i) for i in range(5)))
        print("results:", results)
    except ValueError as exc:
        print(f"  the await itself RAISED: {exc!r}  -> `results` was never assigned")
    await asyncio.sleep(0.4)  # linger so we can see what the surviving tasks did


async def gather_return_exceptions() -> None:
    print("--- 2) gather(return_exceptions=True) ---")
    results = await asyncio.gather(
        *(work(i) for i in range(5)), return_exceptions=True
    )
    print("results:")
    for item in results:
        print(f"  {item!r}")


asyncio.run(gather_default())
asyncio.run(gather_return_exceptions())
