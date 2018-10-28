'''
Created on Oct 28, 2018

@author: erik
'''

import sys
import functools
import asyncio as aio

class Prompt:
    def __init__(self, loop=None):
        self.loop = loop or aio.get_event_loop()
        self.q = aio.Queue(loop=self.loop)
        self.loop.add_reader(sys.stdin, self.got_input)

    def got_input(self):
        aio.ensure_future(self.q.put(sys.stdin.readline()), loop=self.loop)

    async def __call__(self):
        return (await self.q.get()).rstrip('\n')