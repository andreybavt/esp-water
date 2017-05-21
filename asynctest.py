import asyncio
from math import sqrt
from time import time


# def lucas():
#     yield 2
#     a = 2
#     b = 1
#     while True:
#         yield b
#         a, b = b, a + b


# async def is_prime(x):
#     if x < 2:
#         return False
#     for i in range(2, sqrt(x) + 1):
#         if x % 2 == 0:
#             return False
#         await asyncio.sleep(0)
#     return True


async def repetitive_message(msg, sec):
    while True:
        print(str(time()) + " : " + msg + " every " + str(sec) + " sec")
        await asyncio.sleep(sec)


async def print_matches(iterable, predicate):
    for item in iterable:
        matches = await predicate(item)
        if matches:
            print("Found :" % str(item))


loop = asyncio.get_event_loop()
# loop.create_task(print_matches(lucas(),is_prime))
loop.create_task(repetitive_message("Hello world", 2))
loop.create_task(repetitive_message("Hello world", 10))
loop.run_forever()
