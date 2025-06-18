import asyncio
import time
from guardin_mind.manager import ConfigRead, limit_concurrency

class HelloWorld:
    def __init__(self):
        # Load configs
        ConfigRead(self)

    @limit_concurrency(2) # Maximum number of simultaneously running instances
    def ask_sync(self, prompt: str) -> str: # Sync function
        '''
        An example of an ask() function that accepts a question and returns "Hello World"
        '''
        print(f"Prompt is: {prompt}")

        time.sleep(2)

        return "Hello World"

    @limit_concurrency(2) # Maximum number of simultaneously running instances
    async def ask_async(self, prompt: str) -> str: # Async function
        '''
        An example of an ask() function that accepts a question and returns "Hello World"
        '''
        print(f"Prompt is: {prompt}")

        await asyncio.sleep(2)

        return "Hello World"
    