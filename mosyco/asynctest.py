# -*- coding: utf-8 -*-
import asyncio

@asyncio.coroutine
async def do_that(l):
    if len(l) == 0:
        yield
    else:
        print(f'doing that... {l[0]}')


def gen():
    for i in range(5):
        print(f'yielding {i}')
        yield i
@asyncio.coroutine
async def do_this(l, i):
    if i == 0:
        print('doing this...')
    yield
    print(f'appending {i}')
    l.append(item)

def task(future, gen, l):
    item = next(gen)
    do_this(l, item)
    future.set_result('DONE!')
    for item in gen:
        do_this(l, item)


l = []

loop = asyncio.get_event_loop()
loop.run_until_complete(do_that(l))

for item in gen():
    loop.run_until_complete(do_this(l, item))
    # do_this(l, item)
